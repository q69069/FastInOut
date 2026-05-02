import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '工作台', needAuth: true }
  },
  // 8大窗口
  { path: '/pending-orders', name: 'PendingOrders', component: () => import('@/views/PendingOrders.vue'), meta: { title: '待办订单', needAuth: true } },
  { path: '/visit-plan', name: 'VisitPlan', component: () => import('@/views/VisitPlan.vue'), meta: { title: '拜访计划', needAuth: true } },
  { path: '/store-checkin', name: 'StoreCheckin', component: () => import('@/views/StoreCheckin.vue'), meta: { title: '门店打卡', needAuth: true } },
  { path: '/quick-order', name: 'QuickOrder', component: () => import('@/views/QuickOrder.vue'), meta: { title: '快速下单', needAuth: true } },
  { path: '/print-receipt', name: 'PrintReceipt', component: () => import('@/views/PrintReceipt.vue'), meta: { title: '打印小票', needAuth: true } },
  { path: '/performance', name: 'Performance', component: () => import('@/views/Performance.vue'), meta: { title: '业绩查看', needAuth: true } },
  { path: '/stock-check', name: 'StockCheck', component: () => import('@/views/StockCheck.vue'), meta: { title: '查库存', needAuth: true } },
  { path: '/receivables', name: 'Receivables', component: () => import('@/views/Receivables.vue'), meta: { title: '应收查询', needAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - FastInOut` : 'FastInOut'
  const token = localStorage.getItem('token')
  if (to.meta.needAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
