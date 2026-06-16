# 投研知识库查询界面

基于 FastAPI + Jinja2 的轻量级 Web 查询系统，支持：
- 投资机构列表与详情
- 被投公司列表与详情
- 投资交易浏览与筛选
- 全局搜索

---

## 🚀 启动服务

```bash
cd /home/mickey/.openclaw/mihua/tools/query_ui

# 安装依赖
pip3 install -r requirements.txt

# 启动服务
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

访问：http://localhost:8080

---

## 📂 目录结构

```
query_ui/
├── app.py                 # FastAPI 主应用
├── requirements.txt
├── static/
│   └── style.css         # 专业金融风格样式
└── templates/
    ├── base.html
    ├── index.html        # 首页
    ├── investors.html    # 机构列表
    ├── investor_detail.html  # 机构详情
    ├── companies.html    # 公司列表
    ├── company_detail.html   # 公司详情
    ├── investments.html  # 交易列表
    ├── investment_detail.html # 交易详情
    └── search_results.html    # 搜索结果
```

---

## 🎯 功能说明

### 1. 首页 `/`
显示统计卡片（公司、机构、交易数量）+ 最近交易预览

### 2. 投资机构 `/investors`
- 按赛道筛选
- 展示：名称、类型、地点、portfolio 数、基金数、置信度
- 点击进入详情页：基本信息、管理基金、退出记录、投资组合、相关交易

### 3. 被投公司 `/companies`
- 按行业筛选
- 展示：名称、英文名、行业、类型、分析日期、置信度
- 详情页：基本信息、关键指标、财务数据、团队背景、融资历史、投资方

### 4. 投资交易 `/investments`
- 按公司名、投资方筛选
- 表格列：日期、公司、轮次、总金额、估值、投资方数、领投方
- 详情页：交易ID、参与机构列表、数据来源、置信度

### 5. 全局搜索 `/search?q=...`
跨三个维度同时搜索并分组展示结果

---

## 🎨 设计风格

- **配色**: 深蓝 (#1e40af) + 金融金 (#f59e0b)
- **布局**: 卡片式、响应式（移动端友好）
- **字体**: 系统默认 sans-serif
- **状态标签**: 绿色（portfolio）、红色（screening）、黄色（pre_dd）

---

## 🔌 数据源

- 索引文件: `knowledge_base_dd/index.json`
- 完整档案: `knowledge_base_dd/companies/`, `investors/`, `investments/`

所有数据在启动时缓存，修改数据后重启服务或手动刷新。

---

## 📈 后续扩展建议

- [ ] 添加分页（当前列表可能很长）
- [ ] 投资机构关系图（D3.js 显示共同投资网络）
- [ ] 时间线视图（投融资历史时间轴）
- [ ] 导出 CSV/Excel
- [ ] 管理后台（修改数据）
- [ ] 与 FastAPI CORS 配置结合供其他系统调用

---

## 🧠 Frontend Agent 化

将此项目封装为 `frontend_agent`，实现：

```python
def generate_ui(schema: dict, output_dir: str):
    """
    根据输入数据结构（如 index.json 的 metadata）自动生成模板和样式
    支持: list/detail 两种视图，自动识别关联关系
    """
```

这样未来新增数据表（events, funds, exits）时，一键生成查询界面。

---

创建时间: 2026-03-24  
作者: Mihua Assistant
