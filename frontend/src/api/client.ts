import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// ── Request: attach Bearer token ─────────────────────────────────────────────
api.interceptors.request.use((config) => {
  const raw = localStorage.getItem('wms-auth') ?? sessionStorage.getItem('wms-auth')
  if (raw) {
    try {
      const token: string | undefined = JSON.parse(raw)?.state?.token
      if (token) config.headers.Authorization = `Bearer ${token}`
    } catch { /* ignore */ }
  }
  return config
})

// ── Response: on 401 clear session and redirect to login ─────────────────────
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('wms-auth')
      sessionStorage.removeItem('wms-auth')
      if (window.location.pathname !== '/login') {
        window.location.replace('/login')
      }
    }
    return Promise.reject(error)
  }
)

export default api
