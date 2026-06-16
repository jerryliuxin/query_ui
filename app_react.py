#!/usr/bin/env python3
"""
React Frontend Service (Port 8899) - Fixed v3: all APIs with success wrapper
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

WORKSPACE = Path("/home/mickey/.openclaw/mihua")
DD_DIR = WORKSPACE / "knowledge_base_dd"
INDEX_FILE = DD_DIR / "index.json"
FRONTEND_DIST = WORKSPACE / "tools/query_ui/frontend_original/dist"

def get_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@app.get("/health")
async def health():
    return {"status": "OK"}

# ============ API 路由（全部返回 {success, data}）============

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
        data = json.load(f)

    profile = data.get("profile", {}).copy()

    # ========== 1. 估值与评级 ==========
    valuation = (
        data.get("current_valuation_cny") or
        data.get("valuation") or
        data.get("valuation_indicators", {}).get("current_valuation_cny") or
        data.get("investment_committee_decision", {}).get("target_valuation_cny")
    )
    profile["current_valuation_cny"] = valuation

    inv_rec = data.get("investment_recommendation") or data.get("investment_thesis", {})
    if inv_rec:
        rating = inv_rec.get("rating") or inv_rec.get("investment_rating") or inv_rec.get("core_argument", "")
        if isinstance(rating, str) and rating:
            profile["investment_rating"] = rating
        else:
            profile["investment_rating"] = "Buy" if "BUY" in str(inv_rec).upper() else "Pass" if "PASS" in str(inv_rec).upper() else "Hold"
    else:
        rating = data.get("investment_rating")
        profile["investment_rating"] = rating if isinstance(rating, str) and rating else "Hold"

    # ========== 2. 发展阶段 ==========
    if not profile.get("stage"):
        stage = data.get("funding_stage")
        if not stage:
            fh = data.get("funding_history") or data.get("financing_timeline")
            if isinstance(fh, list) and fh:
                stage = fh[0].get("round") or fh[0].get("stage")
        if not stage:
            stage = data.get("company_type")
        profile["stage"] = stage or "未融资"

    # ========== 3. 产品与融资 ==========
    if not profile.get("key_products"):
        kp = (
            data.get("products_technology", {}).get("key_products") or
            data.get("product_portfolio") or
            data.get("technology", {}).get("core_products") or
            data.get("specific_clients")
        )
        if isinstance(kp, list):
            profile["key_products"] = kp
        elif isinstance(kp, str):
            profile["key_products"] = [kp]
        else:
            profile["key_products"] = []

    if not profile.get("financing_timeline"):
        timeline = data.get("funding_history") or data.get("financing_timeline") or []
        normalized = []
        if isinstance(timeline, list):
            for item in timeline:
                if isinstance(item, dict):
                    normalized.append({
                        "round": item.get("round") or item.get("round_type") or item.get("stage"),
                        "date": item.get("date") or item.get("announcement_date"),
                        "amount_cny": item.get("amount_cny") or (item.get("amount", {}).get("value_cny") if isinstance(item.get("amount"), dict) else item.get("amount")),
                        "valuation_cny": item.get("valuation_cny") or item.get("valuation"),
                        "investors": item.get("investors") or item.get("lead_investors")
                    })
        profile["financing_timeline"] = normalized

    # ========== 4. 公司描述 ==========
    if not profile.get("description"):
        profile["description"] = (
            data.get("description") or
            data.get("company_description") or
            data.get("investment_thesis", {}).get("company_summary") or
            data.get("market_position", {}).get("market_position_summary") or
            "暂无描述"
        )

    # ========== 5. 核心团队 ==========
    def norm(name, info, title="核心成员"):
        if isinstance(info, dict):
            return {"name": name, "title": info.get("title") or info.get("role") or info.get("position") or title, "background": info.get("background") or info.get("experience") or "", "education": info.get("education") or ""}
        elif isinstance(info, str):
            return {"name": name, "title": title, "background": info, "education": ""}
        return {"name": str(name), "title": title, "background": "", "education": ""}

    team_list = []

    # 优先级 1: data.founders
    if isinstance(data.get("founders"), list):
        for f in data["founders"]:
            if isinstance(f, dict):
                team_list.append(norm(f.get("name", "Unknown"), f, "创始人"))
            elif isinstance(f, str):
                team_list.append({"name": f, "title": "创始人", "background": "", "education": ""})

    # 优先级 2: profile.team（中英文）
    pt = profile.get("team")
    if isinstance(pt, dict):
        for key in ["founders", "创始人"]:
            if key in pt and isinstance(val := pt[key], list) and val:
                for f in val:
                    team_list.append(norm(f.get("name", "Unknown") if isinstance(f, dict) else f, f if isinstance(f, dict) else {}, "创始人"))
                break
        for kp in pt.get("key_persons", [])[:5]:
            if isinstance(kp, str):
                team_list.append({"name": kp, "title": "核心人员", "background": "", "education": ""})
            elif isinstance(kp, dict):
                team_list.append(norm(kp.get("name", "Unknown"), kp, "核心人员"))
        for role_en, role_cn in [("CEO","CEO"),("CTO","CTO"),("CFO","CFO"),("COO","COO"),("VP","VP"),("VP_Technology","技术副总裁"),("Chief_Scientist","首席科学家"),("board_chair","董事长")]:
            val = pt.get(role_en) or pt.get(role_cn)
            if val:
                if isinstance(val, dict):
                    team_list.append(norm(role_en, val, role_en))
                elif isinstance(val, str):
                    team_list.append({"name": val, "title": role_en, "background": "", "education": ""})

    # 优先级 3: data.team
    if not team_list and isinstance(raw := data.get("team"), dict):
        for key in ["founders", "创始人"]:
            if key in raw and isinstance(val := raw[key], list) and val:
                for f in val:
                    team_list.append(norm(f.get("name", "Unknown") if isinstance(f, dict) else f, f if isinstance(f, dict) else {}, "创始人"))
                break
        for kp in raw.get("key_persons", [])[:5]:
            if isinstance(kp, str):
                team_list.append({"name": kp, "title": "核心人员", "background": "", "education": ""})

    # 优先级 4: 单个字段
    if not team_list:
        cs = data.get("chief_scientist")
        if cs and isinstance(cs, str):
            name = cs.split("（")[0] if "（" in cs else (cs.split("(")[0] if "(" in cs else cs)
            team_list.append({"name": name, "title": "首席科学家", "background": cs, "education": ""})
        cto_bg = data.get("cto_background")
        if cto_bg and isinstance(cto_bg, str):
            team_list.append({"name": "CTO", "title": "CTO", "background": cto_bg, "education": ""})
        p_root = data.get("profile", {})
        cs2 = p_root.get("chief_scientist")
        if cs2 and isinstance(cs2, str) and not any(m.get("title") == "首席科学家" for m in team_list):
            name = cs2.split("（")[0] if "（" in cs2 else (cs2.split("(")[0] if "(" in cs2 else cs2)
            team_list.append({"name": name, "title": "首席科学家", "background": cs2, "education": ""})

    # 兜底: 团队背景
    if not team_list:
        bg = (data.get("team", {}).get("background") or
              data.get("profile", {}).get("team", {}).get("background") or
              data.get("profile", {}).get("team_background"))
        if isinstance(bg, str) and len(bg) > 5:
            team_list.append({"name": "团队背景", "title": "背景", "background": bg, "education": ""})

    # 团队规模
    if "team_size" in data:
        team_list.append({"name": f"团队规模: {data['team_size']}", "title": "规模", "background": "", "education": ""})
    elif "size" in data.get("profile", {}):
        team_list.append({"name": f"团队规模: {data['profile']['size']}", "title": "规模", "background": "", "education": ""})

    profile["team"] = team_list

    # ========== 6. 业务、财务与风险 ==========
    if not profile.get("business_model"):
        bm = data.get("business_model") or data.get("profile", {}).get("business_model")
        if isinstance(bm, dict):
            streams = bm.get("revenue_streams") or bm.get("streams") or []
            if streams:
                parts = []
                for s in streams[:3]:
                    if isinstance(s, dict):
                        t = s.get("type", "")
                        pct = s.get("percentage", "")
                        if t:
                            parts.append(f"{t}（{pct}）" if pct else t)
                profile["business_model"] = " + ".join(parts) if parts else "待补充"
            else:
                profile["business_model"] = str(bm)[:200] if bm else "待补充"
        elif isinstance(bm, str):
            profile["business_model"] = bm[:300]
        else:
            profile["business_model"] = "待补充"

    # 💰 财务数据：保留完整 financials 嵌套
    financials = data.get("financials") or data.get("profile", {}).get("financials")
    if isinstance(financials, dict):
        profile["financials"] = financials
        # 提取常用指标
        rev = financials.get("revenue")
        if rev is None:
            for k in ["revenue_2025", "revenue_2025E", "revenue_2024"]:
                v = financials.get(k)
                if isinstance(v, dict):
                    rev = v.get("value_cny")
                    break
        profile["revenue"] = rev
        # 毛利率
        gm = financials.get("gross_margin") or financials.get("gross_margin_pct")
        if isinstance(gm, dict):
            profile["gross_margin"] = gm.get("2025H1") or gm.get("2024") or next(iter(gm.values()), None)
        elif gm:
            profile["gross_margin"] = gm
        # 亏损
        op_loss = financials.get("operating_loss")
        if isinstance(op_loss, dict):
            profile["operating_loss"] = op_loss.get("2024") or op_loss.get("2025H1") or next(iter(op_loss.values()), None)
        else:
            profile["operating_loss"] = op_loss
        net_loss = financials.get("net_loss")
        if isinstance(net_loss, dict):
            profile["net_loss"] = net_loss.get("2024") or net_loss.get("2025H1") or next(iter(net_loss.values()), None)
        else:
            profile["net_loss"] = net_loss
        profile["rd_expense"] = financials.get("rd_expense")
    else:
        profile["financials"] = {}

    # 风险因素 (同时放在 profile.risks 和 顶层)
    risks = data.get("risk_factors") or data.get("risks") or data.get("investment_concerns") or data.get("risk_items")
    if risks:
        profile["risks"] = risks[:10] if isinstance(risks, list) else [str(risks)]
        profile["risk_factors"] = profile["risks"]
    else:
        profile["risks"] = []
        profile["risk_factors"] = []
    
    # 竞争定位 (competitive_positioning) —— 放入 profile 供前端 hook 读取
    cp = data.get("competitive_positioning") or data.get("profile", {}).get("competitive_positioning")
    if isinstance(cp, dict):
        profile["competitive_positioning"] = cp
    else:
        profile["competitive_positioning"] = {}
    
    # 投资亮点/关注事项 —— 放入 profile 供 InvestmentThesisCard 读取
    if "investment_highlights" in data:
        profile["investment_highlights"] = data["investment_highlights"]
    if "investment_concerns" in data:
        profile["investment_concerns"] = data["investment_concerns"]
    if "investment_thesis" in data:
        profile["investment_thesis"] = data["investment_thesis"]
    
    # 客户/奖项/办公室 —— 确保在 profile 中
    for field in ["specific_clients", "awards", "global_offices", "order_book", "key_products"]:
        if field in data and field not in profile:
            profile[field] = data[field]
        elif field not in profile:
            profile[field] = [] if field not in ["order_book"] else {}
    
    # 打包技术/封装技术
    if "packaging_technologies" in data and "packaging_technologies" not in profile:
        profile["packaging_technologies"] = data["packaging_technologies"]
    if "detailed_products" in data and "detailed_products" not in profile:
        profile["detailed_products"] = data["detailed_products"]
    
    # 团队补充字段
    for field in ["cto_background", "chief_scientist", "team_overseas_ratio", "team_experience_ratio"]:
        if field in data and field not in profile:
            profile[field] = data[field]

    # ========== 7. 市场与投资论据 ==========
    mo = data.get("market_opportunity")
    if isinstance(mo, dict):
        tam = mo.get("tam") or mo.get("china_interconnect", {}).get("2030E") or mo.get("global_market_2025")
        profile["market_tam"] = tam
        profile["market_opportunity_summary"] = str(mo.get("description") or mo.get("growth_drivers", []))[:300]
    else:
        profile["market_tam"] = None
        profile["market_opportunity_summary"] = ""

    thesis = data.get("investment_thesis", {})
    if isinstance(thesis, dict):
        profile["investment_thesis_summary"] = (
            thesis.get("core_argument") or thesis.get("rationale") or
            thesis.get("investment_summary") or thesis.get("thesis") or
            str(thesis)[:300]
        )
        metrics = thesis.get("key_metrics_to_watch") or thesis.get("key_indicators") or thesis.get("watch_list")
        profile["key_metrics_to_watch"] = metrics[:5] if isinstance(metrics, list) else []
    else:
        ir = data.get("investment_recommendation", {})
        if isinstance(ir, dict):
            profile["investment_thesis_summary"] = ir.get("rationale") or ir.get("core_argument") or str(ir)[:200]
        else:
            profile["investment_thesis_summary"] = str(thesis)[:300] if thesis else ""
        profile["key_metrics_to_watch"] = []

    # ========== 8. 技术与合作 ==========
    # 技术栈聚合
    tech_stack = []
    for src in [
        data.get("technology", {}).get("technology_stack"),
        data.get("products_technology", {}).get("technology_stack"),
        data.get("technology_stack"),
        data.get("products_technology", {}).get("core_innovation"),
        data.get("competitive_advantages"),
        data.get("technology", {}).get("competitive_advantages")
    ]:
        if isinstance(src, list):
            tech_stack.extend(src[:10])
        elif isinstance(src, str):
            tech_stack.append(src[:100])

    # technical_metrics 中的技术信息
    tech_metrics = data.get("technology", {}).get("technical_metrics", {})
    if isinstance(tech_metrics, dict):
        chips = tech_metrics.get("chips_supported")
        if isinstance(chips, list):
            for c in chips[:5]:
                tech_stack.append(f"支持{c}")
        perf = tech_metrics.get("performance_claim")
        if perf and isinstance(perf, str):
            tech_stack.append(f"性能：{perf[:80]}")
        users = tech_metrics.get("platform_users")
        if users:
            tech_stack.append(f"平台用户：{users}")
        models = tech_metrics.get("models_supported")
        if models:
            tech_stack.append(f"支持模型：{models}")

    profile["technology_stack"] = list(dict.fromkeys(tech_stack))[:15] if tech_stack else []

    # 合作伙伴
    partners = (
        data.get("key_partners") or
        data.get("partnerships", {}).get("model_providers", []) +
        data.get("partnerships", {}).get("hardware_partners", []) +
        data.get("partnerships", {}).get("customers", []) +
        data.get("investment_committee_decision", {}).get("key_catalysts", [])
    )
    if isinstance(partners, list) and partners:
        unique = []
        for p in partners[:20]:
            if p not in unique:
                unique.append(p)
        profile["key_partners"] = unique[:10]
    else:
        profile["key_partners"] = []

    # ========== 9. 组装响应 ==========
    adapted = {**data, "profile": profile}

    for field in ["id", "name", "english_name", "industry", "analysis_date", "analyst"]:
        if field not in adapted:
            adapted[field] = data.get(field, "")

    if "industry" in adapted and "industry" not in profile:
        profile["industry"] = adapted["industry"]

    # 可比公司
    index = get_index()
    company_meta = next((c for c in index.get("companies", []) if c.get("id") == company_id), None)
    if company_meta:
        peers = [c for c in index.get("companies", []) if c.get("industry") == company_meta.get("industry") and c.get("id") != company_id]
        adapted["peers"] = peers[:5]
    else:
        adapted["peers"] = []

    return {"success": True, "data": adapted}




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
    
    @app.get("/favicon.svg")
    async def favicon():
        return FileResponse(str(FRONTEND_DIST / "favicon.svg"))
    
    @app.get("/")
    async def root():
        return FileResponse(str(FRONTEND_DIST / "index.html"))
    
    # 静态资源路由（只匹配已知的文件类型）
    @app.get("/assets/{filename:path}")
    async def assets(filename: str):
        file_path = FRONTEND_DIST / "assets" / filename
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        raise HTTPException(status_code=404)
    
    # 其他静态文件 (manifest, icons 等) - 必须在 index.html 同级
    @app.get("/{filename:path}")
    async def static_files(filename: str):
        file_path = FRONTEND_DIST / filename
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # 对于 SPA 路由，返回 index.html
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/")
    async def not_built():
        return JSONResponse(status_code=503, content={"error": "Not built"})
