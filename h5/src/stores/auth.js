import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, getCurrentUser } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)
  const displayName = computed(() => user.value?.name || user.value?.username || '')

  async function fetchUser() {
    try {
      const res = await getCurrentUser()
      user.value = res.data || null
    } catch {
      user.value = null
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

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, isLoggedIn, displayName, fetchUser, login, logout }
})