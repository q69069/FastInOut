/**
 * 模块偏好管理 - H5版，与实际路由完全对应
 */

const PREF_KEY = 'home_module_prefs'

// 与 h5/src/router/index.js 实际路由一一对应
export const MODULE_META = {
  sales:              { label: '销售开单',    path: '/order',               icon: 'orders-o',        color: '#409EFF', group: '业务' },
  purchases:          { label: '采购开单',    path: '/purchase',           icon: 'shopping-cart-o', color: '#67C23A', group: '业务' },
  inventory:          { label: '库存查询',    path: '/inventory',           icon: 'cluster-o',        color: '#E6A23C', group: '仓储' },
  customers:          { label: '客户管理',    path: '/customers',           icon: 'friends-o',        color: '#F56C6C', group: '档案' },
  supplier:           { label: '供应商管理',  path: '/supplier',            icon: 'shop-o',          color: '#909399', group: '档案' },
  payments:           { label: '收支管理',    path: '/payments',            icon: 'balance-o',        color: '#07c160', group: '财务' },
  reports:            { label: '报表统计',    path: '/reports',             icon: 'chart-trending-o', color: '#ff9800', group: '报表' },
  settlement:        { label: '交账管理',    path: '/settlement',          icon: 'cash-back-record-o', color: '#3f51b5', group: '业务' },
  check:              { label: '库存盘点',    path: '/check',              icon: 'search',           color: '#795548', group: '仓储' },
  vehicle_load:       { label: '装车管理',    path: '/vehicle-load',        icon: 'logistics',        color: '#607d8b', group: '车销' },
  vehicle_sales:      { label: '车销开单',    path: '/vehicle-sales',        icon: 'shopping-cart-o', color: '#e040fb', group: '业务' },
  approve:           { label: '审核中心',    path: '/approve',             icon: 'passed',           color: '#ab47bc', group: '审核' },
  expense:            { label: '费用报销',    path: '/expense',             icon: 'coupon-o',         color: '#9c27b0', group: '财务' },
  transfer:           { label: '库存调拨',    path: '/transfer',           icon: 'exchange',         color: '#26a69a', group: '仓储' },
  loss_report:        { label: '报损报溢',    path: '/loss-report',         icon: 'warning-o',        color: '#8d6e63', group: '仓储' },
  brand:              { label: '品牌管理',    path: '/brand',              icon: 'flag-o',           color: '#ff7043', group: '档案' },
  channel:            { label: '渠道管理',    path: '/channel',            icon: 'cluster-o',        color: '#26a69a', group: '档案' },
  customer_level:    { label: '客户等级',    path: '/customer-level',     icon: 'user-o',           color: '#42a5f5', group: '档案' },
  promotion:          { label: '促销管理',    path: '/promotion',          icon: 'coupon-o',         color: '#ab47bc', group: '促销' },
}

export const ALL_MODULE_KEYS = Object.keys(MODULE_META)

export function getModuleOrder() {
  try {
    const raw = localStorage.getItem(PREF_KEY)
    if (!raw) return Object.keys(MODULE_META)
    const prefs = JSON.parse(raw)
    const order = prefs.order || Object.keys(MODULE_META)
    const count = prefs.usageCount || {}
    return [...order].sort((a, b) => (count[b] || 0) - (count[a] || 0))
  } catch {
    return Object.keys(MODULE_META)
  }
}

export function recordModuleUsage(key) {
  try {
    const raw = localStorage.getItem(PREF_KEY)
    const prefs = raw ? JSON.parse(raw) : { order: Object.keys(MODULE_META), usageCount: {} }
    prefs.usageCount[key] = (prefs.usageCount[key] || 0) + 1
    localStorage.setItem(PREF_KEY, JSON.stringify(prefs))
  } catch {}
}

export function saveModuleOrder(order) {
  try {
    const raw = localStorage.getItem(PREF_KEY)
    const prefs = raw ? JSON.parse(raw) : { order: Object.keys(MODULE_META), usageCount: {} }
    prefs.order = order
    localStorage.setItem(PREF_KEY, JSON.stringify(prefs))
  } catch {}
}
