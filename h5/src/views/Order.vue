<template>
  <div class="order-page">
    <van-nav-bar title="快速下单" />
    <div class="content">
      <van-cell-group title="选择客户">
        <van-cell is-link @click="showCustomerPicker = true">
          {{ selectedCustomer?.name || '请选择客户' }}
        </van-cell>
      </van-cell-group>
      <van-cell-group title="商品列表" style="margin-top: 12px;">
        <van-cell v-for="item in products" :key="item.id" :title="item.name" :label="`¥${item.price}`">
          <template #extra>
            <van-stepper v-model="item.qty" min="0" />
          </template>
        </van-cell>
      </van-cell-group>
      <div style="padding: 16px;">
        <van-button type="primary" block @click="handleSubmit">提交订单</van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast } from 'vant'
import { getProducts, getCustomers, createSalesOrder } from '../api'

const products = ref([])
const selectedCustomer = ref(null)
const showCustomerPicker = ref(false)

const handleSubmit = async () => {
  if (!selectedCustomer.value) {
    showToast('请选择客户')
    return
  }
  const items = products.value.filter(p => p.qty > 0).map(p => ({ product_id: p.id, quantity: p.qty, price: p.price }))
  if (items.length === 0) {
    showToast('请选择商品')
    return
  }
  try {
    await createSalesOrder({ customer_id: selectedCustomer.value.id, items })
    showToast('下单成功')
  } catch (e) {
    showToast('下单失败')
  }
}

onMounted(async () => {
  try {
    const [pRes, cRes] = await Promise.all([getProducts(), getCustomers()])
    products.value = (pRes.data || []).map(p => ({ ...p, qty: 0 }))
    selectedCustomer.value = cRes.data?.[0] || null
  } catch (e) {}
})
</script>

<style scoped>
.order-page { background: #f7f8fa; min-height: 100vh; }
.content { padding-bottom: 20px; }
</style>