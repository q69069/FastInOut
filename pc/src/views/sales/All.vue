<template>
  <div class="order-page">
    <!-- 顶部：标题栏 -->
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">销售单据</span>
        </div>
        <div class="header-info">
          <span class="info-item">制单人：{{ authStore.displayName }}</span>
          <span class="info-item">{{ now }}</span>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleCreate" :loading="saving">新建</el-button>
        </div>
      </div>
    </el-card>

    <!-- 单据类型 Tab + 筛选条件 -->
    <el-card class="filter-card">
      <el-tabs v-model="activeType" @tab-change="onTypeChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="销售订单" name="order" />
        <el-tab-pane label="销售单" name="delivery" />
        <el-tab-pane label="退货订单" name="return_order" />
        <el-tab-pane label="退货单" name="return_delivery" />
      </el-tabs>

      <el-form inline @submit.prevent="loadData" v-if="activeType === 'all'">
        <el-form-item label="时间">
          <el-date-picker v-model="query.date_range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" />
        </el-form-item>
        <el-form-item label="客户">
          <el-select v-model="query.customer_id" clearable filterable placeholder="全部" style="width:150px">
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="query.warehouse_id" clearable filterable placeholder="全部" style="width:130px">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="业务员">
          <el-select v-model="query.salesman_id" clearable filterable placeholder="全部" style="width:130px">
            <el-option v-for="s in salesmen" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="待处理" value="pending" />
            <el-option label="交账中" value="settling" />
            <el-option label="已交账" value="settled" />
            <el-option label="已作废" value="voided" />
            <el-option label="已锁定" value="locked" />
            <el-option label="已红冲" value="reversed" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" clearable placeholder="单据号/客户/业务员" style="width:150px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="clearFilter">清空</el-button>
          <el-button type="success" @click="handleExport">导出Excel</el-button>
        </el-form-item>
      </el-form>

      <!-- 单类型时显示该类型特有的筛选 -->
      <el-form inline @submit.prevent="loadData" v-else>
        <el-form-item label="时间">
          <el-date-picker v-model="query.date_range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" />
        </el-form-item>
        <el-form-item label="客户" v-if="activeType !== 'return_order'">
          <el-select v-model="query.customer_id" clearable filterable placeholder="全部" style="width:150px">
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="query.warehouse_id" clearable filterable placeholder="全部" style="width:130px">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="业务员">
          <el-select v-model="query.salesman_id" clearable filterable placeholder="全部" style="width:130px">
            <el-option v-for="s in salesmen" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="草稿" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已结算" value="settled" />
            <el-option label="已作废" value="voided" />
            <el-option label="已冲红" value="reversed" />
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
        <el-table-column label="类型" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="typeTagMap[row._type]?.type">{{ typeTagMap[row._type]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="no" label="单据号" width="150">
          <template #default="{ row }">
            <span :class="row._type === 'return_delivery' && row.has_return ? 'text-success' : ''">{{ row.no || row.delivery_no || row.order_no }}</span>
            <el-tag v-if="row._type === 'return_delivery' && row.has_return" size="small" type="success">含退</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="交易时间" width="150" :formatter="fmtDate" />
        <el-table-column prop="salesman_name" label="业务员" width="100" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="warehouse_name" label="仓库" width="100" />
        <el-table-column prop="total_amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label || row.status }}</el-tag>
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
    <el-dialog v-model="createVisible" title="新建销售单据" width="400px">
      <div class="create-menu">
        <div class="create-item" @click="$router.push({ path: '/sales', query: { id: 'new-' + Date.now() } }); createVisible = false">
          <div class="create-icon">📋</div>
          <div class="create-text">
            <div class="create-title">销售订单</div>
            <div class="create-desc">创建新的销售订单</div>
          </div>
        </div>
        <div class="create-item" @click="$router.push({ path: '/sales-deliveries', query: { id: 'new-' + Date.now() } }); createVisible = false">
          <div class="create-icon">🚚</div>
          <div class="create-text">
            <div class="create-title">销售单</div>
            <div class="create-desc">创建新的销售单（出库单）</div>
          </div>
        </div>
        <div class="create-item" @click="$router.push({ path: '/sales-returns', query: { id: 'new-' + Date.now() } }); createVisible = false">
          <div class="create-icon">↩️</div>
          <div class="create-text">
            <div class="create-title">退货订单</div>
            <div class="create-desc">创建新的退货订单</div>
          </div>
        </div>
        <div class="create-item" @click="$router.push({ path: '/return-deliveries', query: { id: 'new-' + Date.now() } }); createVisible = false">
          <div class="create-icon">📦</div>
          <div class="create-text">
            <div class="create-title">退货单</div>
            <div class="create-desc">创建新的退货单</div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getSalesOrders, getSalesOrder, createSalesOrder, updateSalesOrder, deleteSalesOrder,
  getSalesDeliveries, getSalesDeliveries as getSalesStockouts,
  getSalesReturns, getSalesReturn,
  getReturnDeliveries, getReturnDelivery,
  getCustomers, getWarehouses, getSalesmen,
  exportDocuments
} from '../../api'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')
const saving = ref(false)

const activeType = ref('all')
const createVisible = ref(false)

const customers = ref([])
const warehouses = ref([])
const salesmen = ref([])
const list = ref([])
const total = ref(0)

const query = ref({ page: 1, page_size: 20, date_range: [], customer_id: '', warehouse_id: '', salesman_id: '', status: '', keyword: '' })

const statusMap = {
  0: { label: '草稿', type: 'info' },
  1: { label: '已确认', type: 'warning' },
  2: { label: '已出库', type: 'success' },
  3: { label: '已冲红', type: 'danger' },
  pending: { label: '草稿', type: 'info' },
  confirmed: { label: '已出库', type: 'success' },
  settling: { label: '交账中', type: 'primary' },
  settled: { label: '已结算', type: 'success' },
  voided: { label: '已作废', type: 'info' },
  locked: { label: '已锁定', type: 'warning' },
  reversed: { label: '已冲红', type: 'danger' },
  warehouse_confirmed: { label: '已入库', type: 'primary' },
  finance_confirmed: { label: '已结算', type: 'success' },
}

const typeTagMap = {
  order: { label: '销售订单', type: 'primary' },
  delivery: { label: '销售单', type: 'success' },
  return_order: { label: '退货订单', type: 'warning' },
  return_delivery: { label: '退货单', type: 'danger' },
}

const handleCreate = () => { createVisible.value = true }

const onTypeChange = () => {
  query.value.page = 1
  loadData()
}

const clearFilter = () => {
  query.value = { page: 1, page_size: 20, date_range: [], customer_id: '', warehouse_id: '', salesman_id: '', status: '', keyword: '' }
  loadData()
}

const buildParams = () => {
  const p = { page: query.value.page, page_size: query.value.page_size }
  if (query.value.date_range?.length === 2) {
    p.start_date = query.value.date_range[0]
    p.end_date = query.value.date_range[1]
  }
  if (query.value.customer_id) p.customer_id = query.value.customer_id
  if (query.value.warehouse_id) p.warehouse_id = query.value.warehouse_id
  if (query.value.salesman_id) p.salesman_id = query.value.salesman_id
  if (query.value.status) p.status = query.value.status
  if (query.value.keyword) p.keyword = query.value.keyword
  return p
}

const fmtDate = (_r, _c, v) => v ? String(v).replace('T', ' ').slice(0, 16) : ''
const loadData = async () => {
  list.value = []
  total.value = 0

  if (activeType.value === 'all') {
    await Promise.all([
      loadOrders(), loadDeliveries(), loadReturnOrders(), loadReturnDeliveries()
    ])
    sortAndDedup()
  } else if (activeType.value === 'order') {
    await loadOrders()
  } else if (activeType.value === 'delivery') {
    await loadDeliveries()
  } else if (activeType.value === 'return_order') {
    await loadReturnOrders()
  } else if (activeType.value === 'return_delivery') {
    await loadReturnDeliveries()
  }
}

const loadOrders = async () => {
  try {
    const res = await getSalesOrders(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'order'; i.no = i.code })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

const loadDeliveries = async () => {
  try {
    const res = await getSalesDeliveries(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'delivery'; i.no = i.delivery_no })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

const loadReturnOrders = async () => {
  try {
    const res = await getSalesReturns(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'return_order'; i.no = i.code })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

const loadReturnDeliveries = async () => {
  try {
    const res = await getReturnDeliveries(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'return_delivery'; i.no = i.code })
    list.value.push(...items)
    total.value += res.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

const sortAndDedup = () => {
  list.value.sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
}

const getSummary = ({ columns, data }) => {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (col.property === 'total_amount') {
      const val = data.reduce((s, r) => s + Number(r[col.property] || 0), 0)
      sums[idx] = `¥${val.toFixed(2)}`
    } else {
      sums[idx] = ''
    }
  })
  return sums
}

const openDocument = (row) => {
  const routeMap = {
    order: '/sales',
    delivery: '/sales-deliveries',
    return_order: '/sales-returns',
    return_delivery: '/return-deliveries'
  }
  const path = routeMap[row._type]
  if (path) router.push({ path, query: { id: row.id } })
}

const handleExport = async () => {
  try {
    const params = {}
    if (activeType.value && activeType.value !== 'all') params.type = activeType.value === 'order' ? 'sales_order' : activeType.value === 'delivery' ? 'sales_delivery' : activeType.value === 'return_order' ? 'sales_return_order' : 'return_delivery'
    if (query.value.date_range?.length === 2) { params.start_date = query.value.date_range[0]; params.end_date = query.value.date_range[1] }
    if (query.value.keyword) params.keyword = query.value.keyword
    const res = await exportDocuments(params)
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `销售单据导出_${new Date().toISOString().slice(0,10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

onMounted(async () => {
  const [c, w, s] = await Promise.all([
    getCustomers({ page_size: 1000 }),
    getWarehouses({ page_size: 100 }),
    getSalesmen({ page_size: 100 })
  ])
  customers.value = c.data?.list || c.data || []
  warehouses.value = w.data?.list || w.data || []
  salesmen.value = s.data?.list || s.data || []
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

.create-menu { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 8px }
.create-item {
  display: flex; align-items: center; gap: 12px; padding: 16px;
  border: 1px solid #e8e8e8; border-radius: 8px; cursor: pointer; transition: all 0.15s;
}
.create-item:hover { border-color: #409eff; background: #f0f7ff }
.create-icon { font-size: 28px }
.create-title { font-size: 14px; font-weight: 600; color: #303133 }
.create-desc { font-size: 12px; color: #909399; margin-top: 2px }
</style>
