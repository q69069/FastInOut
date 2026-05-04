<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>交账管理</span>
          <el-button type="primary" @click="showCreateDialog()">新建交账</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="audited" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" @click="loadData">查询</el-button></el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="settlement_no" label="单号" width="150" />
        <el-table-column prop="employee_name" label="业务员" width="100" />
        <el-table-column prop="total_sales" label="销售总额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_sales||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="total_returns" label="退货总额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_returns||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="actual_cash" label="实交现金" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.actual_cash||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status==='audited'?'success':row.status==='rejected'?'danger':'info'">
              {{ row.status==='audited'?'已通过':row.status==='rejected'?'已驳回':'待审核' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">详情</el-button>
            <el-button link type="success" v-if="row.status==='pending'" @click="handleAudit(row, 'approve')">通过</el-button>
            <el-button link type="danger" v-if="row.status==='pending'" @click="handleAudit(row, 'reject')">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>

    <!-- 新建交账弹窗 -->
    <el-dialog v-model="createVisible" title="新建交账" width="800px" :close-on-click-modal="false">
      <el-form :model="form" label-width="80px">
        <el-form-item label="业务员" required>
          <el-select v-model="form.employee_id" filterable placeholder="选择业务员" style="width:100%" @change="loadPendingDeliveries">
            <el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-divider content-position="left">待交账销售单</el-divider>
        <el-table :data="pendingDeliveries" border size="small" @selection-change="onDeliverySelect">
          <el-table-column type="selection" width="50" />
          <el-table-column prop="delivery_no" label="单号" width="150" />
          <el-table-column prop="total_amount" label="金额" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.total_amount||0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="cash_amount" label="现金" width="80" align="right">
            <template #default="{ row }">¥{{ Number(row.cash_amount||0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="credit_amount" label="赊账" width="80" align="right">
            <template #default="{ row }">¥{{ Number(row.credit_amount||0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="170" />
        </el-table>
        <div style="margin-top:12px;font-weight:bold">
          选中 {{ selectedDeliveries.length }} 单，合计 ¥{{ selectedTotal.toFixed(2) }}
        </div>
        <el-form-item label="备注" style="margin-top:12px">
          <el-input v-model="form.remark" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible=false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="saving">提交交账</el-button>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="交账详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="单号">{{ detail.settlement_no }}</el-descriptions-item>
        <el-descriptions-item label="业务员">{{ detail.employee_name }}</el-descriptions-item>
        <el-descriptions-item label="销售总额">¥{{ Number(detail.total_sales||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="退货总额">¥{{ Number(detail.total_returns||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="费用总额">¥{{ Number(detail.total_expenses||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="实交现金">¥{{ Number(detail.actual_cash||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="现金">¥{{ Number(detail.total_cash||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="微信">¥{{ Number(detail.total_wechat||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="支付宝">¥{{ Number(detail.total_alipay||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="赊账">¥{{ Number(detail.total_credit||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="detail.status==='audited'?'success':detail.status==='rejected'?'danger':'info'">
            {{ detail.status==='audited'?'已通过':detail.status==='rejected'?'已驳回':'待审核' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="审核意见">{{ detail.audit_comment || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div v-if="detail.deliveries?.length" style="margin-top:16px">
        <h4>关联销售单</h4>
        <el-table :data="detail.deliveries" border size="small">
          <el-table-column prop="delivery_no" label="单号" />
          <el-table-column prop="total_amount" label="金额" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.total_amount||0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSettlements, createSettlement, getSettlement, auditSettlement, getPendingDeliveries, getEmployees } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, status: '' })
const createVisible = ref(false)
const detailVisible = ref(false)
const saving = ref(false)
const detail = ref({})
const employees = ref([])
const pendingDeliveries = ref([])
const selectedDeliveries = ref([])
const form = ref({ employee_id: null, remark: '' })

const selectedTotal = computed(() => selectedDeliveries.value.reduce((sum, d) => sum + (d.total_amount || 0), 0))

const loadData = async () => {
  const res = await getSettlements(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadEmployees = async () => {
  const res = await getEmployees()
  employees.value = res.data || []
}

const showCreateDialog = () => {
  form.value = { employee_id: null, remark: '' }
  pendingDeliveries.value = []
  selectedDeliveries.value = []
  createVisible.value = true
}

const loadPendingDeliveries = async () => {
  if (!form.value.employee_id) return
  const res = await getPendingDeliveries({ employee_id: form.value.employee_id })
  pendingDeliveries.value = res.data || []
}

const onDeliverySelect = (rows) => { selectedDeliveries.value = rows }

const handleCreate = async () => {
  if (!form.value.employee_id) return ElMessage.warning('请选择业务员')
  if (!selectedDeliveries.value.length) return ElMessage.warning('请选择至少一个销售单')
  saving.value = true
  try {
    await createSettlement({
      employee_id: form.value.employee_id,
      delivery_ids: selectedDeliveries.value.map(d => d.id),
      remark: form.value.remark
    })
    ElMessage.success('交账单创建成功')
    createVisible.value = false
    loadData()
  } finally { saving.value = false }
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

onMounted(() => { loadData(); loadEmployees() })
</script>
