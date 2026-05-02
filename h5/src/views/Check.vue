<template>
  <div class="check-page">
    <van-nav-bar title="库存盘点" left-arrow @click-left="$router.back()" />

    <!-- 盘点信息 -->
    <van-cell-group inset title="盘点信息">
      <van-cell title="仓库" is-link :value="form.warehouse_name || '请选择'" @click="showWarehouse = true" />
      <van-cell title="盘点日期" :value="form.check_date" @click="showDate = true" />
      <van-field v-model="form.remark" label="备注" placeholder="请输入备注" rows="2" autosize type="textarea" />
    </van-cell-group>

    <!-- 商品盘点明细 -->
    <van-cell-group inset title="商品明细">
      <div v-for="(item, index) in form.items" :key="index" class="product-item">
        <div class="product-info">
          <div class="product-name">{{ item.product_name }}</div>
          <div class="product-stock">系统库存: {{ item.system_stock || 0 }}</div>
        </div>
        <div class="stock-input">
          <span class="input-label">盘点数量</span>
          <van-stepper v-model="item.actual_stock" min="0" />
        </div>
      </div>
    </van-cell-group>

    <!-- 提交 -->
    <div class="submit-bar">
      <van-button type="primary" size="large" block :loading="loading" @click="handleSubmit">提交盘点</van-button>
    </div>

    <!-- 仓库选择弹窗 -->
    <van-popup v-model:show="showWarehouse" position="bottom" round>
      <van-picker title="选择仓库" :columns="warehouseColumns" @confirm="onWarehouseConfirm" @cancel="showWarehouse = false" />
    </van-popup>

    <!-- 日期选择 -->
    <van-popup v-model:show="showDate" position="bottom" round>
      <van-date-picker v-model="currentDate" @confirm="onDateConfirm" @cancel="showDate = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import { useRouter } from 'vue-router'
import { getWarehouses, getProducts, createInventoryCheck } from '../api'

const router = useRouter()
const loading = ref(false)
const showWarehouse = ref(false)
const showDate = ref(false)
const currentDate = ref(['2026', '05', '02'])

const warehouses = ref([])
const warehouseColumns = computed(() => warehouses.value.map(w => ({ text: w.name, value: w.id })))

const form = ref({
  warehouse_id: null,
  warehouse_name: '',
  check_date: '2026-05-02',
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

const onDateConfirm = ({ selectedOptions }) => {
  form.value.check_date = selectedOptions.map(s => s.value).join('-')
  showDate.value = false
}

const handleSubmit = async () => {
  if (!form.value.warehouse_id) {
    showToast('请选择仓库')
    return
  }
  loading.value = true
  try {
    const items = form.value.items
      .filter(i => i.actual_stock >= 0)
      .map(i => ({
        product_id: i.product_id,
        system_stock: i.system_stock || 0,
        actual_stock: i.actual_stock
      }))
    await createInventoryCheck({
      warehouse_id: form.value.warehouse_id,
      check_date: form.value.check_date,
      remark: form.value.remark,
      items
    })
    showSuccessToast('盘点成功')
    router.back()
  } catch (e) {
    showToast('盘点失败')
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
      system_stock: p.stock || 0,
      actual_stock: p.stock || 0
    }))
  } catch (e) {
    showToast('加载失败')
  }
})
</script>

<style scoped>
.check-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 80px; }
.product-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.product-item:last-child { border-bottom: none; }
.product-info { flex: 1; }
.product-name { font-size: 14px; color: #333; }
.product-stock { font-size: 12px; color: #999; margin-top: 4px; }
.stock-input { display: flex; align-items: center; gap: 8px; }
.input-label { font-size: 12px; color: #666; }
.submit-bar { position: fixed; bottom: 50px; left: 0; right: 0; background: #fff; padding: 12px 16px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
</style>