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
      {
        path: 'home',
        name: 'Home',
        component: () => import('../views/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'todo',
        name: 'Todo',
        component: () => import('../views/Todo.vue'),
        meta: { title: '待办' }
      },
      {
        path: 'visit',
        name: 'Visit',
        component: () => import('../views/Visit.vue'),
        meta: { title: '拜访' }
      },
      {
        path: 'checkin',
        name: 'CheckIn',
        component: () => import('../views/CheckIn.vue'),
        meta: { title: '打卡' }
      },
      {
        path: 'order',
        name: 'Order',
        component: () => import('../views/Order.vue'),
        meta: { title: '下单' }
      },
      {
        path: 'print',
        name: 'Print',
        component: () => import('../views/Print.vue'),
        meta: { title: '打印' }
      },
      {
        path: 'performance',
        name: 'Performance',
        component: () => import('../views/Performance.vue'),
        meta: { title: '业绩' }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('../views/Inventory.vue'),
        meta: { title: '查库存' }
      },
      {
        path: 'receivables',
        name: 'Receivables',
        component: () => import('../views/Receivables.vue'),
        meta: { title: '应收' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory('/h5'),
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
