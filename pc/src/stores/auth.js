import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, getCurrentUser } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const modules = ref([])
  const permissions = ref({})
  const operations = ref([])
  const warehouse_ids = ref([])
  const route_ids = ref([])

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => user.value?.username || '')
  const displayName = computed(() => user.value?.name || user.value?.username || '')
  const roleId = computed(() => user.value?.role_id || null)
  const roleName = computed(() => user.value?.role_name || '')
  const isAdmin = computed(() => {
    if (permissions.value['*']) return true
    if (operations.value.includes('*')) return true
    const roles = user.value?.permissions?.roles || []
    return roles.some(r => r.role_key === 'admin')
  })

  function hasModule(moduleKey) {
    return modules.value.includes(moduleKey)
  }

  function hasOperation(operation) {
    if (isAdmin.value) return true
    return operations.value.includes(operation)
  }

  function can(moduleKey, action) {
    if (isAdmin.value) return true
    const perm = permissions.value[moduleKey]
    if (!perm) return false
    return perm[action] === true
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
      const perms = res.data?.permissions || {}
      modules.value = perms.modules || []
      permissions.value = perms.permissions || {}
      operations.value = perms.operations || []
      warehouse_ids.value = perms.warehouse_ids || []
      route_ids.value = perms.route_ids || []
    } catch {
      user.value = null
      modules.value = []
      permissions.value = {}
      operations.value = []
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    modules.value = []
    permissions.value = {}
    operations.value = []
    localStorage.removeItem('token')
  }

  return {
    token, user, isLoggedIn, username, displayName,
    roleId, roleName, permissions, isAdmin,
    modules, operations, warehouse_ids, route_ids,
    hasModule, hasOperation, can,
    login, fetchUser, logout
  }
})
