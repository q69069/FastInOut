<template>
  <div class="login-page">
    <div class="login-card">
      <h1>🚀 FastInOut</h1>
      <p class="sub">业务员手机端</p>
      <van-form @submit="onLogin">
        <van-cell-group inset>
          <van-field v-model="phone" name="phone" label="手机号" placeholder="请输入手机号"
            type="tel" maxlength="11" :rules="[{ required: true, message: '请填写手机号' }]" />
          <van-field v-model="password" name="password" label="密码" placeholder="请输入密码"
            type="password" :rules="[{ required: true, message: '请填写密码' }]" />
        </van-cell-group>
        <div style="margin: 20px 16px">
          <van-button round block type="primary" native-type="submit" :loading="loading">
            登 录
          </van-button>
        </div>
      </van-form>
      <p class="tip">仅限业务员/仓管/财务账号登录</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { showToast } from 'vant'

const router = useRouter()
const auth = useAuthStore()
const phone = ref('')
const password = ref('')
const loading = ref(false)

const onLogin = async () => {
  loading.value = true
  try {
    await auth.login(phone.value, password.value)
    showToast('登录成功')
    router.replace('/')
  } catch (e) {
    showToast(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 90%; max-width: 380px; background: #fff; border-radius: 16px;
  padding: 40px 20px 30px; box-shadow: 0 10px 40px rgba(0,0,0,.15);
}
.login-card h1 { text-align: center; font-size: 28px; color: #333; margin-bottom: 4px; }
.sub { text-align: center; color: #999; font-size: 14px; margin-bottom: 24px; }
.tip { text-align: center; color: #bbb; font-size: 12px; margin-top: 12px; }
</style>
