<template>
  <view class="container">
    <view class="tabs">
      <view :class="['tab', activeTab === 'list' ? 'active' : '']" @click="activeTab = 'list'">订单列表</view>
      <view :class="['tab', activeTab === 'create' ? 'active' : '']" @click="activeTab = 'create'">销售开单</view>
    </view>
    <view v-if="activeTab === 'list'" class="order-list">
      <view v-for="order in orders" :key="order.id" class="order-card">
        <view class="order-header">
          <text class="order-code">{{ order.code }}</text>
          <text :class="['order-status', 'status-' + order.status]">{{ statusMap[order.status] }}</text>
        </view>
        <view class="order-info">
          <text>客户：{{ order.customer_name }}</text>
          <text>金额：¥{{ order.total_amount }}</text>
        </view>
        <text class="order-time">{{ order.created_at }}</text>
      </view>
      <view v-if="orders.length === 0" class="empty">暂无订单</view>
    </view>
    <view v-if="activeTab === 'create'" class="create-form">
      <view class="form-item">
        <text class="label">选择客户</text>
        <picker :range="customerNames" @change="onCustomerChange">
          <view class="picker">{{ selectedCustomer || '请选择客户' }}</view>
        </picker>
      </view>
      <view class="form-item">
        <text class="label">商品明细</text>
        <view v-for="(item, index) in form.items" :key="index" class="item-row">
          <picker :range="productNames" @change="(e) => onProductChange(index, e)">
            <view class="picker-small">{{ item.product_name || '选择商品' }}</view>
          </picker>
          <input v-model="item.quantity" type="number" placeholder="数量" class="qty-input" />
          <input v-model="item.price" type="digit" placeholder="单价" class="price-input" />
          <text class="delete-btn" @click="form.items.splice(index, 1)">×</text>
        </view>
        <button class="btn-add" size="mini" @click="addItem">+ 添加商品</button>
      </view>
      <view class="form-item">
        <text class="label">备注</text>
        <input v-model="form.remark" placeholder="备注信息" />
      </view>
      <button class="btn-submit" @click="handleSubmit" :loading="submitting">提交订单</button>
    </view>
  </view>
</template>

<script>
import { api } from '../../api/request.js'

export default {
  data() {
    return {
      activeTab: 'list',
      orders: [],
      customers: [],
      products: [],
      form: { customer_id: null, warehouse_id: 1, remark: '', items: [] },
      selectedCustomer: '',
      submitting: false,
      statusMap: { 0: '草稿', 1: '已确认', 2: '已出库', 3: '已关闭' }
    }
  },
  computed: {
    customerNames() {
      return this.customers.map(c => c.name)
    },
    productNames() {
      return this.products.map(p => p.name)
    }
  },
  onShow() {
    this.loadOrders()
    this.loadOptions()
  },
  methods: {
    async loadOrders() {
      try {
        const res = await api.getSalesOrders({ page: 1, page_size: 50 })
        this.orders = res.data || []
      } catch (e) {}
    },
    async loadOptions() {
      try {
        const [c, p] = await Promise.all([
          api.getCustomers({ page_size: 100 }),
          api.getProducts({ page_size: 100 })
        ])
        this.customers = c.data || []
        this.products = p.data || []
      } catch (e) {}
    },
    onCustomerChange(e) {
      const index = e.detail.value
      this.form.customer_id = this.customers[index].id
      this.selectedCustomer = this.customers[index].name
    },
    onProductChange(index, e) {
      const pIndex = e.detail.value
      this.form.items[index].product_id = this.products[pIndex].id
      this.form.items[index].product_name = this.products[pIndex].name
      this.form.items[index].price = this.products[pIndex].sale_price
    },
    addItem() {
      this.form.items.push({ product_id: null, product_name: '', quantity: 1, price: 0 })
    },
    async handleSubmit() {
      if (!this.form.customer_id) {
        uni.showToast({ title: '请选择客户', icon: 'none' })
        return
      }
      if (this.form.items.length === 0) {
        uni.showToast({ title: '请添加商品', icon: 'none' })
        return
      }
      this.submitting = true
      try {
        await api.createSalesOrder(this.form)
        uni.showToast({ title: '下单成功' })
        this.form = { customer_id: null, warehouse_id: 1, remark: '', items: [] }
        this.selectedCustomer = ''
        this.activeTab = 'list'
        this.loadOrders()
      } catch (e) {} finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style>
.container {
  padding: 20rpx;
}
.tabs {
  display: flex;
  background: #fff;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 20rpx;
  font-size: 28rpx;
  color: #666;
}
.tab.active {
  color: #409EFF;
  border-bottom: 4rpx solid #409EFF;
}
.order-card {
  background: #fff;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
}
.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.order-code {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}
.order-status {
  font-size: 24rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}
.status-0 { background: #E6A23C; color: #fff; }
.status-1 { background: #67C23A; color: #fff; }
.status-2 { background: #409EFF; color: #fff; }
.status-3 { background: #909399; color: #fff; }
.order-info {
  display: flex;
  justify-content: space-between;
  margin-top: 12rpx;
  font-size: 26rpx;
  color: #666;
}
.order-time {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}
.empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
}
.create-form {
  background: #fff;
  border-radius: 12rpx;
  padding: 24rpx;
}
.form-item {
  margin-bottom: 24rpx;
}
.label {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 12rpx;
}
.picker {
  background: #f5f5f5;
  padding: 16rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
  color: #666;
}
.item-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 12rpx;
}
.picker-small {
  flex: 2;
  background: #f5f5f5;
  padding: 12rpx;
  border-radius: 8rpx;
  font-size: 26rpx;
}
.qty-input, .price-input {
  flex: 1;
  background: #f5f5f5;
  padding: 12rpx;
  border-radius: 8rpx;
  font-size: 26rpx;
}
.delete-btn {
  color: #F56C6C;
  font-size: 36rpx;
  padding: 0 8rpx;
}
.btn-add {
  margin-top: 12rpx;
}
.btn-submit {
  background: #409EFF;
  color: #fff;
  border: none;
  margin-top: 20rpx;
}
</style>
