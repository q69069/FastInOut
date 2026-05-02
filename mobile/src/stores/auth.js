import { defineStore } from 'pinia'
import api from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    routes: [],
    warehouses: []
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    userName: (state) => state.user?.name || '',
    roleType: (state) => state.user?.role_type || '',
    canSkipAudit: (state) => state.user?.bypass_audit === 1,
    routeIds: (state) => (state.user?.route_ids || '').split(',').filter(Boolean).map(Number),
    warehouseIds: (state) => (state.user?.warehouse_ids || '').split(',').filter(Boolean).map(Number)
  },
  actions: {
    async login(phone, password) {
      const res = await api.post('/auth/login', { phone, password })
      this.token = res.data.data.token
      this.user = res.data.data.user
      localStorage.setItem('token', this.token)
      localStorage.setItem('user', JSON.stringify(this.user))
      return res.data
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
