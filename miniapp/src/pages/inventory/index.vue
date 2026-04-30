<template>
  <view class="container">
    <view class="search-bar">
      <input v-model="keyword" placeholder="搜索商品名称/编码" @confirm="loadData" />
      <button class="btn-search" size="mini" @click="loadData">查询</button>
    </view>
    <view class="inventory-list">
      <view v-for="item in list" :key="item.id" class="inventory-card">
        <view class="card-header">
          <text class="product-name">{{ item.product_name }}</text>
          <text class="warehouse">{{ item.warehouse_name }}</text>
        </view>
        <view class="card-body">
          <view class="info-row">
            <text class="label">编码：</text>
            <text>{{ item.product_code }}</text>
          </view>
          <view class="info-row">
            <text class="label">规格：</text>
            <text>{{ item.product_spec || '-' }}</text>
          </view>
          <view class="info-row">
            <text class="label">库存：</text>
            <text :class="['qty', item.quantity < 10 ? 'low' : '']">{{ item.quantity }} {{ item.product_unit }}</text>
          </view>
          <view class="info-row">
            <text class="label">成本价：</text>
            <text>¥{{ item.cost_price }}</text>
          </view>
        </view>
      </view>
      <view v-if="list.length === 0" class="empty">暂无库存数据</view>
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
        const res = await api.getInventory({ page: 1, page_size: 50, keyword: this.keyword })
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
.inventory-card {
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
.product-name {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}
.warehouse {
  font-size: 24rpx;
  color: #409EFF;
  background: #ecf5ff;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}
.info-row {
  display: flex;
  margin-bottom: 8rpx;
  font-size: 26rpx;
  color: #666;
}
.label {
  color: #999;
  width: 120rpx;
}
.qty {
  font-weight: bold;
  color: #333;
}
.qty.low {
  color: #F56C6C;
}
.empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
}
</style>
