<template>
  <view class="container">
    <view class="user-card">
      <view class="avatar">A</view>
      <view class="user-info">
        <text class="username">admin</text>
        <text class="role">管理员</text>
      </view>
    </view>
    <view class="menu-section">
      <view class="menu-item" @click="showReceipt = true">
        <text class="menu-icon">💰</text>
        <text class="menu-text">收款登记</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="loadReceivables">
        <text class="menu-icon">📊</text>
        <text class="menu-text">应收账款</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/products/index')">
        <text class="menu-icon">📦</text>
        <text class="menu-text">商品管理</text>
        <text class="menu-arrow">></text>
      </view>
    </view>
    <view v-if="receivables.length > 0" class="receivables-section">
      <text class="section-title">应收账款</text>
      <view v-for="r in receivables" :key="r.id" class="receivable-item">
        <text class="party-name">{{ r.name }}</text>
        <text class="balance">¥{{ r.balance }}</text>
      </view>
    </view>
    <button class="btn-logout" @click="handleLogout">退出登录</button>
    <view v-if="showReceipt" class="modal">
      <view class="modal-content">
        <text class="modal-title">收款登记</text>
        <view class="form-item">
          <text class="label">客户ID</text>
          <input v-model="receiptForm.customer_id" type="number" placeholder="客户ID" />
        </view>
        <view class="form-item">
          <text class="label">金额</text>
          <input v-model="receiptForm.amount" type="digit" placeholder="收款金额" />
        </view>
        <view class="form-item">
          <text class="label">方式</text>
          <picker :range="['现金', '转账', '微信', '支付宝']" @change="onMethodChange">
            <view class="picker">{{ receiptForm.payment_method || '选择方式' }}</view>
          </picker>
        </view>
        <view class="modal-btns">
          <button class="btn-cancel" @click="showReceipt = false">取消</button>
          <button class="btn-confirm" @click="handleReceipt">确定</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { api } from '../../api/request.js'

export default {
  data() {
    return {
      showReceipt: false,
      receiptForm: { customer_id: null, amount: 0, payment_method: '转账', remark: '' },
      receivables: []
    }
  },
  methods: {
    onMethodChange(e) {
      this.receiptForm.payment_method = ['现金', '转账', '微信', '支付宝'][e.detail.value]
    },
    async handleReceipt() {
      if (!this.receiptForm.customer_id || !this.receiptForm.amount) {
        uni.showToast({ title: '请填写完整信息', icon: 'none' })
        return
      }
      try {
        await api.createReceipt(this.receiptForm)
        uni.showToast({ title: '收款成功' })
        this.showReceipt = false
        this.receiptForm = { customer_id: null, amount: 0, payment_method: '转账', remark: '' }
      } catch (e) {}
    },
    async loadReceivables() {
      try {
        const res = await api.getReceivables()
        this.receivables = res.data || []
      } catch (e) {}
    },
    goTo(url) {
      uni.navigateTo({ url })
    },
    handleLogout() {
      uni.removeStorageSync('token')
      uni.redirectTo({ url: '/pages/login/login' })
    }
  }
}
</script>

<style>
.container {
  padding: 20rpx;
}
.user-card {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
}
.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: rgba(255,255,255,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  color: #fff;
  font-weight: bold;
}
.user-info {
  margin-left: 24rpx;
}
.username {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #fff;
}
.role {
  display: block;
  font-size: 24rpx;
  color: rgba(255,255,255,0.8);
  margin-top: 4rpx;
}
.menu-section {
  background: #fff;
  border-radius: 12rpx;
  margin-bottom: 24rpx;
}
.menu-item {
  display: flex;
  align-items: center;
  padding: 28rpx 24rpx;
  border-bottom: 1rpx solid #f0f0f0;
}
.menu-icon {
  font-size: 36rpx;
  margin-right: 16rpx;
}
.menu-text {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}
.menu-arrow {
  color: #999;
}
.receivables-section {
  background: #fff;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
}
.section-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 16rpx;
}
.receivable-item {
  display: flex;
  justify-content: space-between;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.party-name {
  font-size: 26rpx;
  color: #666;
}
.balance {
  font-size: 26rpx;
  font-weight: bold;
  color: #F56C6C;
}
.btn-logout {
  background: #fff;
  color: #F56C6C;
  border: 1rpx solid #F56C6C;
  margin-top: 20rpx;
}
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.modal-content {
  background: #fff;
  border-radius: 16rpx;
  padding: 32rpx;
  width: 80%;
}
.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 24rpx;
  text-align: center;
}
.form-item {
  margin-bottom: 20rpx;
}
.form-item .label {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 8rpx;
}
.form-item input, .form-item .picker {
  background: #f5f5f5;
  padding: 16rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
}
.modal-btns {
  display: flex;
  gap: 16rpx;
  margin-top: 24rpx;
}
.btn-cancel {
  flex: 1;
  background: #f0f0f0;
  color: #666;
}
.btn-confirm {
  flex: 1;
  background: #409EFF;
  color: #fff;
}
</style>
