import axios from 'axios'
import { showToast } from 'vant'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/h5/login'
    }
    showToast(error.response?.data?.detail || '网络错误')
    return Promise.reject(error)
  }
)

export default api

export const login = (data) => api.post('/auth/login', data)
export const getCurrentUser = () => api.get('/auth/current')

// 待办任务
export const getTodoTasks = (params) => api.get('/todos', { params })
export const completeTask = (id) => api.post(`/todos/${id}/complete`)

// 拜访记录
export const getVisits = (params) => api.get('/visits', { params })
export const createVisit = (data) => api.post('/visits', data)

// 打卡
export const checkIn = (data) => api.post('/checkins', data)
export const getCheckinRecords = (params) => api.get('/checkins', { params })

// 销售订单
export const getSalesOrders = (params) => api.get('/sales-orders', { params })
export const createSalesOrder = (data) => api.post('/sales-orders', data)
export const orderToStockOut = (id) => api.post(`/sales-orders/${id}/stockout`)

// 库存查询
export const getInventory = (params) => api.get('/inventory', { params })
export const searchInventory = (params) => api.get('/inventory/search', { params })

// 应收款
export const getReceivables = (params) => api.get('/finance/receivables', { params })

// 业绩统计
export const getSalesmanStats = (params) => api.get('/salesmen/stats', { params })

// 打印
export const previewPrint = (templateId, docType, docId) => api.get(`/print-templates/${templateId}/preview/${docType}/${docId}`)

// 客户
export const getCustomers = (params) => api.get('/customers', { params })

// 商品
export const getProducts = (params) => api.get('/products', { params })
