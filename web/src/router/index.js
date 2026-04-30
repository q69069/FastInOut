import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../../../../pc/src/views/Login.vue')
  },
  {
    path: '/',
    component: () => import('../../../../pc/src/views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../../../../pc/src/views/Dashboard.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('../../../../pc/src/views/products/Index.vue'),
        meta: { title: '商品管理' }
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('../../../../pc/src/views/customers/Index.vue'),
        meta: { title: '客户管理' }
      },
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('../../../../pc/src/views/suppliers/Index.vue'),
        meta: { title: '供应商管理' }
      },
      {
        path: 'purchases',
        name: 'Purchases',
        component: () => import('../../../../pc/src/views/purchases/Index.vue'),
        meta: { title: '采购订单' }
      },
      {
        path: 'sales',
        name: 'Sales',
        component: () => import('../../../../pc/src/views/sales/Index.vue'),
        meta: { title: '销售订单' }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('../../../../pc/src/views/inventory/Index.vue'),
        meta: { title: '库存查询' }
      },
      {
        path: 'finance',
        name: 'Finance',
        component: () => import('../../../../pc/src/views/finance/Index.vue'),
        meta: { title: '财务管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
