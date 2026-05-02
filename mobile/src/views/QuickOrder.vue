<template>
  <div class="page">
    <van-nav-bar title="快速下单" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="content">
      <!-- 选择客户 -->
      <van-field v-model="customerSearch" placeholder="🔍 搜索客户" @update:model-value="searchCustomer" />
      <div v-if="customerResults.length" class="customer-list">
        <div v-for="c in customerResults" :key="c.id" class="customer-item"
          :class="{ selected: selectedCustomer?.id === c.id }" @click="selectCustomer(c)">
          <div class="c-name">{{ c.name }}</div>
          <div class="c-meta">欠款 ¥{{ (c.receivable || 0).toFixed(2) }}</div>
        </div>
      </div>

      <!-- 已选客户 -->
      <div v-if="selectedCustomer" class="selected-info">
        <van-tag type="success" size="large">{{ selectedCustomer.name }}</van-tag>
        <span>当前欠款: ¥{{ (selectedCustomer.receivable || 0).toFixed(2) }}</span>
      </div>

      <!-- 搜索商品 -->
      <van-field v-model="productSearch" placeholder="🔍 搜索商品/扫条码" style="margin-top: 8px;" />
      <div v-if="productResults.length" class="product-list">
        <div v-for="p in productResults" :key="p.id" class="product-item" @click="addItem(p)">
          <div class="p-name">{{ p.name }}</div>
          <div class="p-price">售价 ¥{{ p.default_price?.toFixed(2) || p.retail_price?.toFixed(2) }}</div>
        </div>
      </div>

      <!-- 已选商品 -->
      <div v-if="items.length" class="cart-section">
        <h4>已选商品</h4>
        <div v-for="(item, i) in items" :key="i" class="cart-item">
          <span class="ci-name">{{ item.name }}</span>
          <div class="ci-qty">
            <van-button size="mini" icon="minus" @click="item.qty = Math.max(1, item.qty - 1)" />
            <span class="qty-num">{{ item.qty }}</span>
            <van-button size="mini" icon="plus" @click="item.qty++" />
          </div>
          <span class="ci-subtotal">¥{{ (item.price * item.qty).toFixed(2) }}</span>
        </div>
        <div class="cart-footer">
          <span class="total">合计：¥{{ totalAmount.toFixed(2) }}</span>
          <van-button type="primary" size="small" @click="submitOrder" :loading="submitting"
            :disabled="!selectedCustomer || items.length === 0">✅ 提交订单</van-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/api'
import { showToast, showSuccessToast } from 'vant'

const customerSearch = ref(''); const selectedCustomer = ref(null); const customerResults = ref([])
const productSearch = ref(''); const productResults = ref([])
const items = ref([]); const submitting = ref(false)

const totalAmount = computed(() => items.value.reduce((s, i) => s + i.price * i.qty, 0))

const searchCustomer = async (val) => {
  if (!val || val.length < 2) { customerResults.value = []; return }
  const res = await api.get('/customers', { params: { search: val, limit: 10 } })
  customerResults.value = res.data.data?.items || []
}

const selectCustomer = (c) => { selectedCustomer.value = c; customerSearch.value = c.name; customerResults.value = [] }

const addItem = (p) => {
  const price = p.default_price || p.retail_price || 0
  const exist = items.value.find(i => i.id === p.id)
  if (exist) { exist.qty++ } else { items.value.push({ id: p.id, name: p.name, price, qty: 1, unit: p.unit }) }
  productResults.value = []; productSearch.value = ''
}

const submitOrder = async () => {
  submitting.value = true
  try {
    const res = await api.post('/sales-orders', {
      customer_id: selectedCustomer.value.id,
      items: items.value.map(i => ({ product_id: i.id, quantity: i.qty, price: i.price, unit: i.unit })),
      source: 'mobile'
    })
    showSuccessToast(`下单成功！${res.data.data?.code || ''}`)
    items.value = []; selectedCustomer.value = null
  } catch (e) { showToast(e.response?.data?.detail || '下单失败') } finally { submitting.value = false }
}
</script>

<style scoped>
.page { min-height: 100vh; background: #f7f8fa; padding-bottom: 20px; }
.content { padding: 8px 12px; }
.customer-list { background: #fff; border-radius: 8px; margin: 4px 0; overflow: hidden; }
.customer-item { padding: 10px 14px; border-bottom: 1px solid #f0f0f0; }
.customer-item.selected { background: #e8f5e9; }
.c-name { font-size: 15px; font-weight: 600; }
.c-meta { font-size: 12px; color: #999; }
.selected-info { display: flex; align-items: center; gap: 10px; padding: 10px 0; font-size: 14px; color: #666; }
.product-list { background: #fff; border-radius: 8px; margin: 4px 0; }
.product-item { padding: 10px 14px; border-bottom: 1px solid #f0f0f0; }
.p-name { font-size: 14px; }
.p-price { font-size: 12px; color: #ee0a24; }
.cart-section { background: #fff; border-radius: 10px; padding: 12px; margin-top: 12px; }
.cart-section h4 { margin-bottom: 8px; font-size: 15px; color: #333; }
.cart-item { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #f7f7f7; }
.ci-name { flex: 1; font-size: 13px; }
.ci-qty { display: flex; align-items: center; gap: 4px; }
.qty-num { min-width: 28px; text-align: center; font-weight: 600; }
.ci-subtotal { font-weight: 600; color: #ee0a24; font-size: 13px; min-width: 60px; text-align: right; }
.cart-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.total { font-size: 16px; font-weight: 700; color: #ee0a24; }
</style>
