export async function apiRequest(path: string, options: RequestInit = {}) {
  const url = `/api${path}`
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

// Companies
export async function getCompanies(params?: { page_size?: number }) {
  const qs = new URLSearchParams()
  if (params?.page_size) qs.set('page_size', String(params.page_size))
  const query = qs.toString() ? `?${qs.toString()}` : ''
  return fetch(`/api/companies${query}`).then(r => r.json())
}

export async function getCompany(id: string) {
  return fetch(`/api/company/${id}`).then(r => r.json())
}

export async function createCompany(data: Record<string, any>) {
  return apiRequest('/companies', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateCompany(id: string, data: Record<string, any>) {
  return apiRequest(`/companies/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

// Investors
export async function getInvestors(params?: { page_size?: number }) {
  const qs = new URLSearchParams()
  if (params?.page_size) qs.set('page_size', String(params.page_size))
  const query = qs.toString() ? `?${qs.toString()}` : ''
  return fetch(`/api/investors${query}`).then(r => r.json())
}

export async function getInvestments() {
  return fetch('/api/investments').then(r => r.json())
}

// Search
export async function searchCompanies(q: string, limit = 20) {
  return fetch(`/api/search?q=${encodeURIComponent(q)}&limit=${limit}`).then(r => r.json())
}

// Dashboard
export async function getDashboardStats() {
  return fetch('/api/stats/dashboard').then(r => r.json())
}
