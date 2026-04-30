<template>
  <view class="login-container">
    <view class="logo">
      <text class="title">FastInOut</text>
      <text class="subtitle">快消品进销存</text>
    </view>
    <view class="form">
      <view class="input-group">
        <input v-model="username" placeholder="请输入账号" />
      </view>
      <view class="input-group">
        <input v-model="password" type="password" placeholder="请输入密码" />
      </view>
      <button class="btn-login" @click="handleLogin" :loading="loading">登 录</button>
    </view>
  </view>
</template>

<script>
import { api } from '../../api/request.js'

export default {
  data() {
    return {
      username: '',
      password: '',
      loading: false
    }
  },
  methods: {
    async handleLogin() {
      if (!this.username || !this.password) {
        uni.showToast({ title: '请输入账号和密码', icon: 'none' })
        return
      }
      this.loading = true
      try {
        const res = await api.login({ username: this.username, password: this.password })
        const token = res.data?.access_token
        if (token) {
          uni.setStorageSync('token', token)
          uni.showToast({ title: '登录成功' })
          uni.switchTab({ url: '/pages/index/index' })
        }
      } catch (e) {
        // 错误已在request中处理
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style>
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.logo {
  text-align: center;
  margin-bottom: 60rpx;
}
.title {
  display: block;
  font-size: 60rpx;
  font-weight: bold;
  color: #fff;
}
.subtitle {
  display: block;
  font-size: 28rpx;
  color: rgba(255,255,255,0.8);
  margin-top: 10rpx;
}
.form {
  width: 80%;
}
.input-group {
  background: #fff;
  border-radius: 12rpx;
  margin-bottom: 24rpx;
  padding: 0 24rpx;
}
.input-group input {
  height: 88rpx;
  font-size: 28rpx;
}
.btn-login {
  background: #409EFF;
  color: #fff;
  border: none;
  border-radius: 12rpx;
  height: 88rpx;
  line-height: 88rpx;
  font-size: 32rpx;
  margin-top: 20rpx;
}
</style>
