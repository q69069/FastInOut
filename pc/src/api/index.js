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
export const getPurchaseOrder = (id) => api.get(`/purchase-orders/${id}`)
export const updatePurchaseOrder = (id, data) => api.put(`/purchase-orders/${id}`, data)
export const deletePurchaseOrder = (id) => api.delete(`/purchase-orders/${id}`)
export const orderToStockin = (id) => api.post(`/purchase-orders/${id}/stockin`)

// 采购入库
export const getPurchaseStockins = (params) => api.get('/purchase-stockins', { params })
export const createPurchaseStockin = (data) => api.post('/purchase-stockins', data)
export const getPurchaseStockin = (id) => api.get(`/purchase-stockins/${id}`)
export const updatePurchaseStockin = (id, data) => api.put(`/purchase-stockins/${id}`, data)
export const deletePurchaseStockin = (id) => api.delete(`/purchase-stockins/${id}`)
export const confirmPurchaseStockin = (id) => api.post(`/purchase-stockins/${id}/confirm`)

// 采购退货
export const getPurchaseReturns = (params) => api.get('/purchase-returns', { params })
export const createPurchaseReturn = (data) => api.post('/purchase-returns', data)
export const getPurchaseReturn = (id) => api.get(`/purchase-returns/${id}`)
export const updatePurchaseReturn = (id, data) => api.put(`/purchase-returns/${id}`, data)
export const deletePurchaseReturn = (id) => api.delete(`/purchase-returns/${id}`)
export const confirmPurchaseReturn = (id) => api.post(`/purchase-returns/${id}/confirm`)

// 销售
export const getSalesOrders = (params) => api.get('/sales-orders', { params })
export const createSalesOrder = (data) => api.post('/sales-orders', data)
export const getSalesOrder = (id) => api.get(`/sales-orders/${id}`)
export const updateSalesOrder = (id, data) => api.put(`/sales-orders/${id}`, data)
export const deleteSalesOrder = (id) => api.delete(`/sales-orders/${id}`)
export const orderToStockout = (id) => api.post(`/sales-orders/${id}/stockout`)

// 销售出库
export const getSalesStockouts = (params) => api.get('/sales-stockouts', { params })
export const createSalesStockout = (data) => api.post('/sales-stockouts', data)
export const getSalesStockout = (id) => api.get(`/sales-stockouts/${id}`)
export const updateSalesStockout = (id, data) => api.put(`/sales-stockouts/${id}`, data)
export const deleteSalesStockout = (id) => api.delete(`/sales-stockouts/${id}`)
export const confirmSalesStockout = (id) => api.post(`/sales-stockouts/${id}/confirm`)

// 销售退货
export const getSalesReturns = (params) => api.get('/sales-returns', { params })
export const createSalesReturn = (data) => api.post('/sales-returns', data)
export const getSalesReturn = (id) => api.get(`/sales-returns/${id}`)
export const updateSalesReturn = (id, data) => api.put(`/sales-returns/${id}`, data)
export const deleteSalesReturn = (id) => api.delete(`/sales-returns/${id}`)
export const confirmSalesReturn = (id) => api.post(`/sales-returns/${id}/confirm`)

// 库存
export const getInventory = (params) => api.get('/inventory', { params })
export const getInventoryAlerts = () => api.get('/inventory/alerts')
export const getReorderSuggestions = () => api.get('/inventory/reorder-suggestions')

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

// 银行对账
export const getBankStatements = (params) => api.get('/bank-statements', { params })
export const createBankStatement = (data) => api.post('/bank-statements', data)
export const autoMatchBankStatements = () => api.post('/bank-statements/auto-match')
export const getBankSummary = () => api.get('/bank-statements/summary')

// 报表
export const getSalesReport = (params) => api.get('/reports/sales', { params })
export const getPurchaseReport = (params) => api.get('/reports/purchase', { params })
export const getInventoryReport = (params) => api.get('/reports/inventory', { params })
export const getProfitReport = (params) => api.get('/reports/profit', { params })
export const exportSalesReport = (params) => api.get('/reports/export/sales', { params, responseType: 'blob' })
export const exportInventoryReport = () => api.get('/reports/export/inventory', { responseType: 'blob' })
export const exportFinanceReport = (params) => api.get('/reports/export/finance', { params, responseType: 'blob' })
export const getTrendReport = (params) => api.get('/reports/trend', { params })

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
export const smartPriceQuery = (params) => api.get('/customer-prices/price-query', { params })
export const batchPriceQuery = (params) => api.get('/customer-prices/batch-query', { params })

// 发票管理
export const getInvoices = (params) => api.get('/invoices', { params })
export const getInvoice = (id) => api.get(`/invoices/${id}`)
export const createInvoice = (data) => api.post('/invoices', data)
export const updateInvoice = (id, data) => api.put(`/invoices/${id}`, data)
export const deleteInvoice = (id) => api.delete(`/invoices/${id}`)
export const certifyInvoice = (id) => api.put(`/invoices/${id}/certify`)
export const voidInvoice = (id) => api.put(`/invoices/${id}/void`)

// 供应商对账
export const getSupplierReconSummary = () => api.get('/supplier-recon/summary')
export const getSupplierStatement = (params) => api.get('/supplier-recon/statement', { params })

// 系统
export const getEmployees = (params) => api.get('/employees', { params })
export const getCategories = (params) => api.get('/categories', { params })
export const getOperationLogs = (params) => api.get('/system/logs', { params })

// 打印模板
export const getPrintTemplates = (params) => api.get('/print-templates', { params })
export const getPrintTemplate = (id) => api.get(`/print-templates/${id}`)
export const createPrintTemplate = (data) => api.post('/print-templates', data)
export const updatePrintTemplate = (id, data) => api.put(`/print-templates/${id}`, data)
export const deletePrintTemplate = (id) => api.delete(`/print-templates/${id}`)
export const getPrintTemplateTypes = () => api.get('/print-templates/types')
export const previewPrint = (templateId, docType, docId) => api.get(`/print-templates/${templateId}/preview/${docType}/${docId}`)

// 数据导入
export const getImportTypes = () => api.get('/data-import/types')
export const downloadImportTemplate = (type) => api.get(`/data-import/template/${type}`, { responseType: 'blob' })
export const previewImport = (type, file) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post(`/data-import/preview/${type}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const executeImport = (type, file) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post(`/data-import/execute/${type}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
}

// 批次管理
export const getBatches = (params) => api.get('/batches', { params })
export const createBatch = (data) => api.post('/batches', data)
export const updateBatch = (id, data) => api.put(`/batches/${id}`, data)
export const getExpiringBatches = (days = 30) => api.get('/batches/expiring', { params: { days } })
export const getFifoBatches = (params) => api.get(`/batches/fifo/${params.product_id}`, { params })
export const deductBatchStock = (params) => api.post('/batches/deduct', null, { params })
