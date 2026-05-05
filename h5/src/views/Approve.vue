<template>
  <div class="page">
    <van-nav-bar title="审核中心" left-arrow @click-left="$router.back()" />

    <!-- 统计卡片 -->
    <div class="stats-card">
      <div class="stat-item" @click="filterStatus = 'pending'">
        <span class="stat-val orange">{{ pendingCount }}</span>
        <span class="stat-label">待审核</span>
      </div>
      <div class="stat-divider" />
      <div class="stat-item" @click="filterStatus = 'approved'">
        <span class="stat-val green">{{ approvedCount }}</span>
        <span class="stat-label">已通过</span>
      </div>
      <div class="stat-divider" />
      <div class="stat-item" @click="filterStatus = 'rejected'">
        <span class="stat-val red">{{ rejectedCount }}</span>
        <span class="stat-label">已驳回</span>
      </div>
    </div>

    <!-- 筛选标签 -->
    <div class="filter-tabs">
      <van-tag v-for="s in statusOptions" :key="s.value" :type="filterStatus === s.value ? s.type : 'default'" size="large" @click="filterStatus = s.value; loadData()">{{ s.label }}</van-tag>
    </div>

    <!-- 单据列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="loadData">
      <van-list v-model="loading" :finished="finished" finished-text="没有更多了" @load="loadData">
        <div v-for="item in filteredList" :key="item.id" class="bill-card">
          <div class="card-header">
            <van-tag :type="getBillTypeColor(item.bill_type)">{{ getBillTypeLabel(item.bill_type) }}</van-tag>
            <van-tag :type="getStatusType(item.status)">{{ item.status_text || item.status }}</van-tag>
          </div>
          <div class="card-body">
            <div class="info-row"><span>单号</span><span>{{ item.bill_no || item.code }}</span></div>
            <div class="info-row"><span>申请人</span><span>{{ item.applicant_name || item.applicant || '-' }}</span></div>
            <div class="info-row"><span>申请时间</span><span>{{ item.created_at?.substring(0, 16) }}</span></div>
            <div class="info-row" v-if="item.total_amount"><span>金额</span><span class="orange">¥{{ (item.total_amount || 0).toFixed(2) }}</span></div>
            <div class="info-row" v-if="item.remark"><span>备注</span><span>{{ item.remark }}</span></div>
          </div>
          <div style="display:flex;gap:8px;margin-top:8px">
            <van-button v-if="canApprove(item)" size="small" type="success" @click="handleApprove(item)">通过</van-button>
            <van-button v-if="canApprove(item)" size="small" type="danger" plain @click="handleReject(item)">驳回</van-button>
          </div>
        </div>
        <van-empty v-if="filteredList.length === 0 && !loading" description="暂无待审数据" />
      </van-list>
    </van-pull-refresh>

    <!-- 审核弹窗 -->
    <van-popup v-model:show="showApprovePopup" position="bottom" round>
      <div style="padding:20px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">审核单据</div>
        <van-cell-group inset>
          <van-cell title="单号" :value="currentBill?.bill_no || currentBill?.code" />
          <van-cell title="类型" :value="getBillTypeLabel(currentBill?.bill_type)" />
          <van-cell title="金额" :value="currentBill?.total_amount ? '¥' + currentBill.total_amount.toFixed(2) : '-'" />
        </van-cell-group>
        <van-cell-group inset style="margin-top:12px">
          <van-field v-model="approveForm.remark" label="审核意见" placeholder="请输入审核意见" rows="2" type="textarea" />
        </van-cell-group>
        <div style="display:flex;gap:12px;margin-top:16px">
          <van-button type="danger" block @click="doReject">驳回</van-button>
          <van-button type="success" block @click="doPass">通过</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getApproveList, approveBill, rejectBill } from '../api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const filterStatus = ref('pending')
const list = ref([])
const pendingCount = ref(0)
const approvedCount = ref(0)
const rejectedCount = ref(0)
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const showApprovePopup = ref(false)
const currentBill = ref(null)
const approveForm = ref({ remark: '' })

const statusOptions = [
  { label: '待审核', value: 'pending', type: 'warning' },
  { label: '已通过', value: 'approved', type: 'success' },
  { label: '已驳回', value: 'rejected', type: 'danger' },
  { label: '全部', value: 'all', type: 'primary' }
]

const filteredList = computed(() => {
  if (filterStatus.value === 'all') return list.value
  return list.value.filter(i => (i.status || '').toLowerCase().includes(filterStatus.value))
})

const getStatusType = (status) => {
  const s = (status || '').toLowerCase()
  if (s.includes('pass') || s.includes('approved') || s.includes('通过')) return 'success'
  if (s.includes('reject') || s.includes('驳回')) return 'danger'
  return 'warning'
}

const getBillTypeLabel = (type) => {
  const map = { expense: '费用单', purchase_return: '采购退货', sales_return: '销售退货', transfer: '调拨单', damage: '报损单', stocktaking: '盘点单' }
  return map[type] || type || '单据'
}

const getBillTypeColor = (type) => {
  const map = { expense: 'danger', purchase_return: 'warning', sales_return: 'warning', transfer: 'primary', damage: 'danger', stocktaking: 'success' }
  return map[type] || 'default'
}

const canApprove = (item) => {
  if (!authStore.can('sales', 'audit') && !authStore.can('finance', 'audit')) return false
  return (item.status || '').toLowerCase().includes('pending') || (item.status || '').toLowerCase().includes('待审')
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getApproveList({ page_size: 100 })
    list.value = res.data || []
    pendingCount.value = list.value.filter(i => (i.status || '').toLowerCase().includes('pending') || (i.status || '').includes('待审')).length
    approvedCount.value = list.value.filter(i => (i.status || '').toLowerCase().includes('pass') || (i.status || '').includes('通过')).length
    rejectedCount.value = list.value.filter(i => (i.status || '').toLowerCase().includes('reject') || (i.status || '').includes('驳回')).length
  } catch {}
  loading.value = false
  refreshing.value = false
  finished.value = true
}

const handleApprove = (item) => {
  currentBill.value = item
  approveForm.value.remark = ''
  showApprovePopup.value = true
}

const handleReject = async (item) => {
  try {
    await showConfirmDialog({ title: '驳回确认', message: `确认驳回 ${item.bill_no || item.code}？` })
    await rejectBill({ id: item.id, remark: 'H5端驳回' })
    showSuccessToast('已驳回')
    loadData()
  } catch {}
}

const doPass = async () => {
  try {
    await approveBill({ id: currentBill.value.id, remark: approveForm.value.remark })
    showSuccessToast('审核通过')
    showApprovePopup.value = false
    loadData()
  } catch { showToast('操作失败') }
}

const doReject = async () => {
  try {
    await rejectBill({ id: currentBill.value.id, remark: approveForm.value.remark })
    showSuccessToast('已驳回')
    showApprovePopup.value = false
    loadData()
  } catch { showToast('操作失败') }
}

onMounted(loadData)
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.stats-card { display: flex; background: linear-gradient(135deg, #1989fa, #396bec); margin: 8px 16px; border-radius: 12px; padding: 16px; color: #fff; }
.stat-item { flex: 1; text-align: center; }
.stat-val { font-size: 24px; font-weight: bold; display: block; }
.stat-label { font-size: 11px; opacity: 0.9; margin-top: 2px; }
.stat-divider { width: 1px; background: rgba(255,255,255,0.3); }
.orange { color: #ff9a56; }
.green { color: #07c160; }
.red { color: #ee0a24; }
.filter-tabs { display: flex; gap: 8px; padding: 8px 16px; }
.bill-card {
  background: #fff; margin: 8px 16px; border-radius: 10px;
  padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.card-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.card-body { border-top: 1px solid #f5f5f5; padding-top: 8px; }
.info-row { display: flex; justify-content: space-between; padding: 2px 0; font-size: 13px; color: #666; }
</style>
