import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

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
      { path: 'home', name: 'Home', component: () => import('../views/Home.vue'), meta: { moduleKey: 'home' } },
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { moduleKey: 'dashboard' } },
      { path: 'customers', name: 'Customers', component: () => import('../views/Customers.vue'), meta: { moduleKey: 'customers' } },
      { path: 'performance', name: 'Performance', component: () => import('../views/Performance.vue'), meta: { moduleKey: 'performance' } },
      { path: 'inventory', name: 'Inventory', component: () => import('../views/Inventory.vue'), meta: { moduleKey: 'inventory' } },
      { path: 'tools', name: 'Tools', component: () => import('../views/Tools.vue'), meta: { moduleKey: 'tools' } },
      { path: 'todo', name: 'Todo', component: () => import('../views/Todo.vue'), meta: { moduleKey: 'tools' } },
      { path: 'visit', name: 'Visit', component: () => import('../views/Visit.vue'), meta: { moduleKey: 'customers' } },
      { path: 'checkin', name: 'CheckIn', component: () => import('../views/CheckIn.vue'), meta: { moduleKey: 'customers' } },
      { path: 'order', name: 'Order', component: () => import('../views/Order.vue'), meta: { moduleKey: 'sales' } },
      { path: 'print', name: 'Print', component: () => import('../views/Print.vue'), meta: { moduleKey: 'sales' } },
      { path: 'receivables', name: 'Receivables', component: () => import('../views/Receivables.vue'), meta: { moduleKey: 'finance' } },
      { path: 'payments', name: 'Payments', component: () => import('../views/Payments.vue'), meta: { moduleKey: 'finance' } },
      { path: 'account', name: 'Account', component: () => import('../views/Account.vue'), meta: { moduleKey: 'profile' } },
      { path: 'transfer', name: 'Transfer', component: () => import('../views/Transfer.vue'), meta: { moduleKey: 'inventory' } },
      { path: 'check', name: 'Check', component: () => import('../views/Check.vue'), meta: { moduleKey: 'inventory' } },
      { path: 'loss-report', name: 'LossReport', component: () => import('../views/LossReport.vue'), meta: { moduleKey: 'inventory' } },
      { path: 'approve', name: 'Approve', component: () => import('../views/Approve.vue'), meta: { moduleKey: 'sales' } },
      { path: 'employee', name: 'Employee', component: () => import('../views/Employee.vue'), meta: { moduleKey: 'employees' } },
      { path: 'supplier', name: 'Supplier', component: () => import('../views/Supplier.vue'), meta: { moduleKey: 'suppliers' } },
      { path: 'purchase', name: 'Purchase', component: () => import('../views/Purchase.vue'), meta: { moduleKey: 'purchases' } },
      { path: 'settings', name: 'Settings', component: () => import('../views/Settings.vue'), meta: { moduleKey: 'system' } },
      { path: 'roles', name: 'Roles', component: () => import('../views/Roles.vue'), meta: { moduleKey: 'roles' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

// 默认允许访问的Tab（无权限时重定向）
const DEFAULT_TABS = ['home', 'dashboard', 'customers', 'performance', 'inventory', 'finance', 'tools', 'profile']

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const token = localStorage.getItem('token')

  if (to.path !== '/login' && !token) {
    next('/login')
    return
  }

  if (to.path === '/login') {
    next()
    return
  }

  // 权限检查
  const moduleKey = to.meta.moduleKey
  if (moduleKey && !authStore.isAdmin) {
    // 有模块Key且非管理员，检查权限
    if (!authStore.hasModule(moduleKey)) {
      // 找第一个有权限的Tab重定向
      const firstAllowed = DEFAULT_TABS.find(tab => authStore.hasModule(tab))
      if (firstAllowed) {
        next('/' + firstAllowed)
        return
      }
      // 无任何权限，跳转登录
      next('/login')
      return
    }
  }

  next()
})

export default router