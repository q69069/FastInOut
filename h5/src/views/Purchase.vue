<template>
  <div class="purchase-page">
    <van-nav-bar title="采购开单" left-arrow @click-left="$router.back()" />

    <!-- 供应商信息 -->
    <div class="supplier-card">
      <div class="card-label">供应商信息</div>
      <van-cell-group inset>
        <van-cell title="供应商" is-link :value="form.supplier_name || '请选择供应商'" @click="showSupplierPopup = true" />
        <van-cell title="收货仓库" is-link :value="form.warehouse_name || '请选择仓库'" @click="showWarehousePopup = true" />
      </van-cell-group>
    </div>

    <!-- 商品列表 -->
    <div class="product-card">
      <div class="card-label">商品明细</div>
      <van-cell-group inset>
        <div v-for="(item, index) in form.items" :key="index" class="product-item">
          <div class="product-info">
            <div class="product-name">{{ item.product_name }}</div>
            <div class="product-price">¥{{ item.price }} / {{ item.unit }}</div>
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
        <van-cell title="采购金额">
          <template #value><span class="orange">¥{{ totalAmount }}</span></template>
        </van-cell>
        <van-field v-model="form.remark" label="备注" placeholder="备注信息" rows="2" autosize type="textarea" />
      </van-cell-group>
    </div>

    <!-- 提交按钮 -->
    <div class="submit-bar">
      <div class="total-info">
        <span>合计：</span>
        <span class="total-price">¥{{ totalAmount }}</span>
      </div>
      <van-button type="primary" size="large" :loading="loading" @click="handleSubmit">提交采购</van-button>
    </div>

    <!-- 供应商选择弹窗 -->
    <van-popup v-model:show="showSupplierPopup" position="bottom" round>
      <van-picker title="选择供应商" :columns="supplierColumns" @confirm="onSupplierConfirm" @cancel="showSupplierPopup = false" />
    </van-popup>

    <!-- 仓库选择弹窗 -->
    <van-popup v-model:show="showWarehousePopup" position="bottom" round>
      <van-picker title="选择仓库" :columns="warehouseColumns" @confirm="onWarehouseConfirm" @cancel="showWarehousePopup = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import { useRouter, useRoute } from 'vue-router'
import { getSuppliers, getWarehouses, getProducts, createPurchase } from '../api'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const showSupplierPopup = ref(false)
const showWarehousePopup = ref(false)

const suppliers = ref([])
const warehouses = ref([])
const supplierColumns = computed(() => suppliers.value.map(s => ({ text: s.name, value: s.id })))
const warehouseColumns = computed(() => warehouses.value.map(w => ({ text: w.name, value: w.id })))

const form = ref({
  supplier_id: null,
  supplier_name: '',
  warehouse_id: null,
  warehouse_name: '',
  remark: '',
  items: []
})

const totalQty = computed(() => form.value.items.reduce((sum, item) => sum + (item.quantity || 0), 0))
const totalAmount = computed(() => form.value.items.reduce((sum, item) => sum + (item.quantity || 0) * (item.price || 0), 0).toFixed(2))

const calcTotal = () => {}

const onSupplierConfirm = ({ selectedOptions }) => {
  const supplier = suppliers.value.find(s => s.id === selectedOptions[0].value)
  if (supplier) {
    form.value.supplier_id = supplier.id
    form.value.supplier_name = supplier.name
  }
  showSupplierPopup.value = false
}

const onWarehouseConfirm = ({ selectedOptions }) => {
  const wh = warehouses.value.find(w => w.id === selectedOptions[0].value)
  if (wh) {
    form.value.warehouse_id = wh.id
    form.value.warehouse_name = wh.name
  }
  showWarehousePopup.value = false
}

const handleSubmit = async () => {
  if (!form.value.supplier_id) {
    showToast('请选择供应商')
    return
  }
  if (!form.value.warehouse_id) {
    showToast('请选择仓库')
    return
  }
  if (totalQty.value === 0) {
    showToast('请选择商品')
    return
  }
  loading.value = true
  try {
    const items = form.value.items.filter(item => item.quantity > 0).map(item => ({
      product_id: item.product_id,
      quantity: item.quantity,
      price: item.price
    }))
    await createPurchase({
      supplier_id: form.value.supplier_id,
      warehouse_id: form.value.warehouse_id,
      remark: form.value.remark,
      items
    })
    showSuccessToast('采购成功')
    router.back()
  } catch (e) {
    showToast('采购失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const [sRes, wRes, pRes] = await Promise.all([getSuppliers(), getWarehouses(), getProducts()])
    suppliers.value = sRes.data || []
    warehouses.value = wRes.data || []
    form.value.items = (pRes.data || []).map(p => ({
      product_id: p.id,
      product_name: p.name,
      price: p.purchase_price || 0,
      unit: p.unit || '个',
      quantity: 0
    }))
  } catch (e) {
    showToast('加载失败')
  }
})
</script>

<style scoped>
.purchase-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 80px; }
.supplier-card, .product-card, .summary-card { margin: 12px; }
.card-label { font-size: 14px; font-weight: bold; color: #333; margin-bottom: 8px; padding-left: 4px; }
.product-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.product-item:last-child { border-bottom: none; }
.product-info { flex: 1; }
.product-name { font-size: 14px; color: #333; }
.product-price { font-size: 13px; color: #07c160; margin-top: 4px; }
.orange { color: #ff6b35; font-weight: bold; }
.submit-bar { position: fixed; bottom: 50px; left: 0; right: 0; background: #fff; padding: 12px 16px; display: flex; align-items: center; gap: 12px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
.total-info { font-size: 14px; color: #666; }
.total-price { font-size: 20px; color: #ff6b35; font-weight: bold; }
.submit-bar :deep(.van-button) { flex: 1; }
</style>