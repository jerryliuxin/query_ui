#!/usr/bin/env python3
"""Query UI - Saturday Version (Port 8897)"""
import json
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="聚源通汇投研知识库 - 周六版", version="1.0")

# 配置
WORKSPACE = Path("/home/mickey/.openclaw/mihua")
DD_DIR = WORKSPACE / "knowledge_base_dd"
INDEX_FILE = DD_DIR / "index.json"
FRONTEND_DIST = Path(__file__).parent / "frontend_sat" / "dist"

_index_cache = None
def get_index():
    global _index_cache
    if _index_cache is None and INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            _index_cache = json.load(f)
    return _index_cache or {}

@app.get("/api/companies")
async def api_companies(industry: str = None, page: int = 1, page_size: int = 20):
    index = get_index()
    companies = index.get("companies", [])
    if industry:
        companies = [c for c in companies if c.get("industry") == industry]
    enriched = []
    for comp in companies:
        profile_path = DD_DIR / "companies" / comp["id"] / "profile.json"
        if profile_path.exists():
            try:
                data = json.loads(profile_path.read_text(encoding='utf-8'))
                enriched.append(data)
            except:
                enriched.append(comp)
        else:
            enriched.append(comp)
    total = len(enriched)
    start = (page - 1) * page_size
    return {"success": True, "data": enriched[start:start+page_size], "total": total, "page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size}

@app.get("/api/company/{company_id}")
async def api_company_detail(company_id: str):
    index = get_index()
    company = next((c for c in index.get("companies", []) if c.get("id") == company_id), None)
    if not company:
        raise HTTPException(status_code=404, detail="公司未找到")
    profile_path = DD_DIR / "companies" / company_id / "profile.json"
    if not profile_path.exists():
        raise HTTPException(status_code=404, detail="公司档案不存在")
    data = json.loads(profile_path.read_text(encoding='utf-8'))
    return {"success": True, "data": data}

@app.get("/api/investors")
async def api_investors(page: int = 1, page_size: int = 20):
    index = get_index()
    investors = index.get("investors", [])
    total = len(investors)
    start = (page - 1) * page_size
    return {"success": True, "data": investors[start:start+page_size], "total": total, "page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size}

@app.get("/api/investments")
async def api_investments(page: int = 1, page_size: int = 20):
    index = get_index()
    investments = sorted(index.get("investments", []), key=lambda x: x.get("date", ""), reverse=True)
    total = len(investments)
    start = (page - 1) * page_size
    return {"success": True, "data": investments[start:start+page_size], "total": total, "page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size}

@app.get("/api/search")
async def api_search(q: str, limit: int = 10):
    if not q or not q.strip():
        return {"success": True, "data": {"companies": [], "investors": [], "investments": []}}
    index = get_index()
    q_lower = q.lower()
    results = {
        "companies": [c for c in index.get("companies", []) if q_lower in c.get("name", "").lower() or q_lower in c.get("id", "").lower()],
        "investors": [i for i in index.get("investors", []) if q_lower in i.get("name", "").lower()],
        "investments": [inv for inv in index.get("investments", []) if q_lower in inv.get("company", "").lower() or q_lower in inv.get("investor", "").lower()]
    }
    for key in results:
        results[key] = results[key][:limit]
    results["total"] = sum(len(v) for v in results.values())
    return {"success": True, "data": results, "query": q}

@app.get("/api/stats/dashboard")
async def api_dashboard():
    index = get_index()
    companies = index.get("companies", [])
    investors = index.get("investors", [])
    investments = index.get("investments", [])
    industry_counts = {}
    for comp in companies:
        industry = comp.get("industry", "未知")
        industry_counts[industry] = industry_counts.get(industry, 0) + 1
    return {"success": True, "data": {"total_companies": len(companies), "total_investors": len(investors), "total_investments": len(investments), "industry_distribution": industry_counts, "metadata": index.get("metadata", {})}}

@app.get("/health")
async def health():
    return {"status": "ok", "companies": len(get_index().get("companies", [])), "frontend": "react"}

# 静态文件
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), check_dir=False, html=True), name="static")
    print(f"✅ 挂载 frontend_sat: {FRONTEND_DIST}")
else:
    print(f"⚠️  frontend_sat dist 不存在: {FRONTEND_DIST}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8898)
