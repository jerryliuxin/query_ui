import React, { useState } from 'react'
import { Input, Table, Card, Typography } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import { searchCompanies } from '../services/api'

const { Title } = Typography

const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([])
      return
    }
    setLoading(true)
    try {
      const res = await searchCompanies(searchQuery, 50)
      if (res.success) {
        setResults(res.data?.data || res.data || [])
      }
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: 'ID', dataIndex: 'id', key: 'id', width: 200 },
    { title: '行业', dataIndex: 'industry', key: 'industry', width: 150 },
    { title: '类型', dataIndex: 'type', key: 'type', width: 100 },
  ]

  return (
    <div>
      <Title level={5} style={{ marginBottom: 16 }}>搜索公司</Title>
      <Card style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索公司名称或ID..."
          size="large"
          prefix={<SearchOutlined />}
          value={query}
          onChange={e => setQuery(e.target.value)}
          onPressEnter={() => handleSearch(query)}
          allowClear
        />
      </Card>
      <Table
        columns={columns}
        dataSource={results.map(r => ({ ...r, key: r.id || r.name }))}
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
    </div>
  )
}

export default SearchPage
