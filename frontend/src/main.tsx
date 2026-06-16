import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import CompanyList from './pages/CompanyList'
import CompanyDetail from './pages/CompanyDetail'
import CompanyForm from './pages/CompanyForm'
import Investors from './pages/Investors'
import SearchPage from './pages/SearchPage'

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'companies', element: <CompanyList /> },
      { path: 'company/:id', element: <CompanyDetail /> },
      { path: 'company/edit/:id', element: <CompanyForm /> },
      { path: 'company/new', element: <CompanyForm /> },
      { path: 'investors', element: <Investors /> },
      { path: 'search', element: <SearchPage /> },
    ],
  },
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#1F4E79',
          borderRadius: 6,
        },
      }}
    >
      <RouterProvider router={router} />
    </ConfigProvider>
  </React.StrictMode>,
)
