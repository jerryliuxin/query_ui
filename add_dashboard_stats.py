#!/usr/bin/env python3
"""
Add /api/stats/dashboard endpoint to app_react.py
Returns enriched stats with:
- industry_distribution (count by industry)
- recent_investments_count (last 30 days)
"""

def add_dashboard_stats_route():
    import json
    from pathlib import Path
    from datetime import datetime, timedelta
    
    # 假设这些函数已在 app_react.py 中定义
    # 我们将代码直接注入
    
    code = '''
@app.get("/api/stats/dashboard")
async def api_dashboard_stats():
    """富化仪表盘统计数据"""
    index = get_index()
    companies = index.get("companies", [])
    investments = index.get("investments", [])
    
    # 1. 行业分布
    industry_dist = {}
    for c in companies:
        industry = c.get("industry", "未分类")
        industry_dist[industry] = industry_dist.get(industry, 0) + 1
    
    # 2. 近30天交易数
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    recent_count = 0
    for inv in investments:
        inv_date = inv.get("date", "")
        if inv_date >= thirty_days_ago:
            recent_count += 1
    
    return {
        "total_companies": len(companies),
        "total_investors": len(index.get("investors", [])),
        "total_investments": len(investments),
        "recent_investments_count": recent_count,
        "industry_distribution": industry_dist,
        "metadata": index.get("metadata", {})
    }
'''
    return code

if __name__ == "__main__":
    print(add_dashboard_stats_route())
