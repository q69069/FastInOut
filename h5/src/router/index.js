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
      { path: 'todo', name: 'Todo', component: () => import('../views/Todo.vue') },
      { path: 'visit', name: 'Visit', component: () => import('../views/Visit.vue') },
      { path: 'checkin', name: 'CheckIn', component: () => import('../views/CheckIn.vue') },
      { path: 'order', name: 'Order', component: () => import('../views/Order.vue') },
      { path: 'print', name: 'Print', component: () => import('../views/Print.vue') },
      { path: 'inventory', name: 'Inventory', component: () => import('../views/Inventory.vue') },
      { path: 'performance', name: 'Performance', component: () => import('../views/Performance.vue') },
      { path: 'receivables', name: 'Receivables', component: () => import('../views/Receivables.vue') }
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