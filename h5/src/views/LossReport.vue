<template>
  <div class="loss-page">
    <van-nav-bar title="报损单" left-arrow @click-left="$router.back()" />

    <!-- 报损信息 -->
    <van-cell-group inset title="报损信息">
      <van-cell title="仓库" is-link :value="form.warehouse_name || '请选择'" @click="showWarehouse = true" />
      <van-field v-model="form.reason" label="报损原因" placeholder="请输入原因" rows="2" autosize type="textarea" />
      <van-field v-model="form.remark" label="备注" placeholder="备注信息" rows="2" autosize type="textarea" />
    </van-cell-group>

    <!-- 商品明细 -->
    <van-cell-group inset title="商品明细">
      <div v-for="(item, index) in form.items" :key="index" class="product-item">
        <div class="product-info">
          <div class="product-name">{{ item.product_name }}</div>
          <div class="product-stock">库存: {{ item.stock || 0 }}</div>
        </div>
        <van-stepper v-model="item.quantity" min="0" @change="calcTotal" />
      </div>
    </van-cell-group>

    <!-- 提交 -->
    <div class="submit-bar">
      <van-button type="danger" size="large" block :loading="loading" @click="handleSubmit">提交报损</van-button>
    </div>

    <!-- 仓库选择弹窗 -->
    <van-popup v-model:show="showWarehouse" position="bottom" round>
      <van-picker title="选择仓库" :columns="warehouseColumns" @confirm="onWarehouseConfirm" @cancel="showWarehouse = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import { useRouter } from 'vue-router'
import { getWarehouses, getProducts } from '../api'
import api from '../api'

const router = useRouter()
const loading = ref(false)
const showWarehouse = ref(false)

const warehouses = ref([])
const warehouseColumns = computed(() => warehouses.value.map(w => ({ text: w.name, value: w.id })))

const form = ref({
  warehouse_id: null,
  warehouse_name: '',
  reason: '',
  remark: '',
  items: []
})

const onWarehouseConfirm = ({ selectedOptions }) => {
  const wh = warehouses.value.find(w => w.id === selectedOptions[0].value)
  if (wh) {
    form.value.warehouse_id = wh.id
    form.value.warehouse_name = wh.name
  }
  showWarehouse.value = false
}

const calcTotal = () => {}

const handleSubmit = async () => {
  if (!form.value.warehouse_id) {
    showToast('请选择仓库')
    return
  }
  if (!form.value.reason) {
    showToast('请输入报损原因')
    return
  }
  const validItems = form.value.items.filter(i => i.quantity > 0)
  if (validItems.length === 0) {
    showToast('请输入报损数量')
    return
  }
  loading.value = true
  try {
    for (const item of validItems) {
      await api.post('/inventory/other-out', {
        warehouse_id: form.value.warehouse_id,
        product_id: item.product_id,
        quantity: item.quantity,
        reason: form.value.reason,
        remark: form.value.remark
      })
    }
    showSuccessToast('报损成功')
    router.back()
  } catch (e) {
    showToast('报损失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const [wRes, pRes] = await Promise.all([getWarehouses(), getProducts()])
    warehouses.value = wRes.data || []
    form.value.items = (pRes.data || []).map(p => ({
      product_id: p.id,
      product_name: p.name,
      stock: p.stock || 0,
      quantity: 0
    }))
  } catch (e) {
    showToast('加载失败')
  }
})
</script>

<style scoped>
.loss-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 80px; }
.product-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.product-item:last-child { border-bottom: none; }
.product-info { flex: 1; }
.product-name { font-size: 14px; color: #333; }
.product-stock { font-size: 12px; color: #999; margin-top: 4px; }
.submit-bar { position: fixed; bottom: 50px; left: 0; right: 0; background: #fff; padding: 12px 16px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
</style>