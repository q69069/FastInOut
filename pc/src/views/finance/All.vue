<template>
  <div class="order-page">
    <!-- 顶部：标题栏 -->
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">财务单据</span>
        </div>
        <div class="header-info">
          <span class="info-item">制单人：{{ authStore.displayName }}</span>
          <span class="info-item">{{ now }}</span>
        </div>
      </div>
    </el-card>

    <!-- 单据类型 Tab -->
    <el-card class="filter-card">
      <el-tabs v-model="activeType" @tab-change="onTypeChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="收支记录" name="flow" />
        <el-tab-pane label="费用" name="expense" />
        <el-tab-pane label="往来账" name="ledger" />
        <el-tab-pane label="客户对账" name="reconciliation" />
        <el-tab-pane label="银行对账" name="bank" />
        <el-tab-pane label="发票" name="invoice" />
      </el-tabs>

      <el-form inline @submit.prevent="loadData">
        <el-form-item label="时间">
          <el-date-picker v-model="query.date_range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="草稿" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" clearable placeholder="单据号/备注" style="width:150px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="clearFilter">清空</el-button>
          <el-button type="success" @click="handleExport">导出Excel</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 列表 -->
    <el-card class="list-card">
      <el-table :data="list" border stripe show-summary :summary-method="getSummary">
        <el-table-column type="index" width="50" align="center" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="typeTagMap[row._type]?.type">{{ typeTagMap[row._type]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="no" label="单据号" width="150">
          <template #default="{ row }">{{ row.no || row.flow_no || row.invoice_no }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="150" :formatter="fmtDate" />
        <el-table-column prop="party_name" label="对方" />
        <el-table-column prop="type_label" label="收支" width="70" align="center">
          <template #default="{ row }">
            <span :class="row.direction === 'income' ? 'text-success' : 'text-danger'">{{ row.direction === 'income' ? '收入' : '支出' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type" size="small">{{ statusMap[row.status]?.label || row.status || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total"
        layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>

    <DocumentDetail v-model="detailVisible" title="单据详情"
      :fields="detailFields" :items="[]" :item-columns="[]" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getFinanceFlow, getExpenses, getExpense,
  getInvoices, getInvoice,
  getReconciliations, getBankStatements,
  getCustomers, getSuppliers
} from '../../api'
import { useAuthStore } from '../../stores/auth'
import DocumentDetail from '../../components/DocumentDetail.vue'

const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const activeType = ref('all')
const detailVisible = ref(false)
const detail = ref({})

const detailFields = computed(() => {
  const d = detail.value
  const no = d.no || d.flow_no || d.invoice_no
  if (!no) return []
  const amountColor = d.direction === 'income' ? '#67C23A' : '#F56C6C'
  return [
    { label: '单号', value: no },
    { label: '类型', value: typeTagMap[d._type]?.label || '-', type: 'tag', tagType: typeTagMap[d._type]?.type },
    { label: '对方', value: d.party_name || '-' },
    { label: '金额', value: Number(d.amount || 0).toFixed(2), type: 'money', color: amountColor },
    { label: '创建时间', value: fmtDateVal(d.created_at) },
    { label: '备注', value: d.remark, span: 2 }
  ]
})

const customers = ref([])
const suppliers = ref([])
const list = ref([])
const total = ref(0)

const query = ref({ page: 1, page_size: 20, date_range: [], keyword: '', status: '' })

const typeTagMap = {
  flow: { label: '收支记录', type: 'primary' },
  expense: { label: '费用', type: 'warning' },
  ledger: { label: '往来账', type: 'info' },
  reconciliation: { label: '客户对账', type: 'info' },
  bank: { label: '银行对账', type: 'success' },
  invoice: { label: '发票', type: 'danger' },
}

const statusMap = {
  0: { label: '草稿', type: 'info' },
  1: { label: '已确认', type: 'success' },
  pending: { label: '草稿', type: 'info' },
  approved: { label: '已通过', type: 'success' },
  audited: { label: '已审核', type: 'success' },
  confirmed: { label: '已确认', type: 'success' },
  rejected: { label: '已驳回', type: 'danger' },
  cancelled: { label: '已取消', type: 'info' },
  reversed: { label: '已冲红', type: 'danger' },
  voided: { label: '已作废', type: 'info' },
}

const onTypeChange = () => { query.value.page = 1; loadData() }

const clearFilter = () => {
  query.value = { page: 1, page_size: 20, date_range: [], keyword: '', status: '' }
  loadData()
}

const buildParams = () => {
  const p = { page: query.value.page, page_size: query.value.page_size }
  if (query.value.date_range?.length === 2) { p.start_date = query.value.date_range[0]; p.end_date = query.value.date_range[1] }
  if (query.value.keyword) p.keyword = query.value.keyword
  if (query.value.status) p.status = query.value.status
  return p
}

const fmtDate = (_r, _c, v) => v ? String(v).replace('T', ' ').slice(0, 16) : ''
const fmtDateVal = (v) => v ? String(v).replace('T', ' ').slice(0, 16) : ''
const loadData = async () => {
  list.value = []
  total.value = 0
  if (activeType.value === 'all') {
    await Promise.all([loadFlows(), loadExpenses(), loadInvoices()])
    list.value.sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
  } else if (activeType.value === 'flow') { await loadFlows() }
  else if (activeType.value === 'expense') { await loadExpenses() }
  else if (activeType.value === 'invoice') { await loadInvoices() }
}

const loadFlows = async () => {
  try {
    const res = await getFinanceFlow(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'flow'; i.no = i.flow_no; i.party_name = i.party_name || i.customer_name || i.supplier_name; i.direction = i.direction || (Number(i.amount) >= 0 ? 'income' : 'expense') })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('加载收支记录失败:', e) }
}

const loadExpenses = async () => {
  try {
    const res = await getExpenses(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'expense'; i.no = i.expense_no; i.party_name = i.category_name; i.direction = 'expense' })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('加载费用失败:', e) }
}

const loadInvoices = async () => {
  try {
    const res = await getInvoices(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'invoice'; i.no = i.invoice_no; i.party_name = i.customer_name; i.direction = i.invoice_type === 'income' ? 'income' : 'expense' })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('加载发票失败:', e) }
}

const getSummary = ({ columns, data }) => {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (col.property === 'amount') {
      const val = data.reduce((s, r) => s + Number(r[col.property] || 0), 0)
      sums[idx] = `¥${val.toFixed(2)}`
    } else { sums[idx] = '' }
  })
  return sums
}

const showDetail = (row) => { detail.value = row; detailVisible.value = true }

const handleExport = async () => {
  try {
    const params = {}
    if (query.value.date_range?.length === 2) { params.start_date = query.value.date_range[0]; params.end_date = query.value.date_range[1] }
    if (query.value.keyword) params.keyword = query.value.keyword
    const { exportDocuments } = await import('../../api')
    const res = await exportDocuments(params)
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `财务单据导出_${new Date().toISOString().slice(0,10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

onMounted(async () => {
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
.filter-card { margin-top: 12px }
.list-card { margin-top: 12px }
.text-success { color: #67C23A }
.text-danger { color: #F56C6C }
</style>
