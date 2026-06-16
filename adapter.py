#!/usr/bin/env python3
"""
HTML Template Data Adapter
将知识库的 company JSON 转换为 company_detail.html 模板所需的所有变量
"""

def adapt_company_for_detail(company: dict) -> dict:
    """
    转换公司数据，使其适应 company_detail.html 模板
    
    模板使用的变量包括：
    - company (原始对象)
    - profile (基础信息: stage, founded, headquarters, description, industry, is_unicorn...)
    - financials (财务: gross_margin_range...)
    - funding (融资: last_round...)
    - investment_thesis (it) - 投资建议
    - risks (risk_items)
    - team (团队列表)
    - comparable_companies
    - 各种嵌套字段
    """
    profile = company.get("profile", {})
    financials = company.get("financials", {})
    
    # 构建 profile 别名
    profile_vars = dict(profile)
    
    # 映射常见字段
    if "funding_stage" in profile and "stage" not in profile:
        profile_vars["stage"] = profile["funding_stage"]
    else:
        profile_vars["stage"] = profile.get("stage", "")
    
    # 确保基础字段都有默认值（避免 Undefined）
    for key in ["founded", "headquarters", "description", "industry", "is_unicorn"]:
        profile_vars.setdefault(key, profile.get(key, ""))
    
    # 构建 financing_timeline 的 event 对象（模板里遍历）
    financing_timeline = profile.get("financing_timeline", [])
    # 确保每个 event 都有 required fields
    for event in financing_timeline:
        event.setdefault("year", "")
        event.setdefault("round", "")
        event.setdefault("valuation_cny", None)
        event.setdefault("valuation_usd", None)
        event.setdefault("note", "")
    
    # investment_thesis (模板里叫 it)
    investment_thesis = company.get("investment_thesis", {})
    if not investment_thesis:
        investment_thesis = {
            "core_argument": "",
            "investment_rating": company.get("investment_rating", ""),
            "catalyst": "",
            "financial_impact": "",
            "risk_factors": []
        }
    
    # 确保 investment_thesis 嵌套字段存在
    it = investment_thesis
    it.setdefault("core_argument", "")
    it.setdefault("investment_rating", company.get("investment_rating", ""))
    it.setdefault("catalyst", "")
    it.setdefault("financial_impact", "")
    it.setdefault("risk_factors", [])
    
    # 估值相关（模板里用到 current_valuation, target_valuation_ipo）
    current_valuation = company.get("current_valuation") or {}
    if not current_valuation:
        current_valuation = {"pre_ipo_round": {"valuation_cny": None, "ps_multiple": None}}
    pre_ipo = current_valuation.get("pre_ipo_round", {})
    pre_ipo.setdefault("valuation_cny", None)
    pre_ipo.setdefault("ps_multiple", None)
    
    target_valuation_ipo = company.get("target_valuation_ipo") or {"base_case": None, "bull_case": None}
    target_valuation_ipo.setdefault("base_case", None)
    target_valuation_ipo.setdefault("bull_case", None)
    
    # 构建完整的 context
    context = {
        # 原始数据
        "company": company,
        "profile": profile_vars,
        "financials": financials,
        "funding": company.get("last_funding", {}),
        "investment_thesis": it,
        "risks": company.get("risks", []),
        "team": company.get("team", []),
        "comparable_companies": company.get("comparable_companies", []),
        "valuation_indicators": company.get("valuation_indicators", {}),
        
        # 扁平化顶级字段（方便模板直接访问）
        "id": company.get("id", ""),
        "name": company.get("name", ""),
        "english_name": company.get("english_name", ""),
        "industry": company.get("industry", ""),
        "analysis_date": company.get("analysis_date", ""),
        "analyst": company.get("analyst", ""),
        "company_type": company.get("company_type", ""),
        "confidence_level": company.get("confidence_level", 0),
        "investment_rating": company.get("investment_rating", ""),
        "revenue": company.get("revenue"),
        "valuation": company.get("valuation"),
        "business_model": company.get("business_model", ""),
        "data_sources": company.get("data_sources", []),
        
        # 嵌套对象（安全访问）
        "financing_timeline": financing_timeline,
        "current_valuation": current_valuation,
        "target_valuation_ipo": target_valuation_ipo,
        "team_size": company.get("team_size", profile.get("team_size", "")),
        "team_experience_ratio": profile.get("team_experience_ratio", ""),
        "team_overseas_ratio": profile.get("team_overseas_ratio", ""),
        
        # 技术
        "technology": profile.get("technology", {}),
        "core_innovation": profile.get("technology", {}).get("core_innovation", []),
        "differentiation_vs_peers": profile.get("technology", {}).get("differentiation_vs_peers", ""),
        
        # 客户与产品
        "major_clients": profile.get("major_clients", []),
        "specific_clients": profile.get("specific_clients", []),
        "key_products": profile.get("key_products", []),
        "detailed_products": profile.get("detailed_products", []),
        
        # 全球布局
        "global_offices": profile.get("global_offices", []),
        "packaging_technologies": profile.get("packaging_technologies", []),
        
        # 荣誉
        "awards": profile.get("awards", []),
        "industry_certification": profile.get("industry_certification", ""),
        "benchmark_insights": profile.get("benchmark_insights", ""),
        "funding_pressure": profile.get("funding_pressure", ""),
        
        # 其他模板可能用到的
        "raw_data": company,  # 原始 JSON 用于调试
    }
    
    return context
