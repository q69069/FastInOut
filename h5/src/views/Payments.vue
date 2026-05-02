<template>
  <div class="payments-page">
    <van-nav-bar title="应付款管理" />

    <!-- 统计卡片 -->
    <div class="stats-card">
      <div class="stat-item">
        <div class="stat-value">¥{{ totalPayable }}</div>
        <div class="stat-label">应付总额</div>
      </div>
      <div class="stat-divider" />
      <div class="stat-item">
        <div class="stat-value green">¥{{ paidAmount }}</div>
        <div class="stat-label">已付金额</div>
      </div>
      <div class="stat-divider" />
      <div class="stat-item">
        <div class="stat-value red">¥{{ outstandingAmount }}</div>
        <div class="stat-label">未付金额</div>
      </div>
    </div>

    <!-- 付款列表 -->
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadData">
        <div v-for="item in list" :key="item.id" class="payment-card">
          <div class="card-header">
            <div class="supplier-name">{{ item.supplier_name }}</div>
            <van-tag :type="getStatusType(item.status)" size="small">{{ item.status }}</van-tag>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="info-label">应付金额</span>
              <span class="info-value">¥{{ item.amount }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">已付金额</span>
              <span class="info-value green">¥{{ item.paid || 0 }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">单据日期</span>
              <span class="info-value">{{ item.date }}</span>
            </div>
          </div>
          <div class="card-actions">
            <van-button v-if="item.status !== '已结清'" size="small" type="primary" @click="handlePay(item)">付款</van-button>
            <van-button size="small" @click="handleDetail(item)">明细</van-button>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 付款弹窗 -->
    <van-popup v-model:show="showPayPopup" position="bottom" round>
      <div class="pay-popup">
        <div class="popup-title">付款登记</div>
        <van-cell-group inset>
          <van-field v-model="payForm.amount" label="付款金额" type="number" placeholder="请输入付款金额" />
          <van-field v-model="payForm.remark" label="备注" placeholder="备注信息" />
        </van-cell-group>
        <div class="popup-actions">
          <van-button @click="showPayPopup = false">取消</van-button>
          <van-button type="primary" @click="confirmPay">确认</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast } from 'vant'
import { getPayments, makePayment } from '../api'

const loading = ref(false)
const finished = ref(false)
const showPayPopup = ref(false)
const currentItem = ref(null)

const list = ref([])
const totalPayable = ref('0.00')
const paidAmount = ref('0.00')
const outstandingAmount = ref('0.00')

const payForm = ref({ amount: '', remark: '' })

const getStatusType = (status) => {
  if (status === '已结清') return 'success'
  if (status === '部分付款') return 'warning'
  return 'danger'
}

const handlePay = (item) => {
  currentItem.value = item
  payForm.value = { amount: '', remark: '' }
  showPayPopup.value = true
}

const handleDetail = (item) => {
  console.log('查看明细', item)
}

const confirmPay = async () => {
  if (!payForm.value.amount || parseFloat(payForm.value.amount) <= 0) {
    showToast('请输入付款金额')
    return
  }
  try {
    await makePayment({
      payable_id: currentItem.value.id,
      amount: parseFloat(payForm.value.amount),
      remark: payForm.value.remark
    })
    showToast('付款成功')
    showPayPopup.value = false
    loadData()
  } catch (e) {
    showToast('付款失败')
  }
}

const loadData = async () => {
  try {
    const res = await getPayments()
    list.value = res.data?.list || []
    totalPayable.value = res.data?.total || '0.00'
    paidAmount.value = res.data?.paid || '0.00'
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
.payments-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.stats-card { display: flex; background: linear-gradient(135deg, #07c160, #10b980); margin: 12px; border-radius: 12px; padding: 20px; color: #fff; }
.stat-item { flex: 1; text-align: center; }
.stat-value { font-size: 20px; font-weight: bold; }
.stat-label { font-size: 12px; opacity: 0.9; margin-top: 4px; }
.stat-divider { width: 1px; background: rgba(255,255,255,0.3); }
.green { color: #07c160; }
.red { color: #ee0a24; }
.payment-card { background: #fff; margin: 0 12px 12px; border-radius: 12px; padding: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.supplier-name { font-size: 15px; font-weight: bold; color: #333; }
.card-body { border-top: 1px solid #f5f5f5; padding-top: 10px; }
.info-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; }
.info-label { color: #999; }
.info-value { color: #333; }
.card-actions { display: flex; gap: 8px; margin-top: 10px; }
.pay-popup { padding: 20px; }
.popup-title { font-size: 16px; font-weight: bold; text-align: center; margin-bottom: 16px; }
.popup-actions { display: flex; gap: 12px; margin-top: 16px; }
.popup-actions button { flex: 1; }
</style>