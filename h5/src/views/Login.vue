<template>
  <div class="login-page">
    <div class="logo">FastInOut</div>
    <van-form @submit="handleLogin">
      <van-cell-group inset>
        <van-field v-model="form.username" label="账号" placeholder="请输入账号" required />
        <van-field v-model="form.password" type="password" label="密码" placeholder="请输入密码" required />
      </van-cell-group>
      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">登录</van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const form = ref({ username: '', password: '' })
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    await authStore.login(form.value)
    router.push('/home')
  } catch (e) {
    showToast('登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page { padding-top: 100px; background: #f7f8fa; min-height: 100vh; }
.logo { text-align: center; font-size: 28px; font-weight: bold; color: #1989fa; padding: 40px 0; }
</style>