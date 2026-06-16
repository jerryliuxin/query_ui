#!/usr/bin/env python3
"""
React Frontend Service (Port 8899) - Fixed API format
独立部署 React SPA，保留 API 接口，适配前端期望格式
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="投研知识库 React", version="1.0")

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

# ============ API 路由（适配前端）============

@app.get("/api/companies")
async def api_companies(page: int = 1, page_size: int = 100):
    index = get_index()
    allc = index.get("companies", [])
    start = (page-1)*page_size
    end = start + page_size
    return {
        "success": True,
        "data": {
            "data": allc[start:end],
            "total": len(allc),
            "page": page,
            "total_pages": (len(allc) + page_size - 1) // page_size
        }
    }

@app.get("/api/company/{company_id}")
async def api_company_detail(company_id: str):
    profile_path = DD_DIR / "companies" / company_id / "profile.json"
    if not profile_path.exists():
        raise HTTPException(status_code=404, detail="Company not found")
    with open(profile_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {"success": True, "data": data}

@app.get("/api/investors")
async def api_investors():
    index = get_index()
    invs = index.get("investors", [])
    return {
        "success": True,
        "data": {
            "data": invs,
            "total": len(invs)
        }
    }

@app.get("/api/investor/{investor_id}")
async def api_investor_detail(investor_id: str):
    for inv in get_index().get("investors", []):
        if inv.get("id") == investor_id:
            return {"success": True, "data": inv}
    raise HTTPException(status_code=404, detail="Not found")

@app.get("/api/investments")
async def api_investments():
    index = get_index()
    invs = index.get("investments", [])
    return {
        "success": True,
        "data": {
            "data": invs,
            "total": len(invs)
        }
    }

@app.get("/api/stats")
async def api_stats():
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
async def api_stats_dashboard():
    index = get_index()
    companies = index.get("companies", [])
    investments = index.get("investments", [])
    
    # 行业分布
    industry_dist = {}
    for c in companies:
        industry = c.get("industry", "未分类")
        industry_dist[industry] = industry_dist.get(industry, 0) + 1
    
    # 近30天交易数
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

# ============ 静态文件服务 ============

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")
    
    @app.get("/{filename}.svg")
    async def serve_svg(filename: str):
        file_path = FRONTEND_DIST / f"{filename}.svg"
        if file_path.exists():
            return FileResponse(str(file_path))
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    
    @app.get("/favicon.svg")
    async def serve_favicon():
        return FileResponse(str(FRONTEND_DIST / "favicon.svg"))
    
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
    async def not_built():
        return JSONResponse(status_code=503, content={"error": "Not built"})
