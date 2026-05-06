/**
 * 模块偏好管理 - 记忆用户首页模块选择，按使用频率智能排序
 */

const PREF_KEY = 'home_module_prefs'

const DEFAULT_ORDER = [
  'sales', 'purchases', 'inventory', 'customers', 'suppliers',
  'finance', 'expense', 'products', 'reports', 'settlements',
]

export const MODULE_META = {
  sales:       { label: '销售开单', path: '/sales',       icon: 'Sell',         color: '#409EFF', group: '业务' },
  purchases:   { label: '采购开单', path: '/purchases',   icon: 'ShoppingCart', color: '#67C23A', group: '业务' },
  inventory:   { label: '库存查询', path: '/inventory',   icon: 'Box',          color: '#E6A23C', group: '仓储' },
  customers:   { label: '客户管理', path: '/customers',    icon: 'User',         color: '#F56C6C', group: '档案' },
  suppliers:   { label: '供应商管理', path: '/suppliers', icon: 'Shop',         color: '#909399', group: '档案' },
  finance:     { label: '收支管理', path: '/finance',      icon: 'Money',        color: '#07c160', group: '财务' },
  expense:     { label: '费用报销', path: '/expense',      icon: 'Finance',      color: '#9c27b0', group: '财务' },
  products:    { label: '商品管理', path: '/products',     icon: 'Goods',        color: '#00bcd4', group: '档案' },
  reports:     { label: '报表统计', path: '/reports/profit', icon: 'DataAnalysis', color: '#ff9800', group: '报表' },
  settlements: { label: '交账管理', path: '/settlements',  icon: 'Wallet',       color: '#3f51b5', group: '业务' },
  stocktaking: { label: '盘点管理', path: '/stocktaking',  icon: 'Search',       color: '#795548', group: '仓储' },
  vehicle_load:{ label: '装车管理', path: '/vehicle_load', icon: 'Van',          color: '#607d8b', group: '车销' },
}

export const ALL_MODULE_KEYS = Object.keys(MODULE_META)

export function getModuleOrder() {
  try {
    const raw = localStorage.getItem(PREF_KEY)
    if (!raw) return [...DEFAULT_ORDER]
    const prefs = JSON.parse(raw)
    const order = prefs.order || DEFAULT_ORDER
    const count = prefs.usageCount || {}
    const sorted = [...order].sort((a, b) => (count[b] || 0) - (count[a] || 0))
    return sorted
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
