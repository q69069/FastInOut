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
      window.location.href = '/login'
    }
    showToast(error.response?.data?.detail || '网络错误')
    return Promise.reject(error)
  }
)

export default api

export const login = (data) => api.post('/auth/login', data)
export const getCurrentUser = () => api.get('/auth/current')
export const getTodos = () => api.get('/todos')
export const getTodoTasks = (params) => api.get('/todos', { params })
export const getVisits = (params) => api.get('/customer-visits', { params })
export const createVisit = (data) => api.post('/customer-visits', data)
export const checkIn = (data) => api.post('/customer-visits', data)
export const getSalesOrders = (params) => api.get('/sales-orders', { params })
export const createSalesOrder = (data) => api.post('/sales-orders', data)
export const getInventory = (params) => api.get('/inventory', { params })
export const getReceivables = (params) => api.get('/finance/receivables', { params })
export const getSalesmanStats = (params) => api.get('/salesmen/stats', { params })
export const getCustomers = (params) => api.get('/customers', { params })
export const getProducts = (params) => api.get('/products', { params })
export const getWarehouses = () => api.get('/warehouses')
export const createTransfer = (data) => api.post('/inventory/transfers', data)
export const createInventoryCheck = (data) => api.post('/inventory/checks', data)
export const createLossReport = (data) => api.post('/inventory/other-out', data)
export const receivePayment = (data) => api.post('/finance/pre-receipt', data)
export const getPayments = (params) => api.get('/finance/payables', { params })
export const makePayment = (data) => api.post('/finance/pre-payment', data)
export const getCustomerAccounts = (params) => api.get('/finance/receivables', { params })
export const getSupplierAccounts = (params) => api.get('/finance/payables', { params })
export const getApproveList = (params) => api.get('/audit-logs', { params })
export const approveBill = (data) => api.post('/audit-logs', data)
export const rejectBill = (data) => api.post('/audit-logs', data)