#!/usr/bin/env python3
"""Query UI - Production Mode (FastAPI + React SPA)"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="聚源通汇投研知识库", version="2.0")

# ==================== CORS ====================
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.100.45:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 路径配置 ====================
WORKSPACE = Path("/home/mickey/.openclaw/mihua")
DD_DIR = WORKSPACE / "knowledge_base_dd"
INDEX_FILE = DD_DIR / "index.json"
FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"

_index_cache = None
def get_index():
    global _index_cache
    if _index_cache is None and INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            _index_cache = json.load(f)
    return _index_cache or {}

def extract_funding(data):
    timeline = data.get("financing_timeline", [])
    if timeline:
        latest = timeline[-1]
        return {
            "last_round": latest.get("round", ""),
            "last_amount_cny": latest.get("amount_cny"),
            "last_amount_usd": latest.get("amount_usd"),
            "last_funding": {
                "valuation_cny": latest.get("valuation_cny", 0),
                "valuation_usd": latest.get("valuation_usd", 0),
                "date": latest.get("date", "")
            } if latest.get("valuation_cny") or latest.get("valuation_usd") else {}
        }
    vi = data.get("valuation_indicators", {})
    if vi:
        return {
            "last_round": data.get("funding", {}).get("last_round", ""),
            "last_amount_cny": data.get("funding", {}).get("last_amount_cny"),
            "last_amount_usd": data.get("funding", {}).get("last_amount_usd"),
            "valuation_cny": vi.get("current_valuation_cny", 0),
            "last_funding": {
                "valuation_cny": vi.get("current_valuation_cny", 0),
                "valuation_usd": vi.get("current_valuation_usd", 0)
            }
        }
    return {}

def adapt_company_profile(data: dict, company_meta: dict) -> dict:
    """
    适配公司档案数据，确保前端需要的字段都在 'profile' 嵌套对象中。
    前端 CompanyDetail 组件使用 profile.xxx 访问所有字段。
    """
    # 先复制原始数据
    adapted = data.copy()
    company = company_meta or {}
    financials = data.get("financials", {})

    # 🔧 提取 revenue（兼容多种字段名）
    revenue = financials.get("revenue")
    if revenue is None:
        for year in ["revenue_2025", "revenue_2024", "revenue_2026E", "revenue_2023"]:
            rev = financials.get(year, {})
            if isinstance(rev, dict) and "value_cny" in rev:
                revenue = rev["value_cny"]
                break

    # 🔧 提取估值
    valuation = data.get("valuation") or data.get("valuation_indicators", {}).get("current_valuation_cny")

    # 🔧 提取投资评级
    inv_rec = data.get("investment_recommendation") or data.get("investment_thesis", {})
    if inv_rec:
        rating = inv_rec.get("rating") or inv_rec.get("investment_rating") or inv_rec.get("core_argument", "")
        investment_rating = rating if isinstance(rating, str) and rating else (
            "Buy" if "BUY" in str(inv_rec).upper() else
            "Pass" if "PASS" in str(inv_rec).upper() else
            "Hold"
        )
    else:
        investment_rating = "Hold"

    # 🏗️ 确保 profile 对象存在并补充字段
    profile = adapted.get("profile", {}).copy()

    # 将需要的前端字段补充到 profile 中
    profile_updates = {
        "current_valuation_cny": valuation,
        "investment_rating": investment_rating,
        "revenue": revenue,  # 方便显示
    }

    # 从顶层或原始数据中补充其他字段
    for field in ["sub_industry", "key_products", "team", "financing_timeline", "description"]:
        if field in adapted and field not in profile:
            profile_updates[field] = adapted[field]
        elif field not in profile:
            # 默认值
            if field in ["key_products", "team", "financing_timeline"]:
                profile_updates[field] = []
            else:
                profile_updates[field] = None

    profile.update(profile_updates)
    adapted["profile"] = profile

    # 🏗️ 将某些字段同时保留在顶层（兼容旧代码）
    adapted["financials"] = {"revenue": revenue} if revenue is not None else {}
    adapted["valuation"] = valuation
    adapted["technology"] = data.get("technology") or {}
    adapted["investment_thesis"] = adapted.get("investment_thesis") or "暂无投资建议"

    # 🛠️ 修复 team 字段：确保是数组
    team_data = adapted.get("team")
    if isinstance(team_data, dict):
        team_list = []
        for key, value in team_data.items():
            if isinstance(value, dict):
                team_list.append({"name": key, **value})
            elif isinstance(value, str):
                team_list.append({"name": key, "title": value})
        adapted["team"] = team_list
        profile["team"] = team_list  # 同步更新 profile
    elif not isinstance(team_data, list):
        adapted["team"] = []
        profile["team"] = []

    # 🛠️ 修复 financing_timeline：确保是列表
    fin_timeline = adapted.get("financing_timeline")
    if not isinstance(fin_timeline, list):
        adapted["financing_timeline"] = []
        profile["financing_timeline"] = []

    # 🏗️ 确保必需的顶层字段存在
    for field in ["id", "name", "english_name", "analysis_date", "analyst"]:
        if field not in adapted:
            adapted[field] = company.get(field, "")

    # 🔄 保持 industry 在顶层和 profile 中一致
    if "industry" not in adapted and "industry" in company:
        adapted["industry"] = company["industry"]
    if "industry" not in profile and "industry" in adapted:
        profile["industry"] = adapted["industry"]

    return adapted

# ==================== 挂载 React 静态文件 ====================
if FRONTEND_DIST.exists():
    # 挂载 assets 目录到 /assets，匹配前端请求路径
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")
    # 单独挂载 favicon
    @app.get("/favicon.svg")
    async def favicon():
        return FileResponse(FRONTEND_DIST / "favicon.svg")
    print(f"✅ 挂载 React 静态文件: {FRONTEND_DIST}")
else:
    print(f"⚠️  React dist 不存在: {FRONTEND_DIST}")

# ==================== JSON API ====================

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
                adapted = adapt_company_profile(data, comp)
                enriched.append(adapted)
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
    adapted = adapt_company_profile(data, company)
    peers = [c for c in index.get("companies", []) if c.get("industry") == company.get("industry") and c.get("id") != company_id]
    adapted["peers"] = peers[:5]
    return {"success": True, "data": adapted}

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
    recent_date = datetime.now() - timedelta(days=30)
    recent_inv = []
    for inv in investments:
        date_str = inv.get("date", "")
        try:
            if date_str:
                inv_date = datetime.strptime(date_str, "%Y-%m-%d")
                if inv_date >= recent_date:
                    recent_inv.append(inv)
        except (ValueError, TypeError):
            continue
    return {"success": True, "data": {"total_companies": len(companies), "total_investors": len(investors), "total_investments": len(investments), "recent_investments_count": len(recent_inv), "industry_distribution": industry_counts, "metadata": index.get("metadata", {})}}

@app.get("/health")
async def health():
    return {"status": "ok", "companies": len(get_index().get("companies", [])), "frontend": "react"}

# ==================== Debug (仅开发用) ====================
@app.get("/debug")
async def debug():
    """诊断页面：测试 API 连接"""
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head><title>Debug</title></head>
<body>
  <h1>Query UI Debug</h1>
  <pre id="result">Testing API...</pre>
  <script>
    async function test() {
      const r = document.getElementById('result');
      try {
        const res = await fetch('/api/companies?page_size=1');
        const data = await res.json();
        r.textContent = 'API OK: ' + JSON.stringify(data, null, 2).substring(0, 1000);
      } catch (e) {
        r.textContent = 'Error: ' + e;
        r.style.color = 'red';
      }
    }
    test();
  </script>
</body>
</html>
    """)

# ==================== SPA Fallback (服务 index.html) ====================
@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    """所有非 API 路径都返回 index.html (SPA路由)"""
    # 如果是 API 路径，上面的路由已处理
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    else:
        return HTMLResponse(content="<h1>Frontend not built</h1><p>Run npm run build first.</p>", status_code=503)
