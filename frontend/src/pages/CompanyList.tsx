import React, { useEffect, useState } from 'react'
import { Table, Button, Tag, Space, Input, Typography } from 'antd'
import { PlusOutlined, EditOutlined, SearchOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { getCompanies, searchCompanies } from '../services/api'

const { Search } = Input
const { Title } = Typography

const CompanyList: React.FC = () => {
  const navigate = useNavigate()
  const [companies, setCompanies] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [showSearch, setShowSearch] = useState(false)

  const fetchCompanies = async (q?: string) => {
    setLoading(true)
    try {
      let result
      if (q) {
        result = await searchCompanies(q)
      } else {
        result = await getCompanies({ page_size: 100 })
      }
      if (result.success) {
        const data = result.data?.data || result.data || []
        setCompanies(data)
      }
    } catch (e) {
      console.error('Failed to fetch companies:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCompanies()
  }, [])

  const handleSearch = () => {
    if (searchQuery.trim()) {
      fetchCompanies(searchQuery.trim())
    } else {
      fetchCompanies()
    }
  }

  const columns = [
    {
      title: '公司ID',
      dataIndex: 'id',
      key: 'id',
      width: 150,
      render: (id: string) => (
        <a onClick={() => navigate(`/company/${id}`)}>{id}</a>
      ),
    },
    {
      title: '公司名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: '类型',
      dataIndex: 'company_type',
      key: 'company_type',
      width: 120,
      render: (type: string) => (
        <Tag color={type === 'research' ? 'blue' : 'green'}>
          {type || 'unknown'}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'default'}>
          {status || 'active'}
        </Tag>
      ),
    },
    {
      title: '置信度',
      dataIndex: 'confidence_level',
      key: 'confidence_level',
      width: 80,
      render: (conf: number) => (conf ? `${Math.round(conf * 100)}%` : '-'),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: any, record: any) => (
        <Space>
          <a onClick={() => navigate(`/company/${record.id}`)}>详情</a>
          <a onClick={() => navigate(`/company/edit/${record.id}`)}>
            <EditOutlined /> 编辑
          </a>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={5} style={{ margin: 0 }}>公司列表</Title>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/company/new')}
          >
            新增公司
          </Button>
          <Button onClick={() => setShowSearch(!showSearch)}>
            <SearchOutlined /> 搜索
          </Button>
        </Space>
      </div>

      {showSearch && (
        <div style={{ marginBottom: 16 }}>
          <Search
            placeholder="搜索公司名称或ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onSearch={handleSearch}
            allowClear
            style={{ maxWidth: 400 }}
            onPressEnter={handleSearch}
          />
        </div>
      )}

      <Table
        columns={columns}
        dataSource={companies.map(c => ({ ...c, key: c.id }))}
        loading={loading}
        pagination={{ pageSize: 10 }}
        scroll={{ x: 800 }}
      />
    </div>
  )
}

export default CompanyList
