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
    redirect: '/home',
    children: [
      { path: 'home', name: 'Home', component: () => import('../views/Home.vue') },
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { roles: ['admin'] } },
      { path: 'customers', name: 'Customers', component: () => import('../views/Customers.vue') },
      { path: 'performance', name: 'Performance', component: () => import('../views/Performance.vue') },
      { path: 'inventory', name: 'Inventory', component: () => import('../views/Inventory.vue') },
      { path: 'tools', name: 'Tools', component: () => import('../views/Tools.vue') },
      { path: 'todo', name: 'Todo', component: () => import('../views/Todo.vue') },
      { path: 'visit', name: 'Visit', component: () => import('../views/Visit.vue') },
      { path: 'checkin', name: 'CheckIn', component: () => import('../views/CheckIn.vue') },
      { path: 'order', name: 'Order', component: () => import('../views/Order.vue') },
      { path: 'print', name: 'Print', component: () => import('../views/Print.vue') },
      { path: 'receivables', name: 'Receivables', component: () => import('../views/Receivables.vue') },
      { path: 'payments', name: 'Payments', component: () => import('../views/Payments.vue') },
      { path: 'account', name: 'Account', component: () => import('../views/Account.vue') },
      { path: 'transfer', name: 'Transfer', component: () => import('../views/Transfer.vue') },
      { path: 'check', name: 'Check', component: () => import('../views/Check.vue') },
      { path: 'loss-report', name: 'LossReport', component: () => import('../views/LossReport.vue') },
      { path: 'approve', name: 'Approve', component: () => import('../views/Approve.vue') },
      { path: 'employee', name: 'Employee', component: () => import('../views/Employee.vue'), meta: { roles: ['admin'] } },
      { path: 'supplier', name: 'Supplier', component: () => import('../views/Supplier.vue') },
      { path: 'purchase', name: 'Purchase', component: () => import('../views/Purchase.vue') },
      { path: 'settings', name: 'Settings', component: () => import('../views/Settings.vue'), meta: { roles: ['admin'] } },
      { path: 'roles', name: 'Roles', component: () => import('../views/Roles.vue'), meta: { roles: ['admin'] } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.path !== '/login' && !token) {
    next('/login')
  } else if (to.path === '/login') {
    next()
  } else {
    next()
  }
})

export default router