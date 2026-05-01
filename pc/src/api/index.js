import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

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
      router.push('/login')
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
export const createWarehouse = (data) => api.post('/warehouses', data)
export const updateWarehouse = (id, data) => api.put(`/warehouses/${id}`, data)
export const deleteWarehouse = (id) => api.delete(`/warehouses/${id}`)
export const setWarehouseDefault = (id) => api.put(`/warehouses/${id}/default`)

// 单位管理
export const getUnits = (params) => api.get('/units', { params })
export const getAllUnits = () => api.get('/units/all')
export const createUnit = (data) => api.post('/units', data)
export const updateUnit = (id, data) => api.put(`/units/${id}`, data)
export const deleteUnit = (id) => api.delete(`/units/${id}`)

// 单位换算
export const getUnitConversions = (params) => api.get('/units/conversions', { params })
export const createUnitConversion = (data) => api.post('/units/conversions', data)
export const deleteUnitConversion = (id) => api.delete(`/units/conversions/${id}`)
export const getProductUnitConfig = (productId) => api.get(`/units/product/${productId}/config`)
export const convertQuantity = (params) => api.post('/units/convert', null, { params })

// 采购
export const getPurchaseOrders = (params) => api.get('/purchase-orders', { params })
export const createPurchaseOrder = (data) => api.post('/purchase-orders', data)

// 采购退货
export const getPurchaseReturns = (params) => api.get('/purchase-returns', { params })
export const createPurchaseReturn = (data) => api.post('/purchase-returns', data)
export const getPurchaseReturn = (id) => api.get(`/purchase-returns/${id}`)
export const confirmPurchaseReturn = (id) => api.post(`/purchase-returns/${id}/confirm`)

// 销售
export const getSalesOrders = (params) => api.get('/sales-orders', { params })
export const createSalesOrder = (data) => api.post('/sales-orders', data)

// 销售退货
export const getSalesReturns = (params) => api.get('/sales-returns', { params })
export const createSalesReturn = (data) => api.post('/sales-returns', data)
export const getSalesReturn = (id) => api.get(`/sales-returns/${id}`)
export const confirmSalesReturn = (id) => api.post(`/sales-returns/${id}/confirm`)

// 库存
export const getInventory = (params) => api.get('/inventory', { params })
export const getInventoryAlerts = () => api.get('/inventory/alerts')

// 调拨
export const getTransfers = (params) => api.get('/inventory/transfers', { params })
export const createTransfer = (data) => api.post('/inventory/transfers', data)
export const getTransfer = (id) => api.get(`/inventory/transfers/${id}`)
export const confirmTransfer = (id) => api.post(`/inventory/transfers/${id}/confirm`)
export const cancelTransfer = (id) => api.delete(`/inventory/transfers/${id}`)

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

// 促销
export const getPromotions = (params) => api.get('/promotions', { params })
export const createPromotion = (data) => api.post('/promotions', data)
export const updatePromotion = (id, data) => api.put(`/promotions/${id}`, data)
export const deletePromotion = (id) => api.delete(`/promotions/${id}`)

// 角色
export const getRoles = (params) => api.get('/roles', { params })
export const getAllRoles = () => api.get('/roles/all')
export const createRole = (data) => api.post('/roles', data)
export const updateRole = (id, data) => api.put(`/roles/${id}`, data)
export const deleteRole = (id) => api.delete(`/roles/${id}`)
export const assignRole = (data) => api.post('/roles/assign', data)

// 备份
export const exportBackup = () => api.get('/backup/export', { responseType: 'blob' })
export const importBackup = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/backup/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
}

// 客户联系人
export const getContacts = (params) => api.get('/contacts', { params })
export const createContact = (data) => api.post('/contacts', data)
export const updateContact = (id, data) => api.put(`/contacts/${id}`, data)
export const deleteContact = (id) => api.delete(`/contacts/${id}`)

// 拜访记录
export const getVisits = (params) => api.get('/visits', { params })
export const createVisit = (data) => api.post('/visits', data)
export const deleteVisit = (id) => api.delete(`/visits/${id}`)

// 业务员提成
export const getSalesmen = (params) => api.get('/salesmen', { params })
export const getSalesmanStats = (params) => api.get('/salesmen/stats', { params })
export const createSalesman = (data) => api.post('/salesmen', data)
export const updateSalesman = (id, data) => api.put(`/salesmen/${id}`, data)

// 客户价格等级
export const getCustomerPrices = (params) => api.get('/customer-prices', { params })
export const createCustomerPrice = (data) => api.post('/customer-prices', data)
export const updateCustomerPrice = (id, data) => api.put(`/customer-prices/${id}`, data)
export const deleteCustomerPrice = (id) => api.delete(`/customer-prices/${id}`)
export const queryCustomerPrice = (params) => api.get('/customer-prices/query', { params })

// 系统
export const getEmployees = (params) => api.get('/employees', { params })
export const getCategories = (params) => api.get('/categories', { params })
