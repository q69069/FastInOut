<template>
  <view class="container">
    <view class="header">
      <text class="greeting">{{ greeting }}，admin</text>
    </view>
    <view class="stats">
      <view class="stat-card">
        <text class="stat-value">{{ formatNum(dashboard.today_sales) }}</text>
        <text class="stat-label">今日销售额</text>
      </view>
      <view class="stat-card">
        <text class="stat-value">{{ formatNum(dashboard.today_receipt) }}</text>
        <text class="stat-label">今日回款</text>
      </view>
      <view class="stat-card">
        <text class="stat-value">{{ formatNum(dashboard.total_stock_qty) }}</text>
        <text class="stat-label">库存总量</text>
      </view>
      <view class="stat-card">
        <text class="stat-value">{{ formatNum(dashboard.alert_count) }}</text>
        <text class="stat-label">库存预警</text>
      </view>
    </view>
    <view class="quick-actions">
      <text class="section-title">快捷操作</text>
      <view class="actions-grid">
        <view class="action-item" @click="goTo('/pages/sales/index')">
          <text class="action-icon">📝</text>
          <text class="action-text">销售开单</text>
        </view>
        <view class="action-item" @click="goTo('/pages/inventory/index')">
          <text class="action-icon">📦</text>
          <text class="action-text">库存查询</text>
        </view>
        <view class="action-item" @click="goTo('/pages/customers/index')">
          <text class="action-icon">👥</text>
          <text class="action-text">客户管理</text>
        </view>
        <view class="action-item" @click="goTo('/pages/mine/index')">
          <text class="action-icon">💰</text>
          <text class="action-text">收款登记</text>
        </view>
      </view>
    </view>
    <view class="info-cards">
      <view class="info-card">
        <text class="info-label">应收账款</text>
        <text class="info-value">¥{{ formatNum(dashboard.total_receivable) }}</text>
      </view>
      <view class="info-card">
        <text class="info-label">应付账款</text>
        <text class="info-value">¥{{ formatNum(dashboard.total_payable) }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import { api } from '../../api/request.js'

export default {
  data() {
    return {
      dashboard: {}
    }
  },
  computed: {
    greeting() {
      const h = new Date().getHours()
      if (h < 12) return '早上好'
      if (h < 18) return '下午好'
      return '晚上好'
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const res = await api.getDashboard()
        this.dashboard = res.data || {}
      } catch (e) {}
    },
    formatNum(n) {
      if (!n) return '0'
      return Number(n).toLocaleString('zh-CN')
    },
    goTo(url) {
      uni.navigateTo({ url })
    }
  }
}
</script>

<style>
.container {
  padding: 20rpx;
}
.header {
  padding: 20rpx 0;
}
.greeting {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}
.stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
  margin: 20rpx 0;
}
.stat-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: center;
}
.stat-value {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #409EFF;
}
.stat-label {
  display: block;
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}
.quick-actions {
  margin: 30rpx 0;
}
.section-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 16rpx;
}
.actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 16rpx;
}
.action-item {
  background: #fff;
  border-radius: 12rpx;
  padding: 20rpx;
  text-align: center;
}
.action-icon {
  display: block;
  font-size: 48rpx;
}
.action-text {
  display: block;
  font-size: 22rpx;
  color: #666;
  margin-top: 8rpx;
}
.info-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}
.info-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
}
.info-label {
  display: block;
  font-size: 24rpx;
  color: #999;
}
.info-value {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-top: 8rpx;
}
</style>
