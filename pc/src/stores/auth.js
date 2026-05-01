import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, getCurrentUser } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => user.value?.username || '')
  const displayName = computed(() => user.value?.name || user.value?.username || '')
  const roleId = computed(() => user.value?.role_id || null)
  const roleName = computed(() => user.value?.role_name || '')
  const permissions = computed(() => user.value?.permissions || [])
  const isAdmin = computed(() => roleName.value === '管理员' || permissions.value.includes('*'))

  function hasPermission(perm) {
    if (isAdmin.value) return true
    return permissions.value.includes(perm)
  }

  async function login(form) {
    const res = await apiLogin(form)
    const t = res.data?.token
    if (t) {
      token.value = t
      localStorage.setItem('token', t)
      await fetchUser()
    }
    return res
  }

  async function fetchUser() {
    try {
      const res = await getCurrentUser()
      user.value = res.data || null
    } catch {
      user.value = null
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return {
    token, user, isLoggedIn, username, displayName,
    roleId, roleName, permissions, isAdmin,
    hasPermission, login, fetchUser, logout
  }
})
