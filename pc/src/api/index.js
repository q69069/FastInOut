import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
api.interceptors.response.use(
  response => {
    const { data } = response
    if (data.code && data.code !== 200) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(data)
    }
    return data
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    ElMessage.error(error.response?.data?.detail || '网络错误')
    return Promise.reject(error)
  }
)

export default api

// 认证
export const login = (data) => api.post('/auth/login', data)
export const getCurrentUser = () => api.get('/auth/current')

// 仪表盘
export const getDashboard = () => api.get('/reports/dashboard')

// 商品
export const getProducts = (params) => api.get('/products', { params })
export const createProduct = (data) => api.post('/products', data)
export const updateProduct = (id, data) => api.put(`/products/${id}`, data)
export const deleteProduct = (id) => api.delete(`/products/${id}`)

// 客户
export const getCustomers = (params) => api.get('/customers', { params })
export const createCustomer = (data) => api.post('/customers', data)
export const updateCustomer = (id, data) => api.put(`/customers/${id}`, data)
export const deleteCustomer = (id) => api.delete(`/customers/${id}`)

// 供应商
export const getSuppliers = (params) => api.get('/suppliers', { params })
export const createSupplier = (data) => api.post('/suppliers', data)
export const updateSupplier = (id, data) => api.put(`/suppliers/${id}`, data)
export const deleteSupplier = (id) => api.delete(`/suppliers/${id}`)

// 仓库
export const getWarehouses = (params) => api.get('/warehouses', { params })

// 采购
export const getPurchaseOrders = (params) => api.get('/purchase-orders', { params })
export const createPurchaseOrder = (data) => api.post('/purchase-orders', data)

// 销售
export const getSalesOrders = (params) => api.get('/sales-orders', { params })
export const createSalesOrder = (data) => api.post('/sales-orders', data)

// 库存
export const getInventory = (params) => api.get('/inventory', { params })
export const getInventoryAlerts = () => api.get('/inventory/alerts')

// 财务
export const getReceipts = (params) => api.get('/finance/receipts', { params })
export const createReceipt = (data) => api.post('/finance/receipts', data)
export const getPayments = (params) => api.get('/finance/payments', { params })
export const createPayment = (data) => api.post('/finance/payments', data)
export const getReceivables = () => api.get('/finance/receivables')
export const getPayables = () => api.get('/finance/payables')
export const getFinanceFlow = (params) => api.get('/finance/flow', { params })

// 报表
export const getSalesReport = (params) => api.get('/reports/sales', { params })
export const getPurchaseReport = (params) => api.get('/reports/purchase', { params })
export const getInventoryReport = (params) => api.get('/reports/inventory', { params })
export const getProfitReport = (params) => api.get('/reports/profit', { params })

// 系统
export const getEmployees = (params) => api.get('/employees', { params })
export const getCategories = (params) => api.get('/categories', { params })
