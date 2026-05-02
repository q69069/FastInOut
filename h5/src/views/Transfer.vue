<template>
  <div class="transfer-page">
    <van-nav-bar title="调拨单" left-arrow @click-left="$router.back()" />

    <!-- 调拨信息 -->
    <van-cell-group inset title="调拨信息">
      <van-cell title="调出仓库" is-link :value="form.from_warehouse_name || '请选择'" @click="showFromWarehouse = true" />
      <van-cell title="调入仓库" is-link :value="form.to_warehouse_name || '请选择'" @click="showToWarehouse = true" />
      <van-field v-model="form.remark" label="备注" placeholder="请输入备注" rows="2" autosize type="textarea" />
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
      <van-button type="primary" size="large" block :loading="loading" @click="handleSubmit">提交调拨</van-button>
    </div>

    <!-- 仓库选择弹窗 -->
    <van-popup v-model:show="showFromWarehouse" position="bottom" round>
      <van-picker title="选择调出仓库" :columns="warehouseColumns" @confirm="onFromWarehouseConfirm" @cancel="showFromWarehouse = false" />
    </van-popup>
    <van-popup v-model:show="showToWarehouse" position="bottom" round>
      <van-picker title="选择调入仓库" :columns="warehouseColumns" @confirm="onToWarehouseConfirm" @cancel="showToWarehouse = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import { useRouter, useRoute } from 'vue-router'
import { getWarehouses, getProducts, createTransfer } from '../api'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const showFromWarehouse = ref(false)
const showToWarehouse = ref(false)

const warehouses = ref([])
const warehouseColumns = computed(() => warehouses.value.map(w => ({ text: w.name, value: w.id })))

const form = ref({
  from_warehouse_id: null,
  from_warehouse_name: '',
  to_warehouse_id: null,
  to_warehouse_name: '',
  remark: '',
  items: []
})

const onFromWarehouseConfirm = ({ selectedOptions }) => {
  const wh = warehouses.value.find(w => w.id === selectedOptions[0].value)
  if (wh) {
    form.value.from_warehouse_id = wh.id
    form.value.from_warehouse_name = wh.name
  }
  showFromWarehouse.value = false
}

const onToWarehouseConfirm = ({ selectedOptions }) => {
  const wh = warehouses.value.find(w => w.id === selectedOptions[0].value)
  if (wh) {
    form.value.to_warehouse_id = wh.id
    form.value.to_warehouse_name = wh.name
  }
  showToWarehouse.value = false
}

const calcTotal = () => {}

const handleSubmit = async () => {
  if (!form.value.from_warehouse_id) {
    showToast('请选择调出仓库')
    return
  }
  if (!form.value.to_warehouse_id) {
    showToast('请选择调入仓库')
    return
  }
  if (form.value.from_warehouse_id === form.value.to_warehouse_id) {
    showToast('调出和调入仓库不能相同')
    return
  }
  const validItems = form.value.items.filter(i => i.quantity > 0)
  if (validItems.length === 0) {
    showToast('请输入调拨数量')
    return
  }
  loading.value = true
  try {
    await createTransfer({
      from_warehouse_id: form.value.from_warehouse_id,
      to_warehouse_id: form.value.to_warehouse_id,
      remark: form.value.remark,
      items: validItems.map(i => ({ product_id: i.product_id, quantity: i.quantity }))
    })
    showSuccessToast('调拨成功')
    router.back()
  } catch (e) {
    showToast('调拨失败')
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
.transfer-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 80px; }
.product-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.product-item:last-child { border-bottom: none; }
.product-info { flex: 1; }
.product-name { font-size: 14px; color: #333; }
.product-stock { font-size: 12px; color: #999; margin-top: 4px; }
.submit-bar { position: fixed; bottom: 50px; left: 0; right: 0; background: #fff; padding: 12px 16px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
</style>