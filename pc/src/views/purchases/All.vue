<template>
  <div class="order-page">
    <!-- 顶部：标题栏 -->
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">采购单据</span>
        </div>
        <div class="header-info">
          <span class="info-item">制单人：{{ authStore.displayName }}</span>
          <span class="info-item">{{ now }}</span>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleCreate">新建</el-button>
        </div>
      </div>
    </el-card>

    <!-- 单据类型 Tab + 筛选条件 -->
    <el-card class="filter-card">
      <el-tabs v-model="activeType" @tab-change="onTypeChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="采购订单" name="order" />
        <el-tab-pane label="采购单" name="delivery" />
        <el-tab-pane label="采购退货订单" name="return_order" />
        <el-tab-pane label="采购退货" name="return_delivery" />
      </el-tabs>

      <el-form inline @submit.prevent="loadData">
        <el-form-item label="时间">
          <el-date-picker v-model="query.date_range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" />
        </el-form-item>
        <el-form-item label="供应商">
          <el-select v-model="query.supplier_id" clearable filterable placeholder="全部" style="width:150px">
            <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="query.warehouse_id" clearable filterable placeholder="全部" style="width:130px">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="草稿" :value="0" />
            <el-option label="已确认" :value="1" />
            <el-option label="已入库" :value="2" />
            <el-option label="已冲红" :value="3" />
          </el-select>
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
            <span>{{ row.no || row.stockin_no || row.return_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="交易时间" width="150" :formatter="fmtDate" />
        <el-table-column prop="supplier_name" label="供应商" />
        <el-table-column prop="warehouse_name" label="仓库" width="100" />
        <el-table-column prop="total_amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type" size="small">{{ statusMap[row.status]?.label || row.status || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDocument(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total"
        layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>

    <!-- 新建入口 -->
    <el-dialog v-model="createVisible" title="新建采购单据" width="400px">
      <div class="create-menu">
        <div class="create-item" @click="$router.push({ path: '/purchases', query: { id: 'new-' + Date.now() } }); createVisible = false">
          <div class="create-icon">📋</div>
          <div class="create-text">
            <div class="create-title">采购订单</div>
            <div class="create-desc">创建新的采购订单</div>
          </div>
        </div>
        <div class="create-item" @click="$router.push({ path: '/purchase-receipts', query: { id: 'new-' + Date.now() } }); createVisible = false">
          <div class="create-icon">📥</div>
          <div class="create-text">
            <div class="create-title">采购单</div>
            <div class="create-desc">创建新的采购单（入库单）</div>
          </div>
        </div>
        <div class="create-item" @click="$router.push({ path: '/purchase-returns', query: { id: 'new-' + Date.now() } }); createVisible = false">
          <div class="create-icon">↩️</div>
          <div class="create-text">
            <div class="create-title">采购退货订单</div>
            <div class="create-desc">创建新的采购退货订单</div>
          </div>
        </div>
        <div class="create-item" @click="$router.push({ path: '/purchase-return-deliveries', query: { id: 'new-' + Date.now() } }); createVisible = false">
          <div class="create-icon">📦</div>
          <div class="create-text">
            <div class="create-title">采购退货</div>
            <div class="create-desc">创建新的采购退货</div>
          </div>
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
  getPurchaseOrders, getPurchaseOrder,
  getPurchaseReceipts, getPurchaseReceipt,
  getPurchaseReturns, getPurchaseReturn,
  getPurchaseReturnDlvs, getPurchaseReturnDlv,
  getSuppliers, getWarehouses,
  exportDocuments
} from '../../api'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const activeType = ref('all')
const createVisible = ref(false)

const suppliers = ref([])
const warehouses = ref([])
const list = ref([])
const total = ref(0)

const query = ref({ page: 1, page_size: 20, date_range: [], supplier_id: '', warehouse_id: '', keyword: '', status: '' })

const statusMap = {
  0: { label: '草稿', type: 'info' },
  1: { label: '已确认', type: 'warning' },
  2: { label: '已入库', type: 'success' },
  3: { label: '已冲红', type: 'danger' },
  pending: { label: '草稿', type: 'info' },
  confirmed: { label: '已入库', type: 'success' },
  settled: { label: '已结算', type: 'success' },
  warehouse_confirmed: { label: '已出库', type: 'primary' },
  finance_confirmed: { label: '已结算', type: 'success' },
  reversed: { label: '已冲红', type: 'danger' },
  voided: { label: '已作废', type: 'info' },
}

const typeTagMap = {
  order: { label: '采购订单', type: 'primary' },
  delivery: { label: '采购单', type: 'success' },
  return_order: { label: '采购退货订单', type: 'warning' },
  return_delivery: { label: '采购退货', type: 'danger' },
}

const handleCreate = () => { createVisible.value = true }
const onTypeChange = () => { query.value.page = 1; loadData() }

const clearFilter = () => {
  query.value = { page: 1, page_size: 20, date_range: [], supplier_id: '', warehouse_id: '', keyword: '', status: '' }
  loadData()
}

const buildParams = () => {
  const p = { page: query.value.page, page_size: query.value.page_size }
  if (query.value.date_range?.length === 2) { p.start_date = query.value.date_range[0]; p.end_date = query.value.date_range[1] }
  if (query.value.supplier_id) p.supplier_id = query.value.supplier_id
  if (query.value.warehouse_id) p.warehouse_id = query.value.warehouse_id
  if (query.value.status !== '' && query.value.status !== null) p.status = query.value.status
  if (query.value.keyword) p.keyword = query.value.keyword
  return p
}

const fmtDate = (_r, _c, v) => v ? String(v).replace('T', ' ').slice(0, 16) : ''
const loadData = async () => {
  list.value = []
  total.value = 0
  if (activeType.value === 'all') {
    await Promise.all([loadOrders(), loadDeliveries(), loadReturnOrders(), loadReturnDeliveries()])
    list.value.sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
  } else if (activeType.value === 'order') { await loadOrders() }
  else if (activeType.value === 'delivery') { await loadDeliveries() }
  else if (activeType.value === 'return_order') { await loadReturnOrders() }
  else if (activeType.value === 'return_delivery') { await loadReturnDeliveries() }
}

const loadOrders = async () => {
  try {
    const res = await getPurchaseOrders(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'order'; i.no = i.code })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

const loadDeliveries = async () => {
  try {
    const res = await getPurchaseReceipts(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'delivery'; i.no = i.receipt_no })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

const loadReturnOrders = async () => {
  try {
    const res = await getPurchaseReturns(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'return_order'; i.no = i.code })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

const loadReturnDeliveries = async () => {
  try {
    const res = await getPurchaseReturnDlvs(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'return_delivery'; i.no = i.return_dlv_no })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

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

const openDocument = (row) => {
  const routeMap = {
    order: '/purchases',
    delivery: '/purchase-receipts',
    return_order: '/purchase-returns',
    return_delivery: '/purchase-return-deliveries'
  }
  const path = routeMap[row._type]
  if (path) router.push({ path, query: { id: row.id } })
}

const handleExport = async () => {
  try {
    const params = {}
    if (activeType.value && activeType.value !== 'all') params.type = activeType.value === 'order' ? 'purchase_order' : activeType.value === 'delivery' ? 'purchase_receipt' : activeType.value === 'return_order' ? 'purchase_return_order' : 'purchase_return_dlv'
    if (query.value.date_range?.length === 2) { params.start_date = query.value.date_range[0]; params.end_date = query.value.date_range[1] }
    if (query.value.keyword) params.keyword = query.value.keyword
    const res = await exportDocuments(params)
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `采购单据导出_${new Date().toISOString().slice(0,10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

onMounted(async () => {
  const [sup, wh] = await Promise.all([getSuppliers({ page_size: 1000 }), getWarehouses({ page_size: 100 })])
  suppliers.value = sup.data?.list || sup.data || []
  warehouses.value = wh.data?.list || wh.data || []
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
.create-menu { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 8px }
.create-item { display: flex; align-items: center; gap: 12px; padding: 16px; border: 1px solid #e8e8e8; border-radius: 8px; cursor: pointer; transition: all 0.15s; }
.create-item:hover { border-color: #409eff; background: #f0f7ff }
.create-icon { font-size: 28px }
.create-title { font-size: 14px; font-weight: 600; color: #303133 }
.create-desc { font-size: 12px; color: #909399; margin-top: 2px }
</style>
