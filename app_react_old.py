#!/usr/bin/env python3
"""
React Frontend Service (Port 8899)
独立部署 React SPA，保留 API 接口
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="投研知识库 React", version="1.0")

# CORS（可选，如果跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORKSPACE = Path("/home/mickey/.openclaw/mihua")
DD_DIR = WORKSPACE / "knowledge_base_dd"
INDEX_FILE = DD_DIR / "index.json"
FRONTEND_DIST = WORKSPACE / "tools/query_ui/frontend_original/dist"

@app.get("/health")
async def health():
    return {"status": "OK"}

_index_cache = None
def get_index():
    global _index_cache
    if _index_cache is None and INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                _index_cache = json.load(f)
        except:
            _index_cache = {}
    return _index_cache or {}

# ============ API 路由 ============

@app.get("/api/companies")
async def api_companies(page: int = 1, page_size: int = 100):
    """公司列表（分页）- 适配前端格式"""
    index = get_index()
    all_companies = index.get("companies", [])
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "success": True,
        "data": {
            "data": all_companies[start:end],
            "total": len(all_companies),
            "page": page,
            "total_pages": (len(all_companies) + page_size - 1) // page_size
        }
    }

@app.get("/api/company/{company_id}")
async def api_company_detail(company_id: str):
    """公司详情 - 适配前端格式"""
    profile_path = DD_DIR / "companies" / company_id / "profile.json"
    if not profile_path.exists():
        raise HTTPException(status_code=404, detail="Company not found")
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid company data")
    return {"success": True, "data": data}

@app.get("/api/investors")
async def api_investors():
    """投资机构列表 - 适配前端格式"""
    index = get_index()
    return {
        "success": True,
        "data": {
            "data": index.get("investors", []),
            "total": len(index.get("investors", []))
        }
    }

@app.get("/api/investor/{investor_id}")
async def api_investor_detail(investor_id: str):
    """机构详情 - 适配前端格式"""
    investors = get_index().get("investors", [])
    for inv in investors:
        if inv.get("id") == investor_id:
            return {"success": True, "data": inv}
    raise HTTPException(status_code=404, detail="Investor not found")

@app.get("/api/investments")
async def api_investments():
    """投资交易列表 - 适配前端格式"""
    index = get_index()
    return {
        "success": True,
        "data": {
            "data": index.get("investments", []),
            "total": len(index.get("investments", []))
        }
    }

@app.get("/api/stats")
async def api_stats():
    """统计信息 - 适配前端格式"""
    index = get_index()
    return {
        "success": True,
        "data": {
            "total_companies": len(index.get("companies", [])),
            "total_investors": len(index.get("investors", [])),
            "total_investments": len(index.get("investments", [])),
            "last_updated": index.get("metadata", {}).get("generated_at")
        }
    }

@app.get("/api/stats/dashboard")
async def api_dashboard_stats():
    """仪表盘富化统计数据 - 完全匹配前端 DashboardStats 接口"""
    index = get_index()
    companies = index.get("companies", [])
    investments = index.get("investments", [])
    
    # 行业分布
    industry_dist = {}
    for c in companies:
        industry = c.get("industry", "未分类")
        industry_dist[industry] = industry_dist.get(industry, 0) + 1
    
    # 近30天交易数
    from datetime import datetime, timedelta
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    recent_count = 0
    for inv in investments:
        inv_date = inv.get("date", "")
        if inv_date:
            try:
                inv_dt = datetime.strptime(inv_date, "%Y-%m-%d")
                if inv_dt >= thirty_days_ago:
                    recent_count += 1
            except:
                pass
    
    return {
        "success": True,
        "data": {
            "total_companies": len(companies),
            "total_investors": len(index.get("investors", [])),
            "total_investments": len(investments),
            "recent_investments_count": recent_count,
            "industry_distribution": industry_dist,
            "last_updated": index.get("metadata", {}).get("generated_at")
        }
    }

# ============ 静态文件服务（React SPA） ============

if FRONTEND_DIST.exists():
    # 1. 挂载 assets 目录（Vite 构建输出）
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")
    
    # 2. 根目录文件（如 icons.svg, favicon.svg）也挂载到根路径
    @app.get("/{filename}.svg")
    async def serve_svg(filename: str):
        file_path = FRONTEND_DIST / f"{filename}.svg"
        if file_path.exists():
            return FileResponse(str(file_path))
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    
    @app.get("/favicon.svg")
    async def serve_favicon():
        return FileResponse(str(FRONTEND_DIST / "favicon.svg"))
    
    # 3. SPA fallback: 所有非 API 路由返回 index.html
    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return JSONResponse(status_code=503, content={"error": "Frontend not built"})
else:
    @app.get("/")
    async def frontend_not_built():
        return JSONResponse(
            status_code=503,
            content={"error": "React frontend not built", "message": "请执行: cd tools/query_ui/frontend_original && npm run build"}
        )
