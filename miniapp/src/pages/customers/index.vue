<template>
  <view class="container">
    <view class="search-bar">
      <input v-model="keyword" placeholder="搜索客户名称" @confirm="loadData" />
      <button class="btn-search" size="mini" @click="loadData">查询</button>
    </view>
    <view class="customer-list">
      <view v-for="customer in list" :key="customer.id" class="customer-card">
        <view class="card-header">
          <text class="customer-name">{{ customer.name }}</text>
          <text :class="['level', 'level-' + customer.level]">{{ customer.level || '普通' }}</text>
        </view>
        <view class="card-body">
          <view class="info-row">
            <text class="label">联系人：</text>
            <text>{{ customer.contact || '-' }}</text>
          </view>
          <view class="info-row">
            <text class="label">电话：</text>
            <text>{{ customer.phone || '-' }}</text>
          </view>
          <view class="info-row">
            <text class="label">应收余额：</text>
            <text :class="['balance', customer.receivable_balance > 0 ? 'has-balance' : '']">¥{{ customer.receivable_balance || 0 }}</text>
          </view>
        </view>
      </view>
      <view v-if="list.length === 0" class="empty">暂无客户数据</view>
    </view>
  </view>
</template>

<script>
import { api } from '../../api/request.js'

export default {
  data() {
    return {
      keyword: '',
      list: []
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const res = await api.getCustomers({ page: 1, page_size: 50, keyword: this.keyword })
        this.list = res.data || []
      } catch (e) {}
    }
  }
}
</script>

<style>
.container {
  padding: 20rpx;
}
.search-bar {
  display: flex;
  gap: 12rpx;
  margin-bottom: 20rpx;
}
.search-bar input {
  flex: 1;
  background: #fff;
  padding: 16rpx 24rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
}
.btn-search {
  background: #409EFF;
  color: #fff;
  border: none;
}
.customer-card {
  background: #fff;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}
.customer-name {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}
.level {
  font-size: 24rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}
.level-普通 { background: #f0f0f0; color: #666; }
.level-会员 { background: #E6A23C; color: #fff; }
.level-VIP { background: #F56C6C; color: #fff; }
.info-row {
  display: flex;
  margin-bottom: 8rpx;
  font-size: 26rpx;
  color: #666;
}
.label {
  color: #999;
  width: 140rpx;
}
.balance {
  font-weight: bold;
}
.has-balance {
  color: #F56C6C;
}
.empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
}
</style>
