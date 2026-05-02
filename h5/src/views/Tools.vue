<template>
  <div class="tools-page">
    <van-nav-bar title="常用工具" />
    <van-cell-group>
      <van-cell title="清除缓存" is-link @click="clearCache" />
      <van-cell title="检查更新" is-link value="当前版本 1.0.0" />
      <van-cell title="退出登录" is-link @click="handleLogout" />
    </van-cell-group>
    <div class="logout-btn">
      <van-button type="danger" block @click="handleLogout">退出登录</van-button>
    </div>
  </div>
</template>

<script setup>
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const clearCache = () => {
  localStorage.clear()
  showToast('缓存已清除')
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.tools-page { background: #f7f8fa; min-height: 100vh; }
.logout-btn { padding: 20px 16px; }
</style>