<template>
  <div class="page">
    <van-nav-bar title="装车单" left-arrow @click-left="$router.back()" />

    <!-- 装车单列表 -->
    <div v-if="!showCreate" class="load-list">
      <van-button type="primary" block style="margin:12px 16px;width:calc(100% - 32px)" @click="showCreate = true">
        新建装车单
      </van-button>

      <van-pull-refresh v-model="refreshing" @refresh="loadData">
        <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="loadData">
          <van-cell-group v-for="item in list" :key="item.id" style="margin:8px 12px">
            <van-cell :title="item.code" :label="'状态: ' + (item.status_text || item.status)">
              <template #value>
                <van-tag :type="loadStatusType(item.status)">{{ item.status_text || item.status }}</van-tag>
              </template>
            </van-cell>
            <van-cell title="源仓库" :value="item.from_warehouse_name || '-'" />
            <van-cell title="车仓" :value="item.vehicle_warehouse_name || '-'" />
            <van-cell title="总金额" :value="'¥' + (item.total_amount || 0).toFixed(2)" />
            <van-cell title="创建时间" :value="item.created_at" />
            <div style="padding:8px 16px;display:flex;gap:8px">
              <van-button v-if="item.status === 'draft'" size="small" type="primary" @click="handleConfirm(item)">确认装车</van-button>
              <van-button v-if="item.status === 'loaded'" size="small" type="warning" @click="handleReturn(item)">退库</van-button>
              <van-button size="small" @click="showDetail(item)">详情</van-button>
            </div>
          </van-cell-group>
        </van-list>
      </van-pull-refresh>
    </div>

    <!-- 新建装车单 -->
    <div v-else class="create-form">
      <van-cell-group inset style="margin:12px 0">
        <van-cell title="源仓库" is-link :value="form.from_warehouse_name || '请选择'" @click="showFromWhPicker = true" />
        <van-cell title="车仓(目标)" is-link :value="form.vehicle_warehouse_name || '请选择'" @click="showVehicleWhPicker = true" />
      </van-cell-group>

      <div style="padding:0 16px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <span style="font-weight:bold">装车商品</span>
          <van-button size="small" type="primary" @click="showProductPicker = true">添加商品</van-button>
        </div>

        <van-cell-group v-for="(item, idx) in form.items" :key="idx">
          <van-cell :title="item.product_name" :label="'单价: ¥' + (item.unit_price || 0).toFixed(2)">
            <template #value>
              <van-stepper v-model="item.quantity" min="1" />
            </template>
          </van-cell>
          <van-cell>
            <template #value>
              <van-button size="small" type="danger" plain @click="form.items.splice(idx, 1)">删除</van-button>
            </template>
          </van-cell>
        </van-cell-group>

        <van-empty v-if="form.items.length === 0" description="请添加装车商品" image="search" />
      </div>

      <div style="padding:16px;display:flex;gap:8px">
        <van-button block @click="showCreate = false">取消</van-button>
        <van-button type="primary" block :loading="submitting" @click="handleCreate">提交装车单</van-button>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <van-popup v-model:show="showDetailPopup" position="bottom" round style="max-height:80%">
      <div style="padding:16px" v-if="detail">
        <h3 style="margin-bottom:12px">{{ detail.code }}</h3>
        <van-cell-group>
          <van-cell title="源仓库" :value="detail.from_warehouse_name || '-'" />
          <van-cell title="车仓" :value="detail.vehicle_warehouse_name || '-'" />
          <van-cell title="状态" :value="detail.status_text || detail.status" />
          <van-cell title="总金额" :value="'¥' + (detail.total_amount || 0).toFixed(2)" />
        </van-cell-group>
        <van-cell-group title="装车明细" style="margin-top:12px">
          <van-cell v-for="item in detail.items" :key="item.id"
            :title="item.product_name"
            :label="'单价: ¥' + (item.unit_price || 0).toFixed(2)"
            :value="'x' + item.quantity" />
        </van-cell-group>
      </div>
    </van-popup>

    <!-- 源仓库选择 -->
    <van-popup v-model:show="showFromWhPicker" position="bottom" round>
      <van-picker title="选择源仓库" :columns="warehouseColumns" @confirm="onFromWhConfirm" @cancel="showFromWhPicker = false" />
    </van-popup>

    <!-- 车仓选择 -->
    <van-popup v-model:show="showVehicleWhPicker" position="bottom" round>
      <van-picker title="选择车仓" :columns="vehicleWarehouseColumns" @confirm="onVehicleWhConfirm" @cancel="showVehicleWhPicker = false" />
    </van-popup>

    <!-- 商品选择 -->
    <van-popup v-model:show="showProductPicker" position="bottom" round style="max-height:70%">
      <van-search v-model="productSearch" placeholder="搜索商品" />
      <van-list>
        <van-cell v-for="p in filteredProducts" :key="p.id"
          :title="p.name" :label="'¥' + (p.default_price || p.price || 0)"
          clickable @click="addProduct(p)" />
      </van-list>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getVehicleLoads, createVehicleLoad, getVehicleLoad, confirmVehicleLoad, returnVehicleLoad, getWarehouses, getProducts } from '../api'

const refreshing = ref(false)
const loading = ref(false)
const finished = ref(false)
const list = ref([])
const page = ref(1)

const showCreate = ref(false)
const submitting = ref(false)
const form = ref({
  from_warehouse_id: null, from_warehouse_name: '',
  vehicle_warehouse_id: null, vehicle_warehouse_name: '',
  items: []
})

const showDetailPopup = ref(false)
const detail = ref(null)

const showFromWhPicker = ref(false)
const showVehicleWhPicker = ref(false)
const showProductPicker = ref(false)
const productSearch = ref('')

const warehouses = ref([])
const vehicleWarehouses = ref([])
const products = ref([])

const warehouseColumns = computed(() =>
  warehouses.value.filter(w => w.warehouse_type !== 'vehicle').map(w => ({ text: w.name, value: w.id }))
)
const vehicleWarehouseColumns = computed(() =>
  vehicleWarehouses.value.filter(w => w.warehouse_type === 'vehicle').map(w => ({ text: w.name + (w.plate_number ? ` (${w.plate_number})` : ''), value: w.id }))
)
const filteredProducts = computed(() => {
  if (!productSearch.value) return products.value
  return products.value.filter(p => p.name.includes(productSearch.value))
})

const loadStatusType = (status) => {
  const map = { draft: 'warning', pending: 'primary', loaded: 'success', returned: 'info' }
  return map[status] || 'info'
}

const loadData = async () => {
  try {
    const res = await getVehicleLoads({ page: page.value, page_size: 20 })
    if (page.value === 1) list.value = res.data || []
    else list.value.push(...(res.data || []))
    finished.value = (res.data || []).length < 20
    page.value++
  } catch { finished.value = true }
  loading.value = false
  refreshing.value = false
}

const onFromWhConfirm = ({ selectedOptions }) => {
  form.value.from_warehouse_id = selectedOptions[0].value
  form.value.from_warehouse_name = selectedOptions[0].text
  showFromWhPicker.value = false
}

const onVehicleWhConfirm = ({ selectedOptions }) => {
  form.value.vehicle_warehouse_id = selectedOptions[0].value
  form.value.vehicle_warehouse_name = selectedOptions[0].text
  showVehicleWhPicker.value = false
}

const addProduct = (p) => {
  const existing = form.value.items.find(i => i.product_id === p.id)
  if (existing) { existing.quantity++; showProductPicker.value = false; return }
  form.value.items.push({
    product_id: p.id, product_name: p.name,
    quantity: 1, unit_price: p.default_price || p.price || 0
  })
  showProductPicker.value = false
}

const handleCreate = async () => {
  if (!form.value.from_warehouse_id) return showToast('请选择源仓库')
  if (!form.value.vehicle_warehouse_id) return showToast('请选择车仓')
  if (!form.value.items.length) return showToast('请添加商品')

  submitting.value = true
  try {
    await createVehicleLoad({
      from_warehouse_id: form.value.from_warehouse_id,
      vehicle_warehouse_id: form.value.vehicle_warehouse_id,
      items: form.value.items.map(i => ({ product_id: i.product_id, quantity: i.quantity, unit_price: i.unit_price }))
    })
    showSuccessToast('装车单已创建')
    showCreate.value = false
    form.value = { from_warehouse_id: null, from_warehouse_name: '', vehicle_warehouse_id: null, vehicle_warehouse_name: '', items: [] }
    page.value = 1
    loadData()
  } catch { showToast('创建失败') }
  submitting.value = false
}

const handleConfirm = async (item) => {
  try {
    await showConfirmDialog({ title: '确认装车', message: '确认后库存将从源仓库转移到车仓' })
    await confirmVehicleLoad(item.id)
    showSuccessToast('装车确认成功')
    page.value = 1; loadData()
  } catch {}
}

const handleReturn = async (item) => {
  try {
    await showConfirmDialog({ title: '退库确认', message: '确认将车上库存退回仓库？' })
    await returnVehicleLoad(item.id)
    showSuccessToast('退库成功')
    page.value = 1; loadData()
  } catch {}
}

const showDetail = async (item) => {
  const res = await getVehicleLoad(item.id)
  detail.value = res.data
  showDetailPopup.value = true
}

onMounted(async () => {
  const res = await getWarehouses()
  const allWh = res.data || []
  warehouses.value = allWh
  vehicleWarehouses.value = allWh
  const pRes = await getProducts({ page_size: 500 })
  products.value = pRes.data || []
})
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; }
</style>
