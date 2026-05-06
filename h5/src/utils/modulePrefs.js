/**
 * 模块偏好管理 - 记忆用户首页模块选择，按使用频率智能排序
 * 存储结构: { order: string[], usageCount: Record<string, number> }
 */

const PREF_KEY = 'home_module_prefs'

const DEFAULT_ORDER = [
  'sales',       // 销售开单
  'purchases',   // 采购开单
  'inventory',   // 库存查询
  'customers',   // 客户管理
  'suppliers',   // 供应商管理
  'finance',     // 收支管理
  'reports',     // 报表统计
  'settlements', // 交账管理
  'stocktaking', // 盘点管理
  'vehicle_load',// 装车管理
]

// 各模块的定义信息 - path与H5路由一一对应
export const MODULE_META = {
  sales:       { label: '销售开单',   path: '/order',           icon: 'orders-o',     color: '#409EFF', group: '业务' },
  purchases:   { label: '采购开单',   path: '/purchase',         icon: 'shopping-cart-o', color: '#67C23A', group: '业务' },
  inventory:   { label: '库存查询',   path: '/inventory',         icon: 'cluster-o',    color: '#E6A23C', group: '仓储' },
  customers:   { label: '客户管理',   path: '/customers',         icon: 'friends-o',     color: '#F56C6C', group: '档案' },
  suppliers:   { label: '供应商管理', path: '/supplier',          icon: 'shop-o',       color: '#909399', group: '档案' },
  finance:     { label: '收支管理',   path: '/payments',          icon: 'balance-o',     color: '#07c160', group: '财务' },
  reports:     { label: '报表统计',   path: '/reports',           icon: 'chart-trending-o', color: '#ff9800', group: '报表' },
  settlements: { label: '交账管理',   path: '/settlement',        icon: 'cash-back-record-o', color: '#3f51b5', group: '业务' },
  stocktaking: { label: '盘点管理',   path: '/check',             icon: 'search',        color: '#795548', group: '仓储' },
  vehicle_load:{ label: '装车管理',   path: '/vehicle-load',      icon: 'logistics',     color: '#607d8b', group: '车销' },
}

export const ALL_MODULE_KEYS = Object.keys(MODULE_META)

/**
 * 获取用户当前的模块顺序（记忆+智能排序）
 * 新用户返回DEFAULT_ORDER，常用模块排在前面
 */
export function getModuleOrder() {
  try {
    const raw = localStorage.getItem(PREF_KEY)
    if (!raw) return [...DEFAULT_ORDER]
    const prefs = JSON.parse(raw)
    const order = prefs.order || DEFAULT_ORDER
    const count = prefs.usageCount || {}

    // 按使用频率排序，频率相同则保持用户自定义顺序
    const sorted = [...order].sort((a, b) => (count[b] || 0) - (count[a] || 0))
    return sorted
  } catch {
    return [...DEFAULT_ORDER]
  }
}

/**
 * 记录模块被点击使用
 */
export function recordModuleUsage(key) {
  try {
    const raw = localStorage.getItem(PREF_KEY)
    const prefs = raw ? JSON.parse(raw) : { order: [...DEFAULT_ORDER], usageCount: {} }
    prefs.usageCount[key] = (prefs.usageCount[key] || 0) + 1
    localStorage.setItem(PREF_KEY, JSON.stringify(prefs))
  } catch {}
}

/**
 * 保存用户自定义模块顺序
 */
export function saveModuleOrder(order) {
  try {
    const raw = localStorage.getItem(PREF_KEY)
    const prefs = raw ? JSON.parse(raw) : { order: [...DEFAULT_ORDER], usageCount: {} }
    prefs.order = order
    localStorage.setItem(PREF_KEY, JSON.stringify(prefs))
  } catch {}
}
