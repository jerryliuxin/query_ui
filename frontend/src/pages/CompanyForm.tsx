import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Form,
  Input,
  InputNumber,
  Button,
  Card,
  Select,
  Tabs,
  message,
  Space,
  Row,
  Col,
  Divider,
  Typography,
  Spin,
} from 'antd'
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons'
import { getCompany, createCompany, updateCompany } from '../services/api'

const { TextArea } = Input
const { Title } = Typography

interface CompanyFormData {
  name: string
  english_name?: string
  company_type: string
  industry?: string
  country?: string
  confidence_level?: number
  research_date?: string
  data_sources?: string
  source_urls?: string
  analysis_date?: string
  analyst?: string
  notes?: string
  // profile fields
  investment_rating?: string
  valuation_cny?: number
  valuation_usd?: number
  revenue_2025?: number
  revenue_2026E?: number
  gross_margin?: string
  key_technology?: string
  key_clients?: string
  latest_funding_round?: string
  latest_funding_date?: string
  latest_funding_amount_cny?: number
  latest_funding_amount_usd?: number
  latest_funding_investors?: string
  latest_funding_note?: string
  employees?: number
  ipo_status?: string
  ipo_timeline?: string
  competitive_advantage?: string
  key_competitors?: string
  risk_factors?: string
  founders?: string
  board_members?: string
  strategic_buyers?: string
  ma_potential?: string
  market_share?: string
  tam_b?: number
  sam_b?: number
  som_b?: number
  cagr_3y?: number
  growth_rate_yoy?: number
  gross_margin_pct?: number
  net_margin?: number
  operating_margin?: number
  ebitda_margin?: number
  ltv_cac_ratio?: number
  rd_to_revenue_ratio?: number
  customer_acquisition_cost?: number
  net_dollar_retention?: number
  churn_rate?: number
  employee_growth_rate?: number
  customer_concentration?: string
  regulatory_risks?: string
  technology_risks?: string
  confidence_boost?: string
  ipo_status_note?: string
  valuation_note?: string
  revenue_note?: string
}

const CompanyForm: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const isEdit = !!id

  useEffect(() => {
    if (!isEdit) return
    setLoading(true)
    getCompany(id!).then(res => {
      if (res.success) {
        const data = res.data
        // Map top-level fields
        const formData: CompanyFormData = {
          name: data.name || '',
          english_name: data.english_name || undefined,
          company_type: data.company_type || 'research',
          industry: data.industry || undefined,
          country: data.country || undefined,
          confidence_level: data.confidence_level,
          research_date: data.research_date || undefined,
          data_sources: data.data_sources || undefined,
          source_urls: data.source_urls || undefined,
          analysis_date: data.analysis_date || undefined,
          analyst: data.analyst || undefined,
          notes: data.notes || undefined,
          // profile fields
          investment_rating: data.profile?.investment_rating || data.investment_rating || 'Hold',
          valuation_cny: data.valuation_cny || data.profile?.valuation_cny || data.profile?.valuation_indicators?.current_valuation_cny,
          valuation_usd: data.valuation_usd || data.profile?.valuation_usd,
          revenue_2025: data.profile?.revenue_2025 || undefined,
          revenue_2026E: data.profile?.revenue_2026E || undefined,
          gross_margin: data.profile?.gross_margin || undefined,
          key_technology: data.profile?.key_technology || undefined,
          key_clients: data.profile?.key_clients || data.profile?.clients?.map?.((c: any) => c.name)?.join(', ') || undefined,
          latest_funding_round: data.profile?.latest_funding?.round || data.profile?.funding_round || undefined,
          latest_funding_date: data.profile?.latest_funding?.date || undefined,
          latest_funding_amount_cny: data.profile?.latest_funding?.amount_cny || undefined,
          latest_funding_amount_usd: data.profile?.latest_funding?.amount_usd || undefined,
          latest_funding_investors: data.profile?.latest_funding?.investors?.join(', ') || data.profile?.lead_investors?.join(', ') || undefined,
          latest_funding_note: data.profile?.latest_funding?.note || data.profile?.funding_note || undefined,
          employees: data.profile?.employees || undefined,
          ipo_status: data.profile?.ipo_status || undefined,
          ipo_timeline: data.profile?.ipo_timeline || undefined,
          competitive_advantage: data.profile?.competitive_advantage || undefined,
          key_competitors: data.profile?.key_competitors || data.profile?.key_competitors?.join(', ') || undefined,
          risk_factors: data.profile?.risk_factors || data.profile?.risks?.join('\n') || undefined,
          founders: data.profile?.founders || undefined,
          board_members: data.profile?.board_members?.join(', ') || undefined,
          strategic_buyers: data.profile?.strategic_buyers?.join(', ') || undefined,
          ma_potential: data.profile?.ma_potential || undefined,
          market_share: data.profile?.market_share || undefined,
          tam_b: data.profile?.tam_b || undefined,
          sam_b: data.profile?.sam_b || undefined,
          som_b: data.profile?.som_b || undefined,
          cagr_3y: data.profile?.cagr_3y || undefined,
          growth_rate_yoy: data.profile?.growth_rate_yoy || undefined,
          gross_margin_pct: data.profile?.gross_margin || undefined,
          net_margin: data.profile?.net_margin || undefined,
          operating_margin: data.profile?.operating_margin || undefined,
          ebitda_margin: data.profile?.ebitda_margin || undefined,
          ltv_cac_ratio: data.profile?.ltv_cac_ratio || undefined,
          rd_to_revenue_ratio: data.profile?.rd_to_revenue_ratio || undefined,
          customer_acquisition_cost: data.profile?.customer_acquisition_cost || undefined,
          net_dollar_retention: data.profile?.net_dollar_retention || undefined,
          churn_rate: data.profile?.churn_rate || undefined,
          employee_growth_rate: data.profile?.employee_growth_rate || undefined,
          customer_concentration: data.profile?.customer_concentration || undefined,
          regulatory_risks: data.profile?.regulatory_risks || undefined,
          technology_risks: data.profile?.technology_risks || undefined,
          confidence_boost: data.profile?.confidence_boost || undefined,
          ipo_status_note: data.profile?.ipo_status || undefined,
          valuation_note: data.profile?.latest_funding?.note || undefined,
          revenue_note: data.profile?.revenue_note || undefined,
        }
        form.setFieldsValue(formData)
      }
      setLoading(false)
    }).catch(() => {
      message.error('加载公司数据失败')
      setLoading(false)
    })
  }, [id, isEdit, form])

  const handleSubmit = async (values: CompanyFormData) => {
    setSaving(true)
    try {
      const payload: Record<string, any> = {
        name: values.name,
        english_name: values.english_name,
        company_type: values.company_type,
        industry: values.industry,
        country: values.country,
        confidence_level: values.confidence_level,
        research_date: values.research_date,
        data_sources: values.data_sources,
        source_urls: values.source_urls,
        analysis_date: values.analysis_date,
        analyst: values.analyst,
        notes: values.notes,
        profile: {
          investment_rating: values.investment_rating,
        },
      }

      // Map profile fields
      const p = payload.profile as Record<string, any>

      // Valuation
      if (values.valuation_cny) p.valuation_cny = values.valuation_cny
      if (values.valuation_usd) p.valuation_usd = values.valuation_usd
      if (values.valuation_note) p.funding_note = values.valuation_note

      // Financials
      if (values.revenue_2025) p.revenue_2025 = values.revenue_2025
      if (values.revenue_2026E) p.revenue_2026E = values.revenue_2026E
      if (values.gross_margin) p.gross_margin = values.gross_margin
      if (values.gross_margin_pct) p.gross_margin = `${values.gross_margin_pct}%`
      if (values.net_margin !== undefined) p.net_margin = values.net_margin
      if (values.operating_margin !== undefined) p.operating_margin = values.operating_margin
      if (values.ebitda_margin !== undefined) p.ebitda_margin = values.ebitda_margin
      if (values.tam_b) p.tam_b = values.tam_b
      if (values.sam_b) p.sam_b = values.sam_b
      if (values.som_b) p.som_b = values.som_b
      if (values.cagr_3y) p.cagr_3y = values.cagr_3y
      if (values.growth_rate_yoy) p.growth_rate_yoy = values.growth_rate_yoy
      if (values.market_share) p.market_share = values.market_share
      if (values.rd_to_revenue_ratio) p.rd_to_revenue_ratio = values.rd_to_revenue_ratio
      if (values.customer_acquisition_cost) p.customer_acquisition_cost = values.customer_acquisition_cost
      if (values.ltv_cac_ratio) p.ltv_cac_ratio = values.ltv_cac_ratio
      if (values.net_dollar_retention) p.net_dollar_retention = values.net_dollar_retention
      if (values.churn_rate) p.churn_rate = values.churn_rate
      if (values.customer_concentration) p.customer_concentration = values.customer_concentration

      // Technology & Products
      if (values.key_technology) p.key_technology = values.key_technology

      // Key clients
      if (values.key_clients) {
        p.clients = values.key_clients.split('、').map(c => ({ name: c.trim() })).filter(c => c.name)
      }

      // Funding
      if (values.latest_funding_round) {
        p.funding_round = values.latest_funding_round
        p.latest_funding = {
          round: values.latest_funding_round,
          date: values.latest_funding_date,
          amount_cny: values.latest_funding_amount_cny,
          amount_usd: values.latest_funding_amount_usd,
        }
        if (values.latest_funding_investors) {
          p.latest_funding.investors = values.latest_funding_investors.split('、').map(i => i.trim()).filter(i => i)
        }
        if (values.latest_funding_note) p.latest_funding.note = values.latest_funding_note
      }

      // Team
      if (values.employees) p.employees = values.employees
      if (values.founders) p.founders = values.founders
      if (values.board_members) p.board_members = values.board_members.split('、').map(b => b.trim()).filter(b => b)
      if (values.employee_growth_rate) p.employee_growth_rate = values.employee_growth_rate

      // IPO
      if (values.ipo_status) {
        p.ipo_status = values.ipo_status
        p.ipo_timeline = values.ipo_timeline
      }

      // Competitive
      if (values.competitive_advantage) p.competitive_advantage = values.competitive_advantage
      if (values.key_competitors) p.key_competitors = values.key_competitors.split('、').map(k => k.trim()).filter(k => k)
      if (values.strategic_buyers) p.strategic_buyers = values.strategic_buyers.split('、').map(b => b.trim()).filter(b => b)
      if (values.ma_potential) p.ma_potential = values.ma_potential

      // Risks
      if (values.risk_factors) p.risks = values.risk_factors.split('\n').filter(r => r.trim())
      if (values.regulatory_risks) p.regulatory_risks = values.regulatory_risks
      if (values.technology_risks) p.technology_risks = values.technology_risks
      if (values.customer_concentration) p.customer_concentration = values.customer_concentration

      // Meta
      if (values.confidence_level) p.confidence_boost = values.confidence_level

      let result
      if (isEdit) {
        result = await updateCompany(id!, payload)
      } else {
        result = await createCompany(payload)
      }

      if (result.success) {
        message.success(isEdit ? '公司更新成功' : '公司创建成功')
        navigate(`/company/${result.data?.id || result.data?.company_id || id}`)
      } else {
        message.error(result.message || '保存失败')
      }
    } catch (e) {
      console.error('Save error:', e)
      message.error('保存失败：' + (e as Error).message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 40 }}><Spin size="large" /></div>
  }

  const tabItems = [
    {
      key: 'basic',
      label: '基本信息',
      children: (
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12}>
            <Form.Item name="name" label="公司名称" rules={[{ required: true, message: '请输入公司名称' }]}>
              <Input placeholder="如：华封科技" />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item name="english_name" label="英文名称">
              <Input placeholder="如：Capcon Technology" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="company_type" label="公司类型">
              <Select>
                <Select.Option value="research">研究</Select.Option>
                <Select.Option value="public">上市公司</Select.Option>
                <Select.Option value="private">非上市公司</Select.Option>
                <Select.Option value="startup">初创公司</Select.Option>
                <Select.Option value="investment">投资机构</Select.Option>
              </Select>
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="industry" label="行业">
              <Input placeholder="如：先进封装" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="country" label="国家/地区">
              <Input placeholder="如：China" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="confidence_level" label="置信度">
              <InputNumber min={0} max={1} step={0.05} style={{ width: '100%' }} placeholder="0-1" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="research_date" label="研究日期">
              <Input placeholder="YYYY-MM-DD" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="analysis_date" label="分析日期">
              <Input placeholder="YYYY-MM-DD" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="analyst" label="分析师">
              <Input placeholder="分析师姓名" />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="data_sources" label="数据来源">
              <TextArea rows={2} placeholder="每行一个数据源" />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="source_urls" label="来源链接">
              <TextArea rows={2} placeholder="每行一个URL" />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="notes" label="备注">
              <TextArea rows={3} placeholder="额外备注信息" />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
    {
      key: 'financial',
      label: '财务数据',
      children: (
        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Form.Item name="revenue_2025" label="2025年收入(USD)">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="如：300000000" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="revenue_2026E" label="2026E收入(USD)">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="预计值" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="gross_margin" label="毛利率">
              <Input placeholder="如：>40%" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="net_margin" label="净利率">
              <InputNumber min={-100} max={100} style={{ width: '100%' }} placeholder="百分比%" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="operating_margin" label="营业利润率">
              <InputNumber min={-100} max={100} style={{ width: '100%' }} placeholder="百分比%" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="ebitda_margin" label="EBITDA利润率">
              <InputNumber min={-100} max={100} style={{ width: '100%' }} placeholder="百分比%" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="growth_rate_yoy" label="同比增长率(%)">
              <InputNumber min={-100} max={1000} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="cagr_3y" label="三年CAGR(%)">
              <InputNumber min={0} max={1000} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="rd_to_revenue_ratio" label="研发投入占比(%)">
              <InputNumber min={0} max={100} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="ltv_cac_ratio" label="LTV/CAC比">
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="net_dollar_retention" label="净留存率(%)">
              <InputNumber min={0} max={500} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="churn_rate" label="流失率(%)">
              <InputNumber min={0} max={100} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="market_share" label="市场份额">
              <Input placeholder="如：15%" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="tam_b" label="TAM(亿USD)">
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="sam_b" label="SAM(亿USD)">
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="som_b" label="SOM(亿USD)">
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="customer_concentration" label="客户集中度">
              <TextArea rows={2} placeholder="描述主要客户占比情况" />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
    {
      key: 'investment',
      label: '投资信息',
      children: (
        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Form.Item name="investment_rating" label="投资评级">
              <Select>
                <Select.Option value="Buy">Buy</Select.Option>
                <Select.Option value="Hold">Hold</Select.Option>
                <Select.Option value="Sell">Sell</Select.Option>
                <Select.Option value="Watch">Watch</Select.Option>
              </Select>
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="valuation_cny" label="估值(CNY)">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="人民币金额" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="valuation_usd" label="估值(USD)">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="美元金额" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="latest_funding_round" label="最新融资轮次">
              <Input placeholder="如：Pre-IPO" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="latest_funding_date" label="融资日期">
              <Input placeholder="YYYY-MM-DD" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="latest_funding_amount_cny" label="融资金额(CNY)">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="人民币" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="latest_funding_amount_usd" label="融资金额(USD)">
              <InputNumber min={0} style={{ width: '100%' }} placeholder="美元" />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="latest_funding_investors" label="投资方">
              <Input placeholder="多个投资方用、分隔" />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="latest_funding_note" label="融资备注">
              <TextArea rows={2} placeholder="如：投前估值10亿美金" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="ipo_status" label="IPO状态">
              <Input placeholder="如：计划中、已提交" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="ipo_timeline" label="IPO时间线">
              <Input placeholder="如：2026年5月" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="ma_potential" label="并购潜力">
              <Input placeholder="并购可能性分析" />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="strategic_buyers" label="战略买家">
              <Input placeholder="潜在战略买家，多个用、分隔" />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="notes" label="投资备注">
              <TextArea rows={3} placeholder="投资分析备注" />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
    {
      key: 'business',
      label: '业务与技术',
      children: (
        <Row gutter={[16, 16]}>
          <Col xs={24}>
            <Form.Item name="key_technology" label="核心技术">
              <TextArea rows={2} placeholder="核心技术描述" />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="competitive_advantage" label="竞争优势">
              <TextArea rows={2} placeholder="核心竞争优势" />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="key_clients" label="关键客户">
              <Input placeholder="多个客户用、分隔" />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="key_competitors" label="关键竞争对手">
              <Input placeholder="多个竞争对手用、分隔" />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="employees" label="员工数">
              <InputNumber min={0} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} md={8}>
            <Form.Item name="employee_growth_rate" label="员工增长率(%)">
              <InputNumber min={-100} max={1000} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="founders" label="创始人">
              <Input placeholder="创始人姓名" />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="board_members" label="董事会成员">
              <Input placeholder="多个用、分隔" />
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item name="notes" label="备注">
              <TextArea rows={2} placeholder="业务与技术相关备注" />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
    {
      key: 'risks',
      label: '风险分析',
      children: (
        <Row gutter={[16, 16]}>
          <Col xs={24}>
            <Form.Item name="risk_factors" label="风险因素">
              <TextArea rows={5} placeholder="每个风险因素一行" />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item name="regulatory_risks" label="监管风险">
              <TextArea rows={3} placeholder="监管政策相关风险" />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item name="technology_risks" label="技术风险">
              <TextArea rows={3} placeholder="技术路线、研发风险" />
            </Form.Item>
          </Col>
        </Row>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(-1)}
            style={{ marginRight: 8 }}
          >
            返回
          </Button>
          <Title level={5} style={{ margin: 0, display: 'inline' }}>
            {isEdit ? `编辑公司: ${id}` : '新增公司'}
          </Title>
        </div>
      </div>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            company_type: 'research',
            investment_rating: 'Hold',
            confidence_level: 0.8,
          }}
        >
          <Tabs items={tabItems} defaultActiveKey="basic" />

          <Divider />

          <div style={{ textAlign: 'right' }}>
            <Space>
              <Button onClick={() => navigate(-1)}>取消</Button>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={saving}
              >
                {isEdit ? '保存修改' : '创建公司'}
              </Button>
            </Space>
          </div>
        </Form>
      </Card>
    </div>
  )
}

export default CompanyForm
