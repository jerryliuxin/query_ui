import React, { useEffect, useState } from 'react'
import { Table, Typography } from 'antd'
import { getInvestors } from '../services/api'

const { Title } = Typography

const Investors: React.FC = () => {
  const [investors, setInvestors] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getInvestors({ page_size: 100 }).then(res => {
      if (res.success) {
        const data = res.data?.data || res.data || []
        setInvestors(data)
      }
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const columns = [
    { title: '机构ID', dataIndex: 'id', key: 'id', width: 150 },
    { title: '机构名称', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: '类型', dataIndex: 'investor_type', key: 'investor_type', width: 120 },
    { title: '地区', dataIndex: 'region', key: 'region', width: 100 },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
  ]

  return (
    <div>
      <Title level={5} style={{ marginBottom: 16 }}>投资机构列表</Title>
      <Table
        columns={columns}
        dataSource={investors.map(inv => ({ ...inv, key: inv.id }))}
        loading={loading}
        pagination={{ pageSize: 10 }}
        scroll={{ x: 800 }}
      />
    </div>
  )
}

export default Investors
