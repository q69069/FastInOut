<template>
  <div class="order-page">
    <!-- 顶部：标题栏 -->
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">库存单据</span>
        </div>
        <div class="header-info">
          <span class="info-item">制单人：{{ authStore.displayName }}</span>
          <span class="info-item">{{ now }}</span>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="showCreateDialog">+ 新建</el-button>
        </div>
      </div>
    </el-card>

    <!-- 单据类型 Tab -->
    <el-card class="filter-card">
      <el-tabs v-model="activeType" @tab-change="onTypeChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="库存调拨" name="transfer" />
        <el-tab-pane label="盘点管理" name="stocktake" />
        <el-tab-pane label="装车调度" name="vehicle" />
        <el-tab-pane label="报损单" name="damage" />
      </el-tabs>

      <el-form inline @submit.prevent="loadData">
        <el-form-item label="仓库">
          <el-select v-model="query.warehouse_id" clearable filterable placeholder="全部" style="width:150px">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间">
          <el-date-picker v-model="query.date_range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" clearable placeholder="单据号" style="width:150px" />
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
          <template #default="{ row }">
            <span>{{ row.no || row.code || row.transfer_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="150" :formatter="fmtDate" />
        <el-table-column prop="warehouse_name" label="仓库" />
        <el-table-column prop="total_amount" label="金额" width="100" align="right">
          <template #default="{ row }">
            <span v-if="row.total_amount != null">¥{{ Number(row.total_amount || 0).toFixed(2) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type" size="small">{{ statusMap[row.status]?.label || row.status || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDocument(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total"
        layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>

    <!-- 新建选择弹窗 -->
    <el-dialog v-model="createDialogVisible" title="新建单据" width="400px" destroy-on-close>
      <div class="create-grid">
        <div class="create-item" @click="goCreate('transfers')">
          <el-icon><Box /></el-icon>
          <span>调拨单</span>
        </div>
        <div class="create-item" @click="goCreate('stocktaking')">
          <el-icon><Calendar /></el-icon>
          <span>盘点单</span>
        </div>
        <div class="create-item" @click="goCreate('vehicle-loads')">
          <el-icon><Van /></el-icon>
          <span>装车单</span>
        </div>
        <div class="create-item" @click="goCreate('damage-reports')">
          <el-icon><Warning /></el-icon>
          <span>报损单</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  getTransfers,
  getStocktaking,
  getVehicleLoads,
  getDamageReports,
  getWarehouses,
  exportDocuments
} from '../../api'
import { useAuthStore } from '../../stores/auth'
import { Box, Calendar, Van, Warning } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const activeType = ref('all')
const createDialogVisible = ref(false)

const warehouses = ref([])
const list = ref([])
const total = ref(0)

const query = ref({ page: 1, page_size: 20, date_range: [], warehouse_id: '', keyword: '' })

const statusMap = {
  0: { label: '草稿', type: 'info' },
  1: { label: '进行中', type: 'warning' },
  2: { label: '已完成', type: 'success' },
  3: { label: '已取消', type: 'danger' },
  4: { label: '已作废', type: 'danger' },
  pending: { label: '草稿', type: 'info' },
  confirmed: { label: '已确认', type: 'success' },
  settled: { label: '已结算', type: 'success' },
  voided: { label: '已作废', type: 'info' },
  transferring: { label: '调拨中', type: 'warning' },
  completed: { label: '已完成', type: 'success' },
  draft: { label: '草稿', type: 'info' },
  loaded: { label: '已装车', type: 'success' },
  returned: { label: '已退库', type: 'danger' },
  adjusted: { label: '已调整', type: 'success' },
  reversed: { label: '已冲红', type: 'danger' },
}

const typeTagMap = {
  transfer: { label: '库存调拨', type: 'success' },
  stocktake: { label: '盘点管理', type: 'warning' },
  vehicle: { label: '装车调度', type: 'info' },
  damage: { label: '报损单', type: 'danger' },
}

const onTypeChange = () => { query.value.page = 1; loadData() }

const showCreateDialog = () => { createDialogVisible.value = true }

const goCreate = (path) => {
  createDialogVisible.value = false
  router.push(`/${path}`)
}

const clearFilter = () => {
  query.value = { page: 1, page_size: 20, date_range: [], warehouse_id: '', keyword: '' }
  loadData()
}

const buildParams = () => {
  const p = { page: query.value.page, page_size: query.value.page_size }
  if (query.value.date_range?.length === 2) { p.start_date = query.value.date_range[0]; p.end_date = query.value.date_range[1] }
  if (query.value.warehouse_id) p.warehouse_id = query.value.warehouse_id
  if (query.value.keyword) p.keyword = query.value.keyword
  return p
}

const fmtDate = (_r, _c, v) => v ? String(v).replace('T', ' ').slice(0, 16) : ''

const getSummary = ({ columns, data }) => {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (col.property === 'total_amount') {
      const val = data.reduce((s, r) => s + Number(r[col.property] || 0), 0)
      sums[idx] = `¥${val.toFixed(2)}`
    } else { sums[idx] = '' }
  })
  return sums
}

const loadData = async () => {
  list.value = []
  total.value = 0
  if (activeType.value === 'all') {
    await Promise.all([loadTransfers(), loadStocktakes(), loadVehicles(), loadDamages()])
    list.value.sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
  } else if (activeType.value === 'transfer') { await loadTransfers() }
  else if (activeType.value === 'stocktake') { await loadStocktakes() }
  else if (activeType.value === 'vehicle') { await loadVehicles() }
  else if (activeType.value === 'damage') { await loadDamages() }
}

const loadTransfers = async () => {
  try {
    const res = await getTransfers(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'transfer'; i.no = i.code })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

const loadStocktakes = async () => {
  try {
    const res = await getStocktaking(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'stocktake'; i.no = i.code })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

const loadVehicles = async () => {
  try {
    const res = await getVehicleLoads(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'vehicle'; i.no = i.load_no })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

const loadDamages = async () => {
  try {
    const res = await getDamageReports(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'damage'; i.no = i.code })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

const routeMap = {
  transfer: '/transfers',
  stocktake: '/stocktaking',
  vehicle: '/vehicle-loads',
  damage: '/damage-reports'
}

const openDocument = (row) => {
  const path = routeMap[row._type]
  if (path) {
    router.push({ path, query: { id: row.id } })
  }
}

const handleExport = async () => {
  try {
    const params = {}
    if (activeType.value && activeType.value !== 'all') params.type = activeType.value === 'transfer' ? 'transfer' : activeType.value === 'stocktake' ? 'stocktaking' : activeType.value === 'vehicle' ? 'vehicle_load' : 'damage_report'
    if (query.value.date_range?.length === 2) { params.start_date = query.value.date_range[0]; params.end_date = query.value.date_range[1] }
    if (query.value.keyword) params.keyword = query.value.keyword
    const res = await exportDocuments(params)
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `库存单据导出_${new Date().toISOString().slice(0,10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

onMounted(async () => {
  const w = await getWarehouses({ page_size: 100 })
  warehouses.value = w.data?.list || w.data || []
  loadData()
})
</script>

<style scoped>
.order-page { padding: 16px; background: #f5f5f5; min-height: 100vh }
.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px }
.page-title { display: flex; align-items: center; gap: 12px }
.title-text { font-size: 18px; font-weight: 600; color: #303133 }
.header-info { display: flex; gap: 24px; color: #909399; font-size: 13px }
.filter-card { margin-top: 12px }
.list-card { margin-top: 12px }
.create-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; padding: 8px }
.create-item { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 24px 16px; background: #f5f7fa; border: 1px solid #e4e7ed; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
.create-item:hover { background: #ecf5ff; border-color: #409eff; color: #409eff }
.create-item .el-icon { font-size: 28px; }
.create-item span { font-size: 14px; font-weight: 500; }
</style>
