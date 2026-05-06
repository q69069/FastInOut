/**
 * 模块偏好管理 - PC版，与实际路由完全对应
 * 图标全部使用 @element-plus/icons-vue 中存在的名称
 */

const PREF_KEY = 'pc_home_module_prefs'

const DEFAULT_ORDER = [
  'sales', 'purchases', 'inventory', 'customers', 'suppliers',
  'finance', 'expenses', 'reports', 'settlements',
  'stocktaking', 'vehicle_loads', 'sales_deliveries', 'purchase_receipts',
  'brands', 'channels', 'customer_levels', 'promotions', 'damage_reports',
]

// 与 pc/src/router/index.js 完全对齐的路径，图标全部有效
export const MODULE_META = {
  sales:              { label: '销售订单',    path: '/sales',              icon: 'Sell',         color: '#409EFF', group: '业务' },
  purchases:          { label: '采购订单',    path: '/purchases',          icon: 'ShoppingBag',     color: '#67C23A', group: '业务' },
  inventory:          { label: '库存查询',    path: '/inventory',          icon: 'Box',          color: '#E6A23C', group: '仓储' },
  customers:          { label: '客户管理',    path: '/customers',          icon: 'User',         color: '#F56C6C', group: '档案' },
  suppliers:          { label: '供应商管理',  path: '/suppliers',          icon: 'Shop',         color: '#909399', group: '档案' },
  finance:            { label: '收支管理',    path: '/finance',            icon: 'Money',        color: '#07c160', group: '财务' },
  expenses:           { label: '费用报销',    path: '/expenses',           icon: 'Coin',         color: '#9c27b0', group: '财务' },
  reports:            { label: '报表统计',    path: '/reports/profit',     icon: 'DataAnalysis', color: '#ff9800', group: '报表' },
  settlements:        { label: '交账管理',    path: '/settlements',        icon: 'Wallet',       color: '#3f51b5', group: '业务' },
  stocktaking:        { label: '盘点管理',    path: '/stocktaking',        icon: 'Search',       color: '#795548', group: '仓储' },
  vehicle_loads:      { label: '装车管理',    path: '/vehicle-loads',      icon: 'Van',          color: '#607d8b', group: '车销' },
  sales_deliveries:   { label: '销售单管理',  path: '/sales-deliveries',   icon: 'Sell',         color: '#e040fb', group: '业务' },
  purchase_receipts:  { label: '采购入库',    path: '/purchase-receipts',  icon: 'ShoppingBag',     color: '#00acc1', group: '业务' },
  brands:             { label: '品牌管理',    path: '/brands',             icon: 'PriceTag',        color: '#ff7043', group: '档案' },
  channels:           { label: '渠道管理',    path: '/channels',           icon: 'Connection',   color: '#26a69a', group: '档案' },
  customer_levels:    { label: '客户等级',    path: '/customer-levels',    icon: 'User',         color: '#42a5f5', group: '档案' },
  promotions:         { label: '促销方案',    path: '/promotions',         icon: 'Tickets',      color: '#ab47bc', group: '促销' },
  damage_reports:     { label: '报损管理',    path: '/damage-reports',     icon: 'Warning',      color: '#8d6e63', group: '仓储' },
}

export const ALL_MODULE_KEYS = Object.keys(MODULE_META)

export function getModuleOrder() {
  try {
    const raw = localStorage.getItem(PREF_KEY)
    if (!raw) return [...DEFAULT_ORDER]
    const prefs = JSON.parse(raw)
    const order = prefs.order || DEFAULT_ORDER
    const count = prefs.usageCount || {}
    return [...order].sort((a, b) => (count[b] || 0) - (count[a] || 0))
  } catch {
    return [...DEFAULT_ORDER]
  }
}

export function recordModuleUsage(key) {
  try {
    const raw = localStorage.getItem(PREF_KEY)
    const prefs = raw ? JSON.parse(raw) : { order: [...DEFAULT_ORDER], usageCount: {} }
    prefs.usageCount[key] = (prefs.usageCount[key] || 0) + 1
    localStorage.setItem(PREF_KEY, JSON.stringify(prefs))
  } catch {}
}

export function saveModuleOrder(order) {
  try {
    const raw = localStorage.getItem(PREF_KEY)
    const prefs = raw ? JSON.parse(raw) : { order: [...DEFAULT_ORDER], usageCount: {} }
    prefs.order = order
    localStorage.setItem(PREF_KEY, JSON.stringify(prefs))
  } catch {}
}
