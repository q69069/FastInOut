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
export const getEmployees = () => api.get('/employees')
export const createEmployee = (data) => api.post('/employees', data)
export const updateEmployee = (data) => api.put(`/employees/${data.id}`, data)
export const getSuppliers = (params) => api.get('/suppliers', { params })
export const createPurchase = (data) => api.post('/purchases/purchase-orders', data)
export const getDashboard = () => api.get('/reports/dashboard')
export const getRoles = () => api.get('/roles')
export const updateRole = (data) => api.put(`/roles/${data.id}`, data)
export const getCompanySettings = () => api.get('/company')
export const updateCompanySettings = (data) => api.put('/company', data)
export const backupData = () => api.post('/backup')

// ========== 车销流程（Phase B） ==========

// 装车单
export const getVehicleLoads = (params) => api.get('/vehicle-loads', { params })
export const createVehicleLoad = (data) => api.post('/vehicle-loads', data)
export const getVehicleLoad = (id) => api.get(`/vehicle-loads/${id}`)
export const confirmVehicleLoad = (id) => api.post(`/vehicle-loads/${id}/confirm`)
export const returnVehicleLoad = (id) => api.post(`/vehicle-loads/${id}/return`)

// 销售单（车销开单）
export const getSalesDeliveries = (params) => api.get('/sales-deliveries', { params })
export const createSalesDelivery = (data) => api.post('/sales-deliveries', data)
export const getSalesDelivery = (id) => api.get(`/sales-deliveries/${id}`)
export const voidSalesDelivery = (id, data) => api.post(`/sales-deliveries/${id}/void`, data)

// 交账
export const getSettlements = (params) => api.get('/settlements', { params })
export const createSettlement = (data) => api.post('/settlements', data)
export const getSettlement = (id) => api.get(`/settlements/${id}`)
export const getPendingDeliveries = (params) => api.get('/settlements/pending-deliveries', { params })

// 退货单
export const getReturnDeliveries = (params) => api.get('/return-deliveries', { params })
export const getReturnDelivery = (id) => api.get(`/return-deliveries/${id}`)
export const warehouseConfirmReturn = (id) => api.post(`/return-deliveries/${id}/warehouse-confirm`)