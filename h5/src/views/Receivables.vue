<template>
  <div class="receivables-page">
    <van-nav-bar title="应收款管理" />

    <!-- 统计卡片 -->
    <div class="stats-card">
      <div class="stat-item">
        <div class="stat-value red">¥{{ totalReceivable }}</div>
        <div class="stat-label">应收总额</div>
      </div>
      <div class="stat-divider" />
      <div class="stat-item">
        <div class="stat-value orange">¥{{ receivedAmount }}</div>
        <div class="stat-label">已收金额</div>
      </div>
      <div class="stat-divider" />
      <div class="stat-item">
        <div class="stat-value">¥{{ outstandingAmount }}</div>
        <div class="stat-label">未收金额</div>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="filter-bar">
      <van-tag v-for="s in statusOptions" :key="s.value" :type="filterStatus === s.value ? 'primary' : 'default'" @click="filterStatus = s.value" size="large" class="filter-tag">
        {{ s.label }}
      </van-tag>
    </div>

    <!-- 应收列表 -->
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadData">
        <div v-for="item in filteredList" :key="item.id" class="receivable-card">
          <div class="card-header">
            <div class="customer-name">{{ item.customer_name }}</div>
            <van-tag :type="getStatusType(item.status)" size="small">{{ item.status }}</van-tag>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="info-label">应收金额</span>
              <span class="info-value red">¥{{ item.amount }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">已收金额</span>
              <span class="info-value">¥{{ item.received || 0 }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">单据日期</span>
              <span class="info-value">{{ item.date }}</span>
            </div>
            <div class="info-row" v-if="item.overdue_days > 0">
              <span class="info-label">逾期</span>
              <span class="info-value red">{{ item.overdue_days }}天</span>
            </div>
          </div>
          <div class="card-actions">
            <van-button v-if="item.status !== '已结清'" size="small" type="primary" @click="handleReceive(item)">收款</van-button>
            <van-button size="small" @click="handleDetail(item)">明细</van-button>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 收款弹窗 -->
    <van-popup v-model:show="showReceivePopup" position="bottom" round>
      <div class="receive-popup">
        <div class="popup-title">收款登记</div>
        <van-cell-group inset>
          <van-field v-model="receiveForm.amount" label="收款金额" type="number" placeholder="请输入收款金额" />
          <van-field v-model="receiveForm.remark" label="备注" placeholder="备注信息" />
        </van-cell-group>
        <div class="popup-actions">
          <van-button @click="showReceivePopup = false">取消</van-button>
          <van-button type="primary" @click="confirmReceive">确认</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast } from 'vant'
import { getReceivables, receivePayment } from '../api'

const loading = ref(false)
const finished = ref(false)
const filterStatus = ref('all')
const showReceivePopup = ref(false)
const currentItem = ref(null)

const list = ref([])
const totalReceivable = ref('0.00')
const receivedAmount = ref('0.00')
const outstandingAmount = ref('0.00')

const receiveForm = ref({ amount: '', remark: '' })

const statusOptions = [
  { label: '全部', value: 'all' },
  { label: '未结清', value: '未结清' },
  { label: '部分收款', value: '部分收款' },
  { label: '已结清', value: '已结清' }
]

const filteredList = computed(() => {
  if (filterStatus.value === 'all') return list.value
  return list.value.filter(i => i.status === filterStatus.value)
})

const getStatusType = (status) => {
  if (status === '已结清') return 'success'
  if (status === '部分收款') return 'warning'
  return 'danger'
}

const handleReceive = (item) => {
  currentItem.value = item
  receiveForm.value = { amount: '', remark: '' }
  showReceivePopup.value = true
}

const handleDetail = (item) => {
  console.log('查看明细', item)
}

const confirmReceive = async () => {
  if (!receiveForm.value.amount || parseFloat(receiveForm.value.amount) <= 0) {
    showToast('请输入收款金额')
    return
  }
  try {
    await receivePayment({
      receivable_id: currentItem.value.id,
      amount: parseFloat(receiveForm.value.amount),
      remark: receiveForm.value.remark
    })
    showToast('收款成功')
    showReceivePopup.value = false
    loadData()
  } catch (e) {
    showToast('收款失败')
  }
}

const loadData = async () => {
  try {
    const res = await getReceivables()
    list.value = res.data?.list || []
    totalReceivable.value = res.data?.total || '0.00'
    receivedAmount.value = res.data?.received || '0.00'
    outstandingAmount.value = res.data?.outstanding || '0.00'
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
    finished.value = true
  }
}

onMounted(loadData)
</script>

<style scoped>
.receivables-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.stats-card { display: flex; background: linear-gradient(135deg, #ff6b35, #ff9a56); margin: 12px; border-radius: 12px; padding: 20px; color: #fff; }
.stat-item { flex: 1; text-align: center; }
.stat-value { font-size: 20px; font-weight: bold; }
.stat-label { font-size: 12px; opacity: 0.9; margin-top: 4px; }
.stat-divider { width: 1px; background: rgba(255,255,255,0.3); }
.red { color: #ee0a24; }
.orange { color: #ff9a56; }
.filter-bar { display: flex; gap: 8px; padding: 0 12px; margin-bottom: 12px; }
.filter-tag { padding: 8px 16px; }
.receivable-card { background: #fff; margin: 0 12px 12px; border-radius: 12px; padding: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.customer-name { font-size: 15px; font-weight: bold; color: #333; }
.card-body { border-top: 1px solid #f5f5f5; padding-top: 10px; }
.info-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; }
.info-label { color: #999; }
.info-value { color: #333; }
.card-actions { display: flex; gap: 8px; margin-top: 10px; }
.receive-popup { padding: 20px; }
.popup-title { font-size: 16px; font-weight: bold; text-align: center; margin-bottom: 16px; }
.popup-actions { display: flex; gap: 12px; margin-top: 16px; }
.popup-actions button { flex: 1; }
</style>