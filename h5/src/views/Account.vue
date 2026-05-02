<template>
  <div class="account-page">
    <van-nav-bar title="往来账" />

    <!-- 客户/供应商切换 -->
    <div class="type-tabs">
      <div :class="['type-tab', { active: accountType === 'customer' }]" @click="accountType = 'customer'">客户往来</div>
      <div :class="['type-tab', { active: accountType === 'supplier' }]" @click="accountType = 'supplier'">供应商往来</div>
    </div>

    <!-- 筛选 -->
    <div class="filter-section">
      <van-cell-group inset>
        <van-cell title="选择对象" is-link :value="selectedName || '请选择'" @click="showPicker = true" />
        <van-cell title="日期范围">
          <template #value>
            <span @click="showDateRange = true" class="date-range">{{ dateRange[0] }} 至 {{ dateRange[1] }}</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 汇总信息 -->
    <div class="summary-card">
      <div class="summary-row">
        <span class="summary-label">期初余额</span>
        <span :class="['summary-value', { red: initialBalance < 0 }]">¥{{ initialBalance }}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">应收/应付增加</span>
        <span class="summary-value green">+¥{{ increaseAmount }}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">应收/应付减少</span>
        <span class="summary-value orange">-¥{{ decreaseAmount }}</span>
      </div>
      <div class="summary-row total">
        <span class="summary-label">当前余额</span>
        <span :class="['summary-value', { red: currentBalance < 0 }]">¥{{ currentBalance }}</span>
      </div>
    </div>

    <!-- 明细记录 -->
    <div class="detail-section">
      <div class="section-title">明细记录</div>
      <van-cell-group inset>
        <van-cell v-for="item in details" :key="item.id">
          <template #title>
            <div class="detail-title">{{ item.type === '应收' ? '应收' : '应付' }} {{ item.amount }}</div>
            <div class="detail-desc">{{ item.remark || item.type }}</div>
          </template>
          <template #value>
            <div class="detail-balance" :class="{ red: item.balance < 0 }">余额: ¥{{ item.balance }}</div>
            <div class="detail-date">{{ item.date }}</div>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 对象选择弹窗 -->
    <van-popup v-model:show="showPicker" position="bottom" round>
      <van-picker :title="accountType === 'customer' ? '选择客户' : '选择供应商'" :columns="columns" @confirm="onConfirm" @cancel="showPicker = false" />
    </van-popup>

    <!-- 日期范围选择 -->
    <van-popup v-model:show="showDateRange" position="bottom" round>
      <van-date-picker type="range" v-model="dateRangePicker" @confirm="onDateConfirm" @cancel="showDateRange = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { getCustomerAccounts, getSupplierAccounts } from '../api'

const accountType = ref('customer')
const showPicker = ref(false)
const showDateRange = ref(false)
const selectedId = ref(null)
const selectedName = ref('')

const dateRange = ref(['2026-01-01', '2026-05-02'])
const dateRangePicker = ref(['2026-01-01', '2026-05-02'])

const initialBalance = ref('0.00')
const increaseAmount = ref('0.00')
const decreaseAmount = ref('0.00')
const currentBalance = ref('0.00')
const details = ref([])

const customers = ref([])
const suppliers = ref([])

const columns = computed(() => {
  const list = accountType.value === 'customer' ? customers.value : suppliers.value
  return list.map(i => ({ text: i.name, value: i.id }))
})

watch(accountType, async () => {
  selectedId.value = null
  selectedName.value = ''
  await loadObjects()
  if (selectedId.value) {
    await loadData()
  }
})

const onConfirm = ({ selectedOptions }) => {
  const list = accountType.value === 'customer' ? customers.value : suppliers.value
  const obj = list.find(i => i.id === selectedOptions[0].value)
  if (obj) {
    selectedId.value = obj.id
    selectedName.value = obj.name
  }
  showPicker.value = false
  loadData()
}

const onDateConfirm = ({ selectedOptions }) => {
  dateRange.value = selectedOptions
  showDateRange.value = false
  if (selectedId.value) {
    loadData()
  }
}

const loadData = async () => {
  if (!selectedId.value) return
  try {
    const params = {
      type: accountType.value,
      id: selectedId.value,
      start_date: dateRange.value[0],
      end_date: dateRange.value[1]
    }
    const res = accountType.value === 'customer'
      ? await getCustomerAccounts(params)
      : await getSupplierAccounts(params)
    initialBalance.value = res.data?.initial || '0.00'
    increaseAmount.value = res.data?.increase || '0.00'
    decreaseAmount.value = res.data?.decrease || '0.00'
    currentBalance.value = res.data?.balance || '0.00'
    details.value = res.data?.details || []
  } catch (e) {
    details.value = []
  }
}

const loadObjects = async () => {
  // 实际应该调用API获取客户/供应商列表
  // 这里模拟数据
  if (accountType.value === 'customer') {
    customers.value = [
      { id: 1, name: '客户A' },
      { id: 2, name: '客户B' }
    ]
  } else {
    suppliers.value = [
      { id: 1, name: '供应商A' },
      { id: 2, name: '供应商B' }
    ]
  }
}

onMounted(loadObjects)
</script>

<style scoped>
.account-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.type-tabs { display: flex; background: #fff; padding: 12px; gap: 8px; }
.type-tab { flex: 1; text-align: center; padding: 10px 0; border-radius: 20px; font-size: 14px; color: #666; background: #f5f5f5; }
.type-tab.active { background: #1989fa; color: #fff; }
.filter-section { margin: 12px; }
.date-range { color: #1989fa; }
.summary-card { background: #fff; margin: 12px; border-radius: 12px; padding: 16px; }
.summary-row { display: flex; justify-content: space-between; padding: 8px 0; }
.summary-row.total { border-top: 1px solid #eee; margin-top: 8px; padding-top: 12px; }
.summary-label { font-size: 14px; color: #666; }
.summary-value { font-size: 14px; font-weight: bold; color: #333; }
.green { color: #07c160; }
.orange { color: #ff9a56; }
.red { color: #ee0a24; }
.detail-section { margin: 12px; }
.section-title { font-size: 15px; font-weight: bold; color: #333; margin-bottom: 8px; padding-left: 4px; }
.detail-title { font-size: 14px; color: #333; }
.detail-desc { font-size: 12px; color: #999; margin-top: 2px; }
.detail-balance { font-size: 13px; color: #333; }
.detail-date { font-size: 12px; color: #999; margin-top: 2px; }
</style>