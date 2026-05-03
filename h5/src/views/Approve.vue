<template>
  <div class="approve-page">
    <van-nav-bar title="审核中心" />

    <!-- 统计卡片 -->
    <div class="stats-card">
      <div class="stat-item" @click="filterStatus = 'pending'">
        <div class="stat-value orange">{{ pendingCount }}</div>
        <div class="stat-label">待审核</div>
      </div>
      <div class="stat-divider" />
      <div class="stat-item" @click="filterStatus = 'approved'">
        <div class="stat-value green">{{ approvedCount }}</div>
        <div class="stat-label">已通过</div>
      </div>
      <div class="stat-divider" />
      <div class="stat-item" @click="filterStatus = 'rejected'">
        <div class="stat-value red">{{ rejectedCount }}</div>
        <div class="stat-label">已驳回</div>
      </div>
    </div>

    <!-- 筛选标签 -->
    <div class="filter-tabs">
      <van-tag :type="filterStatus === 'pending' ? 'warning' : 'default'" size="large" @click="filterStatus = 'pending'">待审核</van-tag>
      <van-tag :type="filterStatus === 'approved' ? 'success' : 'default'" size="large" @click="filterStatus = 'approved'">已通过</van-tag>
      <van-tag :type="filterStatus === 'rejected' ? 'danger' : 'default'" size="large" @click="filterStatus = 'rejected'">已驳回</van-tag>
      <van-tag :type="filterStatus === 'all' ? 'primary' : 'default'" size="large" @click="filterStatus = 'all'">全部</van-tag>
    </div>

    <!-- 单据列表 -->
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadData">
        <div v-for="item in filteredList" :key="item.id" class="bill-card">
          <div class="card-header">
            <div class="bill-type" :class="item.type_class">{{ item.type_text }}</div>
            <van-tag :type="getStatusType(item.status)" size="small">{{ item.status }}</van-tag>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="info-label">单号</span>
              <span class="info-value">{{ item.bill_no }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">申请人</span>
              <span class="info-value">{{ item.applicant }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">申请时间</span>
              <span class="info-value">{{ item.create_time }}</span>
            </div>
            <div class="info-row" v-if="item.amount">
              <span class="info-label">金额</span>
              <span class="info-value orange">¥{{ item.amount }}</span>
            </div>
          </div>
          <div class="card-actions">
            <van-button v-if="authStore.can('sales', 'audit') && item.status === '待审核'" size="small" type="primary" @click="handleApprove(item)">审核</van-button>
            <van-button size="small" @click="handleDetail(item)">详情</van-button>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 审核弹窗 -->
    <van-popup v-model:show="showApprovePopup" position="bottom" round>
      <div class="approve-popup">
        <div class="popup-title">审核单据</div>
        <van-cell-group inset>
          <van-cell title="单号" :value="currentBill?.bill_no" />
          <van-cell title="类型" :value="currentBill?.type_text" />
          <van-cell title="金额" :value="currentBill?.amount ? '¥' + currentBill.amount : '-'" />
        </van-cell-group>
        <van-cell-group inset style="margin-top: 12px;">
          <van-field v-model="approveForm.remark" label="审核意见" placeholder="请输入审核意见" rows="2" autosize type="textarea" />
        </van-cell-group>
        <div class="popup-actions">
          <van-button v-if="authStore.can('sales', 'audit')" @click="handleReject" type="danger">驳回</van-button>
          <van-button v-if="authStore.can('sales', 'audit')" @click="handlePass" type="success">通过</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast } from 'vant'
import { getApproveList, approveBill, rejectBill } from '../api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const loading = ref(false)
const finished = ref(false)
const filterStatus = ref('pending')
const showApprovePopup = ref(false)
const currentBill = ref(null)

const list = ref([])
const pendingCount = ref(0)
const approvedCount = ref(0)
const rejectedCount = ref(0)

const approveForm = ref({ remark: '' })

const filteredList = computed(() => {
  if (filterStatus.value === 'all') return list.value
  return list.value.filter(i => i.status === filterStatus.value)
})

const getStatusType = (status) => {
  if (status === '已通过') return 'success'
  if (status === '已驳回') return 'danger'
  return 'warning'
}

const handleApprove = (item) => {
  currentBill.value = item
  approveForm.value.remark = ''
  showApprovePopup.value = true
}

const handleDetail = (item) => {
  console.log('查看详情', item)
}

const handlePass = async () => {
  try {
    await approveBill({ id: currentBill.value.id, remark: approveForm.value.remark })
    showToast('审核通过')
    showApprovePopup.value = false
    loadData()
  } catch (e) {
    showToast('操作失败')
  }
}

const handleReject = async () => {
  try {
    await rejectBill({ id: currentBill.value.id, remark: approveForm.value.remark })
    showToast('已驳回')
    showApprovePopup.value = false
    loadData()
  } catch (e) {
    showToast('操作失败')
  }
}

const loadData = async () => {
  try {
    const res = await getApproveList()
    list.value = res.data || []
    pendingCount.value = list.value.filter(i => i.status === '待审核').length
    approvedCount.value = list.value.filter(i => i.status === '已通过').length
    rejectedCount.value = list.value.filter(i => i.status === '已驳回').length
  } catch (e) {
    // 模拟数据
    list.value = [
      { id: 1, bill_no: 'TR20260502001', type_text: '调拨单', type_class: 'transfer', applicant: '张三', create_time: '2026-05-02 10:30', amount: 0, status: '待审核' },
      { id: 2, bill_no: 'SO20260502002', type_text: '销售单', type_class: 'order', applicant: '李四', create_time: '2026-05-02 09:15', amount: 1500, status: '已通过' },
      { id: 3, bill_no: 'LR20260501003', type_text: '报损单', type_class: 'loss', applicant: '王五', create_time: '2026-05-01 16:20', amount: 0, status: '已驳回' }
    ]
    pendingCount.value = 1
    approvedCount.value = 1
    rejectedCount.value = 1
  } finally {
    loading.value = false
    finished.value = true
  }
}

onMounted(loadData)
</script>

<style scoped>
.approve-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.stats-card { display: flex; background: linear-gradient(135deg, #1989fa, #396bec); margin: 12px; border-radius: 12px; padding: 20px; color: #fff; }
.stat-item { flex: 1; text-align: center; }
.stat-value { font-size: 24px; font-weight: bold; }
.stat-label { font-size: 12px; opacity: 0.9; margin-top: 4px; }
.stat-divider { width: 1px; background: rgba(255,255,255,0.3); }
.orange { color: #ff9a56; }
.green { color: #07c160; }
.red { color: #ee0a24; }
.filter-tabs { display: flex; gap: 8px; padding: 0 12px; margin-bottom: 12px; }
.bill-card { background: #fff; margin: 0 12px 12px; border-radius: 12px; padding: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.bill-type { font-size: 14px; font-weight: bold; padding: 4px 8px; border-radius: 4px; }
.bill-type.transfer { background: #e6f7ff; color: #1989fa; }
.bill-type.order { background: #fff7e6; color: #fa8c16; }
.bill-type.loss { background: #fff1f0; color: #ff4d4f; }
.card-body { border-top: 1px solid #f5f5f5; padding-top: 10px; }
.info-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; }
.info-label { color: #999; }
.info-value { color: #333; }
.card-actions { display: flex; gap: 8px; margin-top: 10px; }
.approve-popup { padding: 20px; }
.popup-title { font-size: 16px; font-weight: bold; text-align: center; margin-bottom: 16px; }
.popup-actions { display: flex; gap: 12px; margin-top: 16px; }
.popup-actions button { flex: 1; }
</style>