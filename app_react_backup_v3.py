#!/usr/bin/env python3
"""
React Frontend Service (Port 8899) - V2: mount entire dist
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
    allc = get_index().get("companies", [])
    start = (page-1)*page_size
    return {"success": True, "data": {"data": allc[start:start+page_size], "total": len(allc), "page": page, "total_pages": (len(allc)+page_size-1)//page_size}}

@app.get("/api/company/{company_id}")
async def api_company_detail(company_id: str):
    p = DD_DIR / "companies" / company_id / "profile.json"
    if not p.exists():
        raise HTTPException(status_code=404)
    with open(p, 'r', encoding='utf-8') as f:
        return {"success": True, "data": json.load(f)}

@app.get("/api/investors")
async def api_investors():
    invs = get_index().get("investors", [])
    return {"success": True, "data": {"data": invs, "total": len(invs)}}

@app.get("/api/investor/{investor_id}")
async def api_investor_detail(investor_id: str):
    for inv in get_index().get("investors", []):
        if inv.get("id") == investor_id:
            return {"success": True, "data": inv}
    raise HTTPException(status_code=404)

@app.get("/api/investments")
async def api_investments():
    invs = get_index().get("investments", [])
    return {"success": True, "data": {"data": invs, "total": len(invs)}}

@app.get("/api/stats")
async def api_stats():
    idx = get_index()
    return {"success": True, "data": {"total_companies": len(idx.get("companies", [])), "total_investors": len(idx.get("investors", [])), "total_investments": len(idx.get("investments", [])), "last_updated": idx.get("metadata", {}).get("generated_at")}}

@app.get("/api/stats/dashboard")
async def api_stats_dashboard():
    idx = get_index()
    companies = idx.get("companies", [])
    investments = idx.get("investments", [])
    
    # 行业分布
    industry_dist = {}
    for c in companies:
        ind = c.get("industry", "未分类")
        industry_dist[ind] = industry_dist.get(ind, 0) + 1
    
    # 近30天交易
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    recent_count = 0
    for inv in investments:
        d = inv.get("date", "")
        if d:
            try:
                if datetime.strptime(d, "%Y-%m-%d") >= thirty_days_ago:
                    recent_count += 1
            except:
                pass
    
    return {"success": True, "data": {"total_companies": len(companies), "total_investors": len(idx.get("investors", [])), "total_investments": len(investments), "recent_investments_count": recent_count, "industry_distribution": industry_dist, "last_updated": idx.get("metadata", {}).get("generated_at")}}

# ============ 静态文件服务 ============

if FRONTEND_DIST.exists():
    # 挂载整个 dist 目录（所有文件）
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIST)), name="static")
    
    @app.get("/favicon.svg")
    async def favicon():
        return FileResponse(str(FRONTEND_DIST / "favicon.svg"))
    
    @app.get("/")
    async def root():
        return FileResponse(str(FRONTEND_DIST / "index.html"))
    
    @app.get("/{path:path}")
    async def fallback(path: str):
        if path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        # 尝试从 static 目录提供文件
        file_path = FRONTEND_DIST / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # 否则返回 index.html (SPA)
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/")
    async def not_built():
        return JSONResponse(status_code=503, content={"error": "Frontend not built"})
