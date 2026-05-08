<template>
  <div class="order-page">
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">交账管理</span>
        </div>
        <div class="header-info">
          <span class="info-item">制单人：{{ authStore.displayName }}</span>
          <span class="info-item">{{ now }}</span>
        </div>
        <div class="header-actions" />
      </div>
    </el-card>

    <!-- 列表 -->
    <el-card class="form-card">
      <el-form inline :model="queryFilter" style="margin-bottom:12px">
        <el-select v-model="queryFilter.status" placeholder="状态" clearable style="width:120px" @change="loadData">
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="audited" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
        <el-button @click="queryFilter.page=1;loadData()">查询</el-button>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="settlement_no" label="单号" width="160" />
        <el-table-column prop="employee_name" label="业务员" />
        <el-table-column prop="total_sales" label="销售总额" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.total_sales||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="actual_cash" label="实交现金" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.actual_cash||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="total_cash" label="现金" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_cash||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status==='audited'?'success':row.status==='rejected'?'danger':'info'" size="small">
              {{ row.status==='audited'?'已通过':row.status==='rejected'?'已驳回':'待审核' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="showDetail(row)">详情</el-button>
            <el-button v-if="row.status==='pending'" size="small" type="success" @click="handleAudit(row,'approve')">通过</el-button>
            <el-button v-if="row.status==='pending'" size="small" type="danger" @click="handleAudit(row,'reject')">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:12px" :total="total" :page-size="queryFilter.page_size" background layout="prev,pager,next" v-model:current-page="queryFilter.page" @current-change="loadData" />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="交账详情" width="700px">
      <el-descriptions :column="2" border v-if="detail">
        <el-descriptions-item label="单号">{{ detail.settlement_no }}</el-descriptions-item>
        <el-descriptions-item label="业务员">{{ detail.employee_name }}</el-descriptions-item>
        <el-descriptions-item label="销售总额">¥{{ Number(detail.total_sales || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="退货总额">¥{{ Number(detail.total_returns || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="费用总额">¥{{ Number(detail.total_expenses || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="实交现金">¥{{ Number(detail.actual_cash || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="现金">¥{{ Number(detail.total_cash || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="微信">¥{{ Number(detail.total_wechat || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="支付宝">¥{{ Number(detail.total_alipay || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="赊账">¥{{ Number(detail.total_credit || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="detail.status === 'audited' ? 'success' : detail.status === 'rejected' ? 'danger' : 'info'">
            {{ detail.status === 'audited' ? '已通过' : detail.status === 'rejected' ? '已驳回' : '待审核' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="审核意见">{{ detail.audit_comment || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div v-if="detail.deliveries?.length" style="margin-top:16px">
        <div class="section-title">关联销售单</div>
        <el-table :data="detail.deliveries" border size="small">
          <el-table-column prop="delivery_no" label="单号" />
          <el-table-column prop="total_amount" label="金额" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.total_amount || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSettlements, getSettlement, auditSettlement } from '../../api'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const list = ref([])
const total = ref(0)
const detail = ref({})
const detailVisible = ref(false)

const queryFilter = ref({ page: 1, page_size: 20, status: '' })

const loadData = async () => {
  const params = { ...queryFilter.value }
  if (!params.status) delete params.status
  const res = await getSettlements(params)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDetail = async (row) => {
  const res = await getSettlement(row.id)
  detail.value = res.data || res
  detailVisible.value = true
}

const handleAudit = async (row, action) => {
  const label = action === 'approve' ? '通过' : '驳回'
  await ElMessageBox.confirm(`确认${label}此交账单？`, '审核', { type: action === 'approve' ? 'success' : 'warning' })
  await auditSettlement(row.id, { action })
  ElMessage.success(`已${label}`)
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.order-page { padding: 16px; background: #f5f5f5; min-height: 100vh }
.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px }
.page-title { display: flex; align-items: center; gap: 12px }
.title-text { font-size: 18px; font-weight: 600; color: #303133 }
.header-info { display: flex; gap: 24px; color: #909399; font-size: 13px }
.header-actions { display: flex; gap: 8px }
.form-card { margin-top: 12px }
.section-title { font-size: 14px; font-weight: 600; color: #303133; margin: 16px 0 10px; padding-left: 8px; border-left: 3px solid #409eff }
</style>