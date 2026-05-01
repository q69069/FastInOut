import { createRouter, createWebHistory } from 'vue-router'

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
        meta: { title: '首页' }
      },
      // 档案
      {
        path: 'products',
        name: 'Products',
        component: () => import('../views/products/Index.vue'),
        meta: { title: '商品管理' }
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('../views/customers/Index.vue'),
        meta: { title: '客户管理' }
      },
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('../views/suppliers/Index.vue'),
        meta: { title: '供应商管理' }
      },
      // 采购
      {
        path: 'purchases',
        name: 'Purchases',
        component: () => import('../views/purchases/Index.vue'),
        meta: { title: '采购订单' }
      },
      {
        path: 'purchase-returns',
        name: 'PurchaseReturns',
        component: () => import('../views/purchases/Returns.vue'),
        meta: { title: '采购退货' }
      },
      // 销售
      {
        path: 'sales',
        name: 'Sales',
        component: () => import('../views/sales/Index.vue'),
        meta: { title: '销售订单' }
      },
      {
        path: 'sales-returns',
        name: 'SalesReturns',
        component: () => import('../views/sales/Returns.vue'),
        meta: { title: '销售退货' }
      },
      // 库存
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('../views/inventory/Index.vue'),
        meta: { title: '库存查询' }
      },
      {
        path: 'transfers',
        name: 'Transfers',
        component: () => import('../views/inventory/Transfers.vue'),
        meta: { title: '库存调拨' }
      },
      {
        path: 'warehouses',
        name: 'Warehouses',
        component: () => import('../views/warehouses/Index.vue'),
        meta: { title: '仓库管理' }
      },
      // 财务
      {
        path: 'finance',
        name: 'Finance',
        component: () => import('../views/finance/Index.vue'),
        meta: { title: '财务管理' }
      },
      // 报表
      {
        path: 'reports/profit',
        name: 'ProfitReport',
        component: () => import('../views/reports/Profit.vue'),
        meta: { title: '利润统计' }
      },
      {
        path: 'reports/inventory',
        name: 'InventoryReport',
        component: () => import('../views/reports/Inventory.vue'),
        meta: { title: '库存汇总' }
      },
      {
        path: 'reports/sales-ranking',
        name: 'SalesRanking',
        component: () => import('../views/reports/SalesRanking.vue'),
        meta: { title: '销售排行' }
      },
      // 促销
      {
        path: 'promotions',
        name: 'Promotions',
        component: () => import('../views/promotions/Index.vue'),
        meta: { title: '促销方案' }
      },
      // 系统
      {
        path: 'units',
        name: 'Units',
        component: () => import('../views/units/Index.vue'),
        meta: { title: '单位管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
