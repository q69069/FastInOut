import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, getCurrentUser, getPermissions } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const roles = ref([])  // 所有角色列表
  const currentRoleId = ref(null)  // 当前选中的角色ID
  const modules = ref([])
  const permissions = ref({})
  const operations = ref([])
  const warehouse_ids = ref([])
  const route_ids = ref([])

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => user.value?.username || '')
  const displayName = computed(() => user.value?.name || user.value?.username || '')
  const roleId = computed(() => currentRoleId.value || user.value?.role_id || null)
  const roleName = computed(() => {
    const r = roles.value.find(r => r.id === currentRoleId.value)
    return r?.name || user.value?.role_name || ''
  })
  const isAdmin = computed(() => {
    if (permissions.value['*']) return true
    if (operations.value.includes('*')) return true
    return roles.value.some(r => r.role_key === 'admin')
  })

  // 当前角色的角色信息
  const currentRole = computed(() => {
    return roles.value.find(r => r.id === currentRoleId.value) || roles.value[0] || null
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

  // 切换角色
  async function switchRole(roleId) {
    if (!roles.value.find(r => r.id === roleId)) {
      console.error('[Auth] 角色不存在:', roleId)
      return
    }
    currentRoleId.value = roleId
    // 重新获取该角色的权限
    await fetchPermissionsForRole(roleId)
    localStorage.setItem('currentRoleId', String(roleId))
  }

  // 获取指定角色的权限
  async function fetchPermissionsForRole(roleId) {
    try {
      const res = await getPermissions({ role_id: roleId })
      const perms = res.data || {}
      modules.value = perms.modules || []
      permissions.value = perms.permissions || {}
      operations.value = perms.operations || []
      warehouse_ids.value = perms.warehouse_ids || []
      route_ids.value = perms.route_ids || []
    } catch (e) {
      console.error('[Auth] 获取角色权限失败:', e)
    }
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
      // 设置所有角色
      roles.value = res.data?.roles || []
      // 恢复上次选中的角色，或默认选第一个
      const savedRoleId = localStorage.getItem('currentRoleId')
      const defaultRole = savedRoleId
        ? roles.value.find(r => r.id === parseInt(savedRoleId))
        : roles.value[0]
      if (defaultRole) {
        currentRoleId.value = defaultRole.id
      }
      // 获取权限
      const perms = res.data?.permissions || {}
      modules.value = perms.modules || []
      permissions.value = perms.permissions || {}
      operations.value = perms.operations || []
      warehouse_ids.value = perms.warehouse_ids || []
      route_ids.value = perms.route_ids || []
    } catch {
      user.value = null
      roles.value = []
      modules.value = []
      permissions.value = {}
      operations.value = []
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    roles.value = []
    currentRoleId.value = null
    modules.value = []
    permissions.value = {}
    operations.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('currentRoleId')
  }

  return {
    token, user, isLoggedIn, username, displayName,
    roleId, roleName, isAdmin, roles, currentRole,
    modules, operations, warehouse_ids, route_ids,
    hasModule, hasOperation, can,
    switchRole, login, fetchUser, logout
  }
})
