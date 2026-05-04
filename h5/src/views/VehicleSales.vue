<template>
  <div class="page">
    <van-nav-bar title="车销开单" left-arrow @click-left="$router.back()" />

    <!-- 车仓选择 -->
    <van-cell-group inset style="margin:12px 0">
      <van-cell title="当前车仓" is-link :value="selectedVehicleWh?.name || '请选择车仓'" @click="showVehiclePicker = true" />
      <van-cell v-if="selectedVehicleWh" title="车牌" :value="selectedVehicleWh.plate_number || '-'" />
    </van-cell-group>

    <!-- 客户选择 -->
    <van-cell-group inset style="margin:0 0 12px">
      <van-cell title="客户" is-link :value="form.customer_name || '请选择客户'" @click="showCustomerPicker = true" />
    </van-cell-group>

    <!-- 车上库存商品列表 -->
    <div style="padding:0 16px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span style="font-weight:bold">车上商品</span>
        <van-tag type="primary">库存: {{ vehicleInventory.length }} 种</van-tag>
      </div>

      <van-cell-group v-for="item in vehicleInventory" :key="item.product_id">
        <van-cell :title="item.product_name" :label="'库存: ' + item.stock + ' | 单价: ¥' + (item.price || 0).toFixed(2)">
          <template #value>
            <van-stepper v-model="item.quantity" min="0" :max="item.stock" />
          </template>
        </van-cell>
      </van-cell-group>

      <van-empty v-if="vehicleInventory.length === 0 && selectedVehicleWh" description="车上无库存，请先装车" />
      <van-empty v-if="!selectedVehicleWh" description="请先选择车仓" />
    </div>

    <!-- 收款方式 -->
    <van-cell-group inset style="margin:12px 0" v-if="totalAmount > 0">
      <van-cell title="合计金额">
        <template #value><span style="color:#ee0a24;font-size:18px;font-weight:bold">¥{{ totalAmount.toFixed(2) }}</span></template>
      </van-cell>
      <van-cell title="现金收款">
        <template #extra>
          <van-field v-model.number="form.cash_amount" type="number" input-align="right" placeholder="0" style="width:100px" />
        </template>
      </van-cell>
      <van-cell title="微信收款">
        <template #extra>
          <van-field v-model.number="form.wechat_amount" type="number" input-align="right" placeholder="0" style="width:100px" />
        </template>
      </van-cell>
      <van-cell title="支付宝收款">
        <template #extra>
          <van-field v-model.number="form.alipay_amount" type="number" input-align="right" placeholder="0" style="width:100px" />
        </template>
      </van-cell>
      <van-cell title="赊账金额">
        <template #extra>
          <van-field v-model.number="form.credit_amount" type="number" input-align="right" placeholder="0" style="width:100px" />
        </template>
      </van-cell>
      <van-cell title="收款合计" :value="'¥' + totalPaid.toFixed(2)" />
    </van-cell-group>

    <!-- 提交 -->
    <div style="padding:16px" v-if="totalAmount > 0">
      <van-button type="primary" block size="large" :loading="submitting" @click="handleSubmit">
        确认开单 (¥{{ totalAmount.toFixed(2) }})
      </van-button>
    </div>

    <!-- 今日开单记录 -->
    <van-cell-group inset title="今日开单" style="margin:12px 0">
      <van-cell v-for="d in todayDeliveries" :key="d.id"
        :title="d.delivery_no"
        :label="d.customer_name + ' | ' + d.created_at?.substring(11, 16)"
        :value="'¥' + (d.total_amount || 0).toFixed(2)"
        is-link @click="showDeliveryDetail(d)" />
      <van-empty v-if="todayDeliveries.length === 0" description="今日暂无开单" image="default" />
    </van-cell-group>

    <!-- 车仓选择 -->
    <van-popup v-model:show="showVehiclePicker" position="bottom" round>
      <van-picker title="选择车仓" :columns="vehicleColumns" @confirm="onVehicleConfirm" @cancel="showVehiclePicker = false" />
    </van-popup>

    <!-- 客户选择 -->
    <van-popup v-model:show="showCustomerPicker" position="bottom" round>
      <van-picker title="选择客户" :columns="customerColumns" @confirm="onCustomerConfirm" @cancel="showCustomerPicker = false" />
    </van-popup>

    <!-- 详情弹窗 -->
    <van-popup v-model:show="showDetailPopup" position="bottom" round style="max-height:70%">
      <div style="padding:16px" v-if="deliveryDetail">
        <h3>{{ deliveryDetail.delivery_no }}</h3>
        <van-cell-group style="margin-top:12px">
          <van-cell title="客户" :value="deliveryDetail.customer_name" />
          <van-cell title="总金额" :value="'¥' + (deliveryDetail.total_amount || 0).toFixed(2)" />
          <van-cell title="现金" :value="'¥' + (deliveryDetail.cash_amount || 0).toFixed(2)" />
          <van-cell title="微信" :value="'¥' + (deliveryDetail.wechat_amount || 0).toFixed(2)" />
          <van-cell title="支付宝" :value="'¥' + (deliveryDetail.alipay_amount || 0).toFixed(2)" />
          <van-cell title="赊账" :value="'¥' + (deliveryDetail.credit_amount || 0).toFixed(2)" />
          <van-cell title="状态">
            <template #value><van-tag :type="deliveryDetail.status === 'voided' ? 'danger' : 'success'">{{ deliveryDetail.status_text || deliveryDetail.status }}</van-tag></template>
          </van-cell>
        </van-cell-group>
        <van-button v-if="deliveryDetail.status === 'pending'" block type="danger" plain style="margin-top:12px" @click="handleVoid(deliveryDetail)">
          作废此单
        </van-button>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getWarehouses, getCustomers, getProducts, getInventory, createSalesDelivery, getSalesDeliveries, voidSalesDelivery } from '../api'

const showVehiclePicker = ref(false)
const showCustomerPicker = ref(false)
const showDetailPopup = ref(false)
const submitting = ref(false)

const vehicleWarehouses = ref([])
const customers = ref([])
const selectedVehicleWh = ref(null)
const vehicleInventory = ref([])
const todayDeliveries = ref([])
const deliveryDetail = ref(null)

const form = ref({
  customer_id: null, customer_name: '',
  cash_amount: 0, wechat_amount: 0, alipay_amount: 0, credit_amount: 0
})

const vehicleColumns = computed(() =>
  vehicleWarehouses.value.map(w => ({ text: w.name + (w.plate_number ? ` (${w.plate_number})` : ''), value: w.id }))
)
const customerColumns = computed(() =>
  customers.value.map(c => ({ text: c.name, value: c.id }))
)

const totalAmount = computed(() =>
  vehicleInventory.value.reduce((sum, item) => sum + (item.quantity || 0) * (item.price || 0), 0)
)
const totalPaid = computed(() =>
  (form.value.cash_amount || 0) + (form.value.wechat_amount || 0) + (form.value.alipay_amount || 0) + (form.value.credit_amount || 0)
)

const onVehicleConfirm = async ({ selectedOptions }) => {
  const wh = vehicleWarehouses.value.find(w => w.id === selectedOptions[0].value)
  selectedVehicleWh.value = wh
  showVehiclePicker.value = false
  await loadVehicleInventory()
}

const onCustomerConfirm = ({ selectedOptions }) => {
  const c = customers.value.find(c => c.id === selectedOptions[0].value)
  form.value.customer_id = c?.id
  form.value.customer_name = c?.name
  showCustomerPicker.value = false
}

const loadVehicleInventory = async () => {
  if (!selectedVehicleWh.value) return
  try {
    const res = await getInventory({ warehouse_id: selectedVehicleWh.value.id, page_size: 500 })
    vehicleInventory.value = (res.data || []).map(inv => ({
      product_id: inv.product_id,
      product_name: inv.product_name || `商品#${inv.product_id}`,
      stock: inv.quantity || 0,
      price: inv.price || inv.unit_price || 0,
      quantity: 0
    }))
  } catch { vehicleInventory.value = [] }
}

const loadTodayDeliveries = async () => {
  try {
    const today = new Date().toISOString().substring(0, 10)
    const res = await getSalesDeliveries({ start_date: today, page_size: 50 })
    todayDeliveries.value = res.data || []
  } catch {}
}

const handleSubmit = async () => {
  if (!form.value.customer_id) return showToast('请选择客户')
  const items = vehicleInventory.value.filter(i => i.quantity > 0)
  if (!items.length) return showToast('请选择商品')

  submitting.value = true
  try {
    await createSalesDelivery({
      customer_id: form.value.customer_id,
      vehicle_id: selectedVehicleWh.value.id,
      total_amount: totalAmount.value,
      cash_amount: form.value.cash_amount || 0,
      wechat_amount: form.value.wechat_amount || 0,
      alipay_amount: form.value.alipay_amount || 0,
      credit_amount: form.value.credit_amount || 0,
      items: items.map(i => ({ product_id: i.product_id, quantity: i.quantity, unit_price: i.price }))
    })
    showSuccessToast('开单成功')
    form.value = { customer_id: null, customer_name: '', cash_amount: 0, wechat_amount: 0, alipay_amount: 0, credit_amount: 0 }
    await loadVehicleInventory()
    await loadTodayDeliveries()
  } catch { showToast('开单失败') }
  submitting.value = false
}

const showDeliveryDetail = async (d) => {
  deliveryDetail.value = d
  showDetailPopup.value = true
}

const handleVoid = async (d) => {
  try {
    await showConfirmDialog({ title: '作废确认', message: `确定作废 ${d.delivery_no}？库存将回滚` })
    await voidSalesDelivery(d.id, { reason: 'H5端作废' })
    showSuccessToast('已作废')
    showDetailPopup.value = false
    await loadVehicleInventory()
    await loadTodayDeliveries()
  } catch {}
}

onMounted(async () => {
  const [whRes, cRes] = await Promise.all([getWarehouses(), getCustomers()])
  vehicleWarehouses.value = (whRes.data || []).filter(w => w.warehouse_type === 'vehicle')
  customers.value = cRes.data || []
  await loadTodayDeliveries()
})
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
</style>
