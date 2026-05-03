<template>
  <div class="order-page">
    <van-nav-bar title="快速下单" left-arrow @click-left="$router.back()" />

    <!-- 客户信息 -->
    <div class="customer-card">
      <div class="card-label">客户信息</div>
      <van-cell-group inset>
        <van-cell title="客户" is-link :value="form.customer_name || '请选择客户'" @click="showCustomerPopup = true" />
        <van-cell title="收货地址" :label="form.address || ''" value="查看地图" />
      </van-cell-group>
    </div>

    <!-- 商品列表 -->
    <div class="product-card">
      <div class="card-label">商品明细</div>
      <van-cell-group inset>
        <div v-for="(item, index) in form.items" :key="index" class="product-item">
          <div class="product-info">
            <div class="product-name">{{ item.product_name }}</div>
            <div class="product-price">¥{{ item.price }}</div>
          </div>
          <van-stepper v-model="item.quantity" min="0" @change="calcTotal" />
        </div>
      </van-cell-group>
    </div>

    <!-- 订单汇总 -->
    <div class="summary-card">
      <van-cell-group inset>
        <van-cell title="商品数量">
          <template #value><span class="orange">{{ totalQty }}</span> 件</template>
        </van-cell>
        <van-cell title="订单金额">
          <template #value><span class="orange">¥{{ totalAmount }}</span></template>
        </van-cell>
        <van-cell title="整单折扣">
          <template #extra>
            <van-field v-model="form.discount" type="number" input-align="right" placeholder="0" style="width: 80px;" @change="calcTotal" />
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 提交按钮 -->
    <div class="submit-bar">
      <div class="total-info">
        <span>合计：</span>
        <span class="total-price">¥{{ finalAmount }}</span>
      </div>
      <van-button v-if="authStore.hasOperation('sales:create')" type="primary" size="large" :loading="loading" @click="handleSubmit">提交订单</van-button>
      <van-button v-else type="default" size="large" disabled>无权限提交</van-button>
    </div>

    <!-- 客户选择弹窗 -->
    <van-popup v-model:show="showCustomerPopup" position="bottom" round>
      <van-picker
        title="选择客户"
        :columns="customerColumns"
        @confirm="onCustomerConfirm"
        @cancel="showCustomerPopup = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getCustomers, getProducts, createSalesOrder } from '../api'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const showCustomerPopup = ref(false)

const form = ref({
  customer_id: null,
  customer_name: '',
  address: '',
  discount: 0,
  items: []
})

const customers = ref([])

const customerColumns = computed(() =>
  customers.value.map(c => ({ text: c.name, value: c.id }))
)

const totalQty = computed(() =>
  form.value.items.reduce((sum, item) => sum + (item.quantity || 0), 0)
)

const totalAmount = computed(() =>
  form.value.items.reduce((sum, item) => sum + (item.quantity || 0) * (item.price || 0), 0)
)

const finalAmount = computed(() => {
  const total = totalAmount.value
  const discount = parseFloat(form.value.discount) || 0
  return Math.max(0, total - discount).toFixed(2)
})

const calcTotal = () => {
  // 触发计算
}

const onCustomerConfirm = ({ selectedOptions }) => {
  const customer = customers.value.find(c => c.id === selectedOptions[0].value)
  if (customer) {
    form.value.customer_id = customer.id
    form.value.customer_name = customer.name
    form.value.address = customer.address || '暂无地址'
  }
  showCustomerPopup.value = false
}

const handleSubmit = async () => {
  if (!form.value.customer_id) {
    showToast('请选择客户')
    return
  }
  if (totalQty.value === 0) {
    showToast('请选择商品')
    return
  }
  loading.value = true
  try {
    const items = form.value.items
      .filter(item => item.quantity > 0)
      .map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        price: item.price
      }))
    await createSalesOrder({
      customer_id: form.value.customer_id,
      items,
      remark: `折扣:${form.value.discount}`
    })
    showSuccessToast('下单成功')
    router.back()
  } catch (e) {
    showToast('下单失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const [cRes, pRes] = await Promise.all([
      getCustomers(),
      getProducts()
    ])
    customers.value = cRes.data || []
    form.value.items = (pRes.data || []).map(p => ({
      product_id: p.id,
      product_name: p.name,
      price: p.default_price || p.price || 0,
      quantity: 0
    }))
    if (customers.value.length > 0) {
      const first = customers.value[0]
      form.value.customer_id = first.id
      form.value.customer_name = first.name
      form.value.address = first.address || ''
    }
  } catch (e) {
    showToast('加载失败')
  }
})
</script>

<style scoped>
.order-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 80px; }
.customer-card, .product-card, .summary-card { margin: 12px; }
.card-label { font-size: 14px; font-weight: bold; color: #333; margin-bottom: 8px; padding-left: 4px; }
.product-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.product-item:last-child { border-bottom: none; }
.product-info { flex: 1; }
.product-name { font-size: 14px; color: #333; }
.product-price { font-size: 13px; color: #ff6b35; margin-top: 4px; }
.orange { color: #ff6b35; font-weight: bold; }
.submit-bar {
  position: fixed;
  bottom: 50px;
  left: 0;
  right: 0;
  background: #fff;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
}
.total-info { font-size: 14px; color: #666; }
.total-price { font-size: 20px; color: #ff6b35; font-weight: bold; }
.submit-bar :deep(.van-button) { flex: 1; }
</style>