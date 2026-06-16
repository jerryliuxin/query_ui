import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Row,
  Col,
  Typography,
  Spin,
  Empty,
  Tabs,
} from 'antd'
import {
  EditOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons'
import { getCompany } from '../services/api'

const { Title, Text } = Typography

// Get all keys from the nested profile structure
function getAllProfileKeys(profile: any): string[] {
  if (!profile) return []
  const keys: string[] = []
  for (const key of Object.keys(profile)) {
    const val = profile[key]
    if (val === null || val === undefined || val === '') continue
    if (typeof val === 'object' && !Array.isArray(val)) {
      // Check if nested object has meaningful values
      const nestedVals = Object.values(val)
      if (nestedVals.some(v => v !== null && v !== undefined && v !== '' && v !== 0)) {
        for (const nk of Object.keys(val)) {
          keys.push(`${key}.${nk}`)
        }
        continue
      }
    }
    if (Array.isArray(val) && val.length > 0) {
      // Check if array has meaningful content
      const hasMeaningful = val.some(v => v !== null && v !== undefined && v !== '')
      if (hasMeaningful) keys.push(key)
      continue
    }
    if (typeof val === 'boolean') {
      keys.push(key)
      continue
    }
    if (typeof val === 'number') {
      keys.push(key)
      continue
    }
    if (typeof val === 'string' && val.length > 0) {
      keys.push(key)
    }
  }
  return keys
}

function formatLabel(key: string): string {
  const labelMap: Record<string, string> = {
    id: '公司ID',
    name: '公司名称',
    english_name: '英文名称',
    research_date: '研究日期',
    data_sources: '数据来源',
    source_urls: '来源链接',
    confidence_level: '置信度',
    analysis_version: '分析版本',
    has_financial_info: '有财务信息',
    has_funding_info: '有融资信息',
    valuation_mentioned: '提及估值',
    revenue_mentioned: '提及收入',
    products_mentioned: '提及产品',
    valuation_b: '估值(亿CNY)',
    pre_money_valuation_b: '投前估值(亿)',
    post_money_valuation_b: '投后估值(亿)',
    funding_rounds: '融资轮次',
    lead_investors: '领投机构',
    total_funding_b: '总融资(亿)',
    revenue_b: '收入(亿)',
    revenue_m: '收入(百万)',
    arr_b: 'ARR(亿)',
    mrr_m: 'MRR(百万)',
    gross_margin: '毛利率',
    net_margin: '净利率',
    operating_margin: '营业利润率',
    ebitda_margin: 'EBITDA利润率',
    growth_rate_yoy: '同比增长率',
    growth_rate_qoq: '环比增长率',
    cagr_3y: '三年CAGR',
    net_dollar_retention: '净留存率',
    churn_rate: '流失率',
    customer_acquisition_cost: '获客成本',
    ltv: '客户终身价值',
    ltv_cac_ratio: 'LTV/CAC比',
    market_share: '市场份额',
    tam_b: 'TAM(亿)',
    sam_b: 'SAM(亿)',
    som_b: 'SOM(亿)',
    key_competitors: '关键竞争对手',
    competitive_advantage: '竞争优势',
    founders: '创始人',
    employees: '员工数',
    employee_growth_rate: '员工增长率',
    rd_to_revenue_ratio: '研发收入比',
    board_members: '董事会成员',
    investor_representation: '投资方代表',
    ipo_status: 'IPO状态',
    ipo_timeline: 'IPO时间线',
    underwriters: '承销商',
    comparable_ipos: '可比IPO',
    ma_potential: '并购潜力',
    strategic_buyers: '战略买家',
    risk_factors: '风险因素',
    customer_concentration: '客户集中度',
    regulatory_risks: '监管风险',
    technology_risks: '技术风险',
    confidence_boost: '信心提升',
    valuation_usd: '估值(USD)',
    revenue_usd: '收入(USD)',
    revenue_scale: '收入规模',
    investment_rating: '投资评级',
  }
  return labelMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function formatValue(val: any): string {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'boolean') return val ? '是' : '否'
  if (typeof val === 'number') {
    if (val === 0) return '0'
    return val.toLocaleString()
  }
  if (typeof val === 'string') return val
  if (Array.isArray(val)) {
    return val.map(v => {
      if (typeof v === 'object') return JSON.stringify(v)
      return String(v)
    }).join('、')
  }
  if (typeof val === 'object') return JSON.stringify(val)
  return String(val)
}

function getConfidenceColor(level: number): string {
  if (level >= 0.8) return 'green'
  if (level >= 0.5) return 'orange'
  return 'red'
}

function getRatingTag(rating: string): { color: string; text: string } {
  const r = (rating || 'Hold').toLowerCase()
  if (r === 'buy' || r === '强烈建议') return { color: 'green', text: 'Buy' }
  if (r === 'sell' || r === '强烈卖出') return { color: 'red', text: 'Sell' }
  if (r === 'hold' || r === '持有') return { color: 'gold', text: 'Hold' }
  if (r === 'watch' || r === '关注') return { color: 'blue', text: 'Watch' }
  return { color: 'default', text: rating || 'N/A' }
}

const CompanyDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [company, setCompany] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    getCompany(id).then(res => {
      if (res.success) {
        setCompany(res.data)
      }
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [id])

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 40 }}><Spin size="large" /></div>
  }

  if (!company) {
    return <Empty description="未找到该公司" />
  }

  const profile = company.profile || {}
  const profileKeys = getAllProfileKeys(profile)

  // Group profile keys
  const groupKeys = (keys: string[]) => {
    const basic: string[] = []
    const financial: string[] = []
    const investment: string[] = []
    const risk: string[] = []
    const other: string[] = []

    for (const key of keys) {
      if (['confidence_level', 'id', 'name', 'english_name', 'research_date', 'data_sources', 'source_urls', 'analysis_version', 'valuation_usd', 'revenue_usd', 'revenue_scale', 'investment_rating'].includes(key)) {
        basic.push(key)
      } else if (['valuation_b', 'pre_money_valuation_b', 'post_money_valuation_b', 'total_funding_b', 'revenue_b', 'revenue_m', 'arr_b', 'mrr_m', 'gross_margin', 'net_margin', 'operating_margin', 'ebitda_margin', 'growth_rate_yoy', 'growth_rate_qoq', 'cagr_3y', 'ltv', 'ltv_cac_ratio', 'market_share', 'tam_b', 'sam_b', 'som_b', 'rd_to_revenue_ratio', 'revenue_b', 'revenue_m', 'revenue_usd'].includes(key)) {
        financial.push(key)
      } else if (['investment_rating', 'has_financial_info', 'has_funding_info', 'valuation_mentioned', 'revenue_mentioned', 'products_mentioned', 'funding_rounds', 'lead_investors', 'ipo_status', 'ipo_timeline', 'underwriters', 'comparable_ipos', 'ma_potential', 'strategic_buyers', 'ltv', 'ltv_cac_ratio'].includes(key)) {
        investment.push(key)
      } else if (['risk_factors', 'customer_concentration', 'regulatory_risks', 'technology_risks', 'key_competitors', 'competitive_advantage'].includes(key)) {
        risk.push(key)
      } else if (['founders', 'employees', 'employee_growth_rate', 'board_members', 'investor_representation', 'customer_acquisition_cost', 'net_dollar_retention', 'churn_rate'].includes(key)) {
        other.push(key)
      } else {
        other.push(key)
      }
    }

    return { basic, financial, investment, risk, other }
  }

  const groups = groupKeys(profileKeys)

  const renderGroup = (title: string, keys: string[]) => {
    if (keys.length === 0) return null
    return (
      <Card title={title} size="small" style={{ marginBottom: 16 }}>
        <Descriptions column={{ xs: 1, sm: 2, md: 2, lg: 3 }} size="small" bordered>
          {keys.map(key => (
            <Descriptions.Item key={key} label={formatLabel(key)}>
              {formatValue(profile[key])}
            </Descriptions.Item>
          ))}
        </Descriptions>
      </Card>
    )
  }

  const ratingTag = getRatingTag(profile.investment_rating || company.investment_rating || 'Hold')

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/companies')}
            style={{ marginRight: 8 }}
          >
            返回列表
          </Button>
          <Button
            icon={<EditOutlined />}
            onClick={() => navigate(`/company/edit/${id}`)}
            type="primary"
          >
            编辑公司
          </Button>
        </div>
      </div>

      {/* Header card with basic info */}
      <Card style={{ marginBottom: 16, background: 'linear-gradient(135deg, #ffffff 0%, #f0f6ff 100%)' }}>
        <Row gutter={[16, 16]} align="middle">
          <Col>
            <div style={{
              width: 80, height: 80, borderRadius: 12,
              background: 'linear-gradient(135deg, #1F4E79 0%, #4A6FA5 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 36, color: 'white', fontWeight: 'bold',
            }}>
              {(company.name || id || '?').charAt(0).toUpperCase()}
            </div>
          </Col>
          <Col flex="auto">
            <Title level={4} style={{ margin: 0 }}>
              {company.name} {company.english_name && <Text type="secondary">{company.english_name}</Text>}
            </Title>
            <div style={{ marginTop: 8, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <Tag color={ratingTag.color} style={{ fontSize: 14 }}>
                {ratingTag.text}
              </Tag>
              <Tag color={getConfidenceColor(company.confidence_level || 0)}>
                置信度 {Math.round((company.confidence_level || 0) * 100)}%
              </Tag>
              {company.company_type && (
                <Tag>{company.company_type}</Tag>
              )}
            </div>
          </Col>
        </Row>
      </Card>

      {/* Profile tabs */}
      <Tabs
        defaultActiveKey="basic"
        items={[
          { key: 'basic', label: '基本信息', children: renderGroup('基本信息', groups.basic) },
          { key: 'financial', label: '财务数据', children: renderGroup('财务数据', groups.financial) },
          { key: 'investment', label: '投资信息', children: renderGroup('投资信息', groups.investment) },
          { key: 'risk', label: '风险与竞争', children: renderGroup('风险与竞争', groups.risk) },
          { key: 'other', label: '其他数据', children: renderGroup('其他数据', groups.other) },
        ]}
      />
    </div>
  )
}

export default CompanyDetail
