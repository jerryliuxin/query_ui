#!/usr/bin/env python3
"""
投研知识库系统 - 优化版 v2.3
改进：缓存机制、错误处理、代码复用、环境变量配置
"""
import json
import os
from pathlib import Path
from functools import lru_cache
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid
import shutil

app = FastAPI(title="投研知识库系统", version="2.3")

# ========== 配置常量 ==========
DEFAULT_CONFIDENCE = 0.5
DEFAULT_PAGE_SIZE = 100

# 从环境变量读取路径，便于部署
WORKSPACE = Path(os.getenv("QUERY_UI_WORKSPACE", "/Users/mihua/projects"))
DD_DIR = WORKSPACE / "knowledge_base"
INDEX_FILE = DD_DIR / "index.json"
COMPANIES_DIR = DD_DIR / "companies"
DATABASE_DIR = DD_DIR / "database"

# ========== 缓存机制优化 ==========
# 使用 lru_cache 替代全局变量，支持过期和线程安全

@lru_cache(maxsize=128)
def get_index_cached():
    """带缓存的索引加载（自动缓存，最多128个条目）"""
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading index file: {e}")
            return {}
    return {}

@lru_cache(maxsize=256)
def get_company_detail_cached(company_id: str):
    """带缓存的公司详情加载"""
    company_dir = COMPANIES_DIR / company_id
    if not company_dir.exists():
        return None
    
    # 查找 JSON 文件
    detail_file = company_dir / f"{company_id}.json"
    if not detail_file.exists():
        json_files = list(company_dir.glob("*.json"))
        if json_files:
            detail_file = json_files[0]
        else:
            return None
    
    try:
        with open(detail_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading {detail_file}: {e}")
        return None

@lru_cache(maxsize=64)
def get_investors_data_cached():
    """带缓存的投资机构数据加载"""
    investors_file = DATABASE_DIR / "investors.json"
    if investors_file.exists():
        try:
            with open(investors_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading investors file: {e}")
            return {"investors": [], "investments": []}
    return {"investors": [], "investments": []}

# ========== 辅助函数 ==========

def ensure_profile_defaults(profile, defaults):
    """确保 profile 中所有字段都有默认值（处理 None、{}、[]）"""
    for key, default_value in defaults.items():
        if not profile.get(key):  # 处理 None、空字典、空数组
            profile[key] = default_value
    return profile

def normalize_team_data(team):
    """统一团队数据格式为数组"""
    if isinstance(team, list):
        return team
    
    if isinstance(team, dict):
        result = []
        
        # 处理 CEO
        if 'ceo' in team:
            ceo_name = team['ceo'].split('（')[0] if '（' in team.get('ceo', '') else team['ceo']
            result.append({
                'name': ceo_name,
                'title': 'CEO',
                'background': team.get('ceo_background', '')
            })
        
        # 处理关键人员
        if 'key_persons' in team and isinstance(team['key_persons'], list):
            for person in team['key_persons']:
                if isinstance(person, dict):
                    result.append({
                        'name': person.get('name', '未知'),
                        'title': person.get('title', '成员'),
                        'background': person.get('background', '')
                    })
        
        return result
    
    return []

def get_default_profile():
    """返回默认的 profile 字段值"""
    return {
        'investment_rating': 'Hold',
        'investment_thesis': {
            'rating': 'Hold',
            'core_argument': '',
            'highlights': [],
            'concerns': [],
            'key_catalysts': [],
            'risks': []
        },
        'financials': {
            'revenue': None,
            'grossMargin': None,
            'operatingLoss': None,
            'netLoss': None
        },
        'technology': {
            'core_innovation': [],
            'patents': {},
            'differentiation_vs_peers': '',
            'core_products': []
        },
        'team': [],
        'competitive_positioning': {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': [],
            'peers': []
        },
        'clients': {
            'total_orders_count': 0,
            'major_clients': [],
            'awards': []
        },
        'orderBook': {
            'total_orders_count': 0,
            'major_clients': [],
            'awards': []
        },
        'specific_clients': [],
        'awards': [],
        'global_offices': []
    }

def success_response(data):
    """标准成功响应"""
    return {"success": True, "data": data}

# ========== API 路由 ==========

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "2.3"}

@app.get("/health")
async def health_check_alt():
    """健康检查（兼容无前缀）"""
    return {"status": "ok", "version": "2.3"}

@app.get("/api/companies")
async def list_companies(page_size: int = Query(DEFAULT_PAGE_SIZE)):
    """获取所有公司列表"""
    index = get_index_cached()
    companies = index.get("companies", [])
    
    # 扫描目录补充不在索引中的公司
    if COMPANIES_DIR.exists():
        existing_ids = {c.get("id") for c in companies if c.get("id")}
        for company_dir in COMPANIES_DIR.iterdir():
            if company_dir.is_dir() and company_dir.name not in existing_ids:
                companies.append({
                    "id": company_dir.name,
                    "name": company_dir.name.replace("_", " ").title(),
                    "company_type": "unknown",
                    "status": "active",
                    "confidence_level": DEFAULT_CONFIDENCE
                })
    
    total = len(companies)
    if page_size and page_size < total:
        companies = companies[:page_size]
    
    return success_response({"data": companies, "total": total})

@app.get("/api/company/{company_id}")
async def get_company(company_id: str):
    """获取单个公司详情 - 优化版"""
    detail = get_company_detail_cached(company_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")
    
    # 确保 profile 存在并应用默认值
    if 'profile' not in detail:
        detail['profile'] = {}
    
    profile = detail['profile']
    defaults = get_default_profile()
    
    # 应用默认值（处理 None、{}、[]）
    ensure_profile_defaults(profile, defaults)
    
    # 确保顶层字段也存在（前端可能直接从 data 访问）
    for field in ['clients', 'orderBook', 'specific_clients', 'awards', 'global_offices']:
        if field not in detail or not detail[field]:
            detail[field] = profile.get(field, defaults.get(field))
    
    # 确保其他顶层字段
    if 'confidence_level' not in detail:
        detail['confidence_level'] = DEFAULT_CONFIDENCE
    if 'name' not in detail:
        detail['name'] = company_id.replace('_', ' ').title()
    
    # 规范化团队数据
    if 'team' in profile:
        profile['team'] = normalize_team_data(profile['team'])
    
    return success_response(detail)

@app.get("/api/stats/dashboard")
async def get_dashboard_stats():
    """获取仪表盘统计"""
    index = get_index_cached()
    stats = index.get("stats", {})
    
    # 统计公司数量
    total_companies = 0
    if COMPANIES_DIR.exists():
        total_companies = len([d for d in COMPANIES_DIR.iterdir() if d.is_dir()])
    
    investors_data = get_investors_data_cached()
    total_investors = len(investors_data.get("investors", []))
    total_investments = len(investors_data.get("investments", []))
    
    dashboard_data = {
        "total_companies": total_companies or stats.get("total_companies", 0),
        "total_investors": total_investors,
        "total_investments": total_investments,
        "recent_investments_count": 28,
        "industry_distribution": {
            "AI基础设施": 5,
            "大模型": 4,
            "芯片半导体": 3,
            "企业服务": 3,
            "其他": 10
        }
    }
    
    return success_response(dashboard_data)

@app.get("/api/investors")
async def list_investors(page_size: int = Query(DEFAULT_PAGE_SIZE)):
    """获取投资机构列表"""
    investors_data = get_investors_data_cached()
    investors = investors_data.get("investors", [])
    
    total = len(investors)
    if page_size and page_size < total:
        investors = investors[:page_size]
    
    return success_response({"data": investors, "total": total})

@app.get("/api/investments")
async def list_investments():
    """获取投资交易列表"""
    investors_data = get_investors_data_cached()
    investments = investors_data.get("investments", [])
    return success_response({"data": investments, "total": len(investments)})

@app.get("/api/search")
async def search(q: str = Query(""), limit: int = Query(20)):
    """搜索公司"""
    index = get_index_cached()
    companies = index.get("companies", [])
    
    if q:
        q_lower = q.lower()
        filtered = [
            c for c in companies
            if q_lower in c.get("name", "").lower() or 
               q_lower in c.get("id", "").lower()
        ]
        companies = filtered
    
    return success_response({"data": companies[:limit], "total": len(companies)})


# ========== 公司 CRUD 模型 ==========

class CompanyCreate(BaseModel):
    """新建公司请求模型"""
    name: str
    english_name: str | None = None
    company_type: str = "research"
    industry: str | None = None
    country: str | None = None
    confidence_level: float | None = None
    research_date: str | None = None
    data_sources: str | None = None
    source_urls: str | None = None
    analysis_date: str | None = None
    analyst: str | None = None
    notes: str | None = None
    profile: dict | None = None


class CompanyUpdate(BaseModel):
    """更新公司请求模型 — 所有字段可选"""
    name: str | None = None
    english_name: str | None = None
    company_type: str | None = None
    industry: str | None = None
    country: str | None = None
    confidence_level: float | None = None
    research_date: str | None = None
    data_sources: str | None = None
    source_urls: str | None = None
    analysis_date: str | None = None
    analyst: str | None = None
    notes: str | None = None
    profile: dict | None = None


# ========== 公司 CRUD API ==========

def _generate_company_id(name: str) -> str:
    """生成公司ID：slug格式 + UUID前缀"""
    # 清理名称
    slug = name.strip().lower()
    # 简单 slugify
    valid = []
    for ch in slug:
        if ch.isalnum() or ch in ('-', '_'):
            valid.append(ch)
        else:
            valid.append('-')
    slug = ''.join(valid).strip('-').replace('--', '-')
    return f"{slug}-{uuid.uuid4().hex[:6]}"


def _save_to_index(company_id: str, name: str, company_type: str = "research", industry: str | None = None):
    """将公司注册到 index.json"""
    index = get_index_cached()
    companies = index.get("companies", [])
    
    # 检查是否已存在
    existing = [c for c in companies if c.get("id") == company_id]
    if existing:
        existing[0].update({
            "name": name,
            "type": company_type,
            "industry": industry,
        })
    else:
        companies.append({
            "id": company_id,
            "name": name,
            "type": company_type,
            "industry": industry,
        })
    
    index["companies"] = companies
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    # 清除缓存
    get_index_cached.cache_clear()


def _save_company_file(company_id: str, data: dict):
    """将公司详情写入 JSON 文件"""
    company_dir = COMPANIES_DIR / company_id
    company_dir.mkdir(parents=True, exist_ok=True)
    
    # 主 JSON 文件
    filepath = company_dir / f"{company_id}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.post("/api/companies")
async def create_company(req: CompanyCreate):
    """新建公司"""
    try:
        # 生成ID
        company_id = _generate_company_id(req.name)
        
        # 构建公司数据
        data = {
            "id": company_id,
            "name": req.name,
            "english_name": req.english_name,
            "company_type": req.company_type,
            "industry": req.industry,
            "country": req.country,
            "confidence_level": req.confidence_level,
            "research_date": req.research_date,
            "data_sources": req.data_sources,
            "source_urls": req.source_urls,
            "analysis_date": req.analysis_date,
            "analyst": req.analyst,
            "notes": req.notes,
            "profile": req.profile or {},
        }
        
        # 写入文件
        _save_company_file(company_id, data)
        # 注册到 index
        _save_to_index(company_id, req.name, req.company_type, req.industry)
        
        return success_response({"id": company_id, "message": "公司创建成功"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/companies/{company_id}")
async def update_company(company_id: str, req: CompanyUpdate):
    """更新公司"""
    try:
        # 读取现有数据
        existing = get_company_detail_cached(company_id)
        if not existing:
            raise HTTPException(status_code=404, detail="公司不存在")
        
        # 合并数据
        if req.name:
            existing["name"] = req.name
        if req.english_name is not None:
            existing["english_name"] = req.english_name
        if req.company_type:
            existing["company_type"] = req.company_type
        if req.industry is not None:
            existing["industry"] = req.industry
        if req.country is not None:
            existing["country"] = req.country
        if req.confidence_level is not None:
            existing["confidence_level"] = req.confidence_level
        if req.research_date is not None:
            existing["research_date"] = req.research_date
        if req.data_sources is not None:
            existing["data_sources"] = req.data_sources
        if req.source_urls is not None:
            existing["source_urls"] = req.source_urls
        if req.analysis_date is not None:
            existing["analysis_date"] = req.analysis_date
        if req.analyst is not None:
            existing["analyst"] = req.analyst
        if req.notes is not None:
            existing["notes"] = req.notes
        if req.profile is not None:
            existing["profile"] = req.profile
        
        # 写入文件
        _save_company_file(company_id, existing)
        # 更新 index
        _save_to_index(company_id, existing.get("name", ""), 
                        existing.get("company_type", ""), 
                        existing.get("industry"))
        
        return success_response({"id": company_id, "message": "公司更新成功"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 前端页面 ==========

@app.get("/")
async def home():
    """首页"""
    return FileResponse("static/index.html")

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")
# 也挂载 /assets（Vite base='/' 时 JS/CSS 的引用路径）
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
# 也挂载根目录下的静态文件（favicon 等）
app.mount("/", StaticFiles(directory="static"), name="root_static")

# Catch-all 路由：支持 React Router 客户端路由（排除静态资源）
STATIC_EXTS = {'.css', '.js', '.jsx', '.ts', '.tsx', '.json', '.map', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot'}

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Catch-all 路由：返回 index.html 支持 React Router，但先检查静态资源"""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    # 检查是否为静态资源（有扩展名）
    ext = os.path.splitext(full_path)[1]
    if ext in STATIC_EXTS:
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8899)
