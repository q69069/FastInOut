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
export const deleteEmployee = (id) => api.delete(`/employees/${id}`)
export const getSuppliers = (params) => api.get('/suppliers', { params })
export const createPurchase = (data) => api.post('/purchases/purchase-orders', data)
export const getDashboard = () => api.get('/reports/dashboard')
export const getRoles = () => api.get('/roles')
export const updateRole = (data) => api.put(`/roles/${data.id}`, data)
export const getCompanySettings = () => api.get('/company')
export const updateCompanySettings = (data) => api.put('/company', data)
export const backupData = () => api.post('/backup')

// ========== 库存相关（扩展） ==========
export const getInventoryFlow = (params) => api.get('/inventory/flow', { params })
export const getInventoryAlerts = (params) => api.get('/inventory/alerts', { params })
export const getInventorySummary = () => api.get('/inventory/summary')
export const getSlowMoving = (days) => api.get('/inventory/slow-moving', { params: { days } })
export const getReorderSuggestions = () => api.get('/inventory/reorder-suggestions')

// 盘点
export const getStocktaking = (params) => api.get('/inventory/checks', { params })
export const createStocktaking = (data) => api.post('/inventory/checks', data)
export const getStocktakingDetail = (id) => api.get(`/inventory/checks/${id}`)
export const updateStocktaking = (id, data) => api.put(`/inventory/checks/${id}`, data)
export const auditStocktaking = (id) => api.post(`/inventory/checks/${id}/confirm`)
export const voidStocktaking = (id) => api.delete(`/inventory/checks/${id}`)

// 调拨
export const getTransfers = (params) => api.get('/inventory/transfers', { params })
export const getTransfer = (id) => api.get(`/inventory/transfers/${id}`)
export const confirmTransfer = (id) => api.post(`/inventory/transfers/${id}/confirm`)
export const cancelTransfer = (id) => api.delete(`/inventory/transfers/${id}`)

// 报损报溢
export const getOtherLog = (params) => api.get('/inventory/other-log', { params })
export const createOtherIn = (data) => api.post('/inventory/other-in', data)
export const createOtherOut = (data) => api.post('/inventory/other-out', data)

// ========== 采购相关 ==========
export const getPurchaseOrders = (params) => api.get('/purchase-orders', { params })
export const createPurchaseOrder = (data) => api.post('/purchase-orders', data)
export const getPurchaseOrder = (id) => api.get(`/purchase-orders/${id}`)
export const updatePurchaseOrder = (id, data) => api.put(`/purchase-orders/${id}`, data)
export const orderToStockin = (id) => api.post(`/purchase-orders/${id}/stockin`)

export const getPurchaseStockins = (params) => api.get('/purchase-stockins', { params })
export const createPurchaseStockin = (data) => api.post('/purchase-stockins', data)
export const getPurchaseStockin = (id) => api.get(`/purchase-stockins/${id}`)
export const updatePurchaseStockin = (id, data) => api.put(`/purchase-stockins/${id}`, data)
export const deletePurchaseStockin = (id) => api.delete(`/purchase-stockins/${id}`)
export const confirmPurchaseStockin = (id) => api.post(`/purchase-stockins/${id}/confirm`)

export const getPurchaseReturns = (params) => api.get('/purchase-returns', { params })
export const createPurchaseReturn = (data) => api.post('/purchase-returns', data)
export const getPurchaseReturn = (id) => api.get(`/purchase-returns/${id}`)
export const confirmPurchaseReturn = (id) => api.post(`/purchase-returns/${id}/confirm`)

// ========== 财务+费用 ==========
export const getReceipts = (params) => api.get('/finance/receipts', { params })
export const createReceipt = (data) => api.post('/finance/receipts', data)
export const getPaymentRecords = (params) => api.get('/finance/payments', { params })
export const createPayment = (data) => api.post('/finance/payments', data)
export const getFinanceFlow = (params) => api.get('/finance/flow', { params })

export const getExpenseCategories = () => api.get('/expense-categories')
export const createExpenseCategory = (data) => api.post('/expense-categories', data)
export const getExpenses = (params) => api.get('/expenses', { params })
export const createExpense = (data) => api.post('/expenses', data)
export const getExpense = (id) => api.get(`/expenses/${id}`)
export const approveExpense = (id) => api.post(`/expenses/${id}/approve`)
export const rejectExpense = (id) => api.post(`/expenses/${id}/reject`)

// ========== 报表 ==========
export const getSalesReport = (params) => api.get('/reports/sales', { params })
export const getPurchaseReport = (params) => api.get('/reports/purchase', { params })
export const getTrendReport = (params) => api.get('/reports/trend', { params })
export const getProfitReport = (params) => api.get('/reports/profit', { params })
export const getSalesDetailReport = (params) => api.get('/reports/sales-detail', { params })
export const getCommissionReport = (params) => api.get('/reports/commission', { params })

// ========== 客户+供应商 ==========
export const createCustomer = (data) => api.post('/customers', data)
export const getCustomer = (id) => api.get(`/customers/${id}`)
export const updateCustomer = (id, data) => api.put(`/customers/${id}`, data)
export const getCustomerContacts = (params) => api.get('/customer-contacts', { params })
export const createCustomerContact = (data) => api.post('/customer-contacts', data)
export const deleteCustomerContact = (id) => api.delete(`/customer-contacts/${id}`)
export const getCustomerPrices = (params) => api.get('/customer-prices', { params })
export const createCustomerPrice = (data) => api.post('/customer-prices', data)
export const queryCustomerPrice = (params) => api.get('/customer-prices/query', { params })

export const createSupplier = (data) => api.post('/suppliers', data)
export const getSupplier = (id) => api.get(`/suppliers/${id}`)
export const updateSupplier = (id, data) => api.put(`/suppliers/${id}`, data)
export const deleteSupplier = (id) => api.delete(`/suppliers/${id}`)
export const getSupplierReconSummary = () => api.get('/supplier-recon/summary')
export const getSupplierStatement = (params) => api.get('/supplier-recon/statement', { params })

// ========== 员工+角色 ==========
export const createRole = (data) => api.post('/roles', data)
export const deleteRole = (id) => api.delete(`/roles/${id}`)
export const assignRole = (data) => api.post('/roles/assign', data)

// ========== 消息+系统 ==========
export const getMessages = (params) => api.get('/messages', { params })
export const getUnreadCount = () => api.get('/messages/unread-count')
export const markMessageRead = (id) => api.put(`/messages/${id}/read`)
export const markAllRead = () => api.put('/messages/read-all')
export const getOperationLogs = (params) => api.get('/system/logs', { params })

// ========== 发票+促销 ==========
export const getInvoices = (params) => api.get('/invoices', { params })
export const createInvoice = (data) => api.post('/invoices', data)
export const getInvoice = (id) => api.get(`/invoices/${id}`)
export const voidInvoice = (id) => api.put(`/invoices/${id}/void`)
export const certifyInvoice = (id) => api.put(`/invoices/${id}/certify`)

export const getPromotions = (params) => api.get('/promotions', { params })
export const createPromotion = (data) => api.post('/promotions', data)
export const updatePromotion = (id, data) => api.put(`/promotions/${id}`, data)
export const deletePromotion = (id) => api.delete(`/promotions/${id}`)

// ========== 往来账 ==========
export const getReceivablesSummary = () => api.get('/account-ledger/receivables')
export const getReceivableDetail = (customerId) => api.get(`/account-ledger/receivables/${customerId}`)
export const getPayablesSummary = () => api.get('/account-ledger/payables')
export const getPayableDetail = (supplierId) => api.get(`/account-ledger/payables/${supplierId}`)

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