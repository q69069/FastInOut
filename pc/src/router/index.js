import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '首页', moduleKey: 'home' }
      },
      // 档案
      {
        path: 'products',
        name: 'Products',
        component: () => import('../views/products/Index.vue'),
        meta: { title: '商品管理', moduleKey: 'products' }
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('../views/customers/Index.vue'),
        meta: { title: '客户管理', moduleKey: 'customers' }
      },
      {
        path: 'customer-prices',
        name: 'CustomerPrices',
        component: () => import('../views/customers/PriceLevel.vue'),
        meta: { title: '客户价格等级', moduleKey: 'customers' }
      },
      {
        path: 'customers/crm',
        name: 'Crm',
        component: () => import('../views/customers/Crm.vue'),
        meta: { title: '客户关系管理', moduleKey: 'customers' }
      },
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('../views/suppliers/Index.vue'),
        meta: { title: '供应商管理', moduleKey: 'suppliers' }
      },
      {
        path: 'supplier-reconciliation',
        name: 'SupplierReconciliation',
        component: () => import('../views/suppliers/Reconciliation.vue'),
        meta: { title: '供应商对账', moduleKey: 'suppliers' }
      },
      // 采购
      {
        path: 'purchases',
        name: 'Purchases',
        component: () => import('../views/purchases/Index.vue'),
        meta: { title: '采购订单', moduleKey: 'purchases' }
      },
      {
        path: 'purchase-returns',
        name: 'PurchaseReturns',
        component: () => import('../views/purchases/Returns.vue'),
        meta: { title: '采购退货', moduleKey: 'purchases' }
      },
      // 销售
      {
        path: 'sales',
        name: 'Sales',
        component: () => import('../views/sales/Index.vue'),
        meta: { title: '销售订单', moduleKey: 'sales' }
      },
      {
        path: 'sales-returns',
        name: 'SalesReturns',
        component: () => import('../views/sales/Returns.vue'),
        meta: { title: '销售退货', moduleKey: 'sales' }
      },
      {
        path: 'salesmen',
        name: 'Salesmen',
        component: () => import('../views/salesmen/Index.vue'),
        meta: { title: '业务员管理', moduleKey: 'sales' }
      },
      // 库存
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('../views/inventory/Index.vue'),
        meta: { title: '库存查询', moduleKey: 'inventory' }
      },
      {
        path: 'transfers',
        name: 'Transfers',
        component: () => import('../views/inventory/Transfers.vue'),
        meta: { title: '库存调拨', moduleKey: 'inventory' }
      },
      {
        path: 'warehouses',
        name: 'Warehouses',
        component: () => import('../views/warehouses/Index.vue'),
        meta: { title: '仓库管理', moduleKey: 'warehouses' }
      },
      {
        path: 'batches',
        name: 'Batches',
        component: () => import('../views/batches/Index.vue'),
        meta: { title: '批次管理', moduleKey: 'batches' }
      },
      // 财务
      {
        path: 'finance',
        name: 'Finance',
        component: () => import('../views/finance/Index.vue'),
        meta: { title: '财务管理', moduleKey: 'finance' }
      },
      {
        path: 'bank-reconciliation',
        name: 'BankReconciliation',
        component: () => import('../views/finance/BankReconciliation.vue'),
        meta: { title: '银行对账', moduleKey: 'finance' }
      },
      {
        path: 'invoices',
        name: 'Invoices',
        component: () => import('../views/finance/Invoices.vue'),
        meta: { title: '发票管理', moduleKey: 'finance' }
      },
      // 报表
      {
        path: 'reports/profit',
        name: 'ProfitReport',
        component: () => import('../views/reports/Profit.vue'),
        meta: { title: '利润统计', moduleKey: 'reports' }
      },
      {
        path: 'reports/inventory',
        name: 'InventoryReport',
        component: () => import('../views/reports/Inventory.vue'),
        meta: { title: '库存汇总', moduleKey: 'reports' }
      },
      {
        path: 'reports/sales-ranking',
        name: 'SalesRanking',
        component: () => import('../views/reports/SalesRanking.vue'),
        meta: { title: '销售排行', moduleKey: 'reports' }
      },
      {
        path: 'reports/trend',
        name: 'TrendReport',
        component: () => import('../views/reports/Trend.vue'),
        meta: { title: '趋势图', moduleKey: 'reports' }
      },
      // 促销
      {
        path: 'promotions',
        name: 'Promotions',
        component: () => import('../views/promotions/Index.vue'),
        meta: { title: '促销方案', moduleKey: 'promotions' }
      },
      // 系统
      {
        path: 'units',
        name: 'Units',
        component: () => import('../views/units/Index.vue'),
        meta: { title: '单位管理', moduleKey: 'products' }
      },
      {
        path: 'system/roles',
        name: 'Roles',
        component: () => import('../views/system/Roles.vue'),
        meta: { title: '角色管理', moduleKey: 'roles' }
      },
      {
        path: 'system/backup',
        name: 'Backup',
        component: () => import('../views/system/Backup.vue'),
        meta: { title: '数据备份', moduleKey: 'system' }
      },
      {
        path: 'system/print-templates',
        name: 'PrintTemplates',
        component: () => import('../views/system/PrintTemplates.vue'),
        meta: { title: '打印模板', moduleKey: 'system' }
      },
      {
        path: 'system/data-import',
        name: 'DataImport',
        component: () => import('../views/system/DataImport.vue'),
        meta: { title: '数据导入', moduleKey: 'system' }
      },
      {
        path: 'system/logs',
        name: 'OperationLogs',
        component: () => import('../views/system/Logs.vue'),
        meta: { title: '操作日志', moduleKey: 'system' }
      },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

import { useAuthStore } from '../stores/auth'

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else if (token) {
    const authStore = useAuthStore()
    if (!authStore.user) {
      await authStore.fetchUser()
    }
    // 模块权限检查
    const moduleKey = to.meta.moduleKey
    if (moduleKey && !authStore.isAdmin && !authStore.hasModule(moduleKey)) {
      ElMessage.error('无权访问此页面')
      next('/dashboard')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
