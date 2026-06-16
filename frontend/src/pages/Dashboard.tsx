import React, { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic, Typography } from 'antd'
import { ArrowUpOutlined, BuildOutlined, TeamOutlined } from '@ant-design/icons'
import { getDashboardStats, getCompanies } from '../services/api'

const { Title } = Typography

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null)
  const [recentCompanies, setRecentCompanies] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getDashboardStats(),
      getCompanies({ page_size: 5 }),
    ]).then(([statsRes, companiesRes]) => {
      if (statsRes.success) setStats(statsRes.data)
      if (companiesRes.success) {
        const data = companiesRes.data?.data || companiesRes.data || []
        setRecentCompanies(data)
      }
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 40 }}>加载中...</div>
  }

  return (
    <div>
      <Title level={4}>仪表盘概览</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="公司总数"
              value={stats?.total_companies || 0}
              prefix={<BuildOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="投资机构"
              value={stats?.total_investors || 0}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="投资交易"
              value={stats?.total_investments || 0}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="近期交易"
              value={stats?.recent_investments_count || 0}
              prefix={<ArrowUpOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {stats?.industry_distribution && Object.keys(stats.industry_distribution).length > 0 && (
        <Card title="行业分布" style={{ marginTop: 16 }}>
          {Object.entries(stats.industry_distribution).map(([name, count]) => (
            <div key={name} style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
              <span style={{ width: 120 }}>{name}</span>
              <div
                style={{
                  flex: 1,
                  height: 8,
                  background: '#f0f0f0',
                  borderRadius: 4,
                  overflow: 'hidden',
                  marginRight: 12,
                }}
              >
                <div
                  style={{
                    width: `${(count as number) / (stats.total_companies || 1) * 100}%`,
                    height: '100%',
                    background: '#1F4E79',
                    borderRadius: 4,
                    transition: 'width 0.3s',
                  }}
                />
              </div>
              <span style={{ width: 30, textAlign: 'right' }}>{String(count)}</span>
            </div>
          ))}
        </Card>
      )}

      <Card title="最近添加的公司" style={{ marginTop: 16 }}>
        {recentCompanies.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#999' }}>暂无数据</div>
        ) : (
          recentCompanies.map((company) => (
            <div key={company.id} style={{
              display: 'flex',
              justifyContent: 'space-between',
              padding: '8px 0',
              borderBottom: '1px solid #f5f5f5',
            }}>
              <span>{company.name}</span>
              <span style={{ color: '#999', fontSize: 12 }}>
                {company.company_type || 'unknown'}
              </span>
            </div>
          ))
        )}
      </Card>
    </div>
  )
}

export default Dashboard
