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
        <el-tab-pane label="库存查询" name="inventory" />
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
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 列表 -->
    <el-card class="list-card">
      <el-table :data="list" border stripe>
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
        <el-table-column prop="created_at" label="时间" width="150" />
        <el-table-column prop="warehouse_name" label="仓库" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label || row.status }}</el-tag>
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

    <!-- 多窗口详情弹窗 -->
    <template v-for="(dlg, key) in dialogs" :key="key">
      <el-dialog :model-value="dlg.visible" :title="'单据详情 - ' + (dlg.data?.no || dlg.data?.code || dlg.data?.transfer_no || '')" width="600px" @update:model-value="v => { if (!v) closeDialog(key) }">
        <div v-if="dlg.loading" style="text-align:center;padding:40px">加载中...</div>
        <template v-else-if="dlg.data">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="单号">{{ dlg.data.no || dlg.data.code || dlg.data.transfer_no }}</el-descriptions-item>
            <el-descriptions-item label="类型">
              <el-tag size="small" :type="typeTagMap[dlg.data._type]?.type">{{ typeTagMap[dlg.data._type]?.label }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="statusMap[dlg.data.status]?.type">{{ statusMap[dlg.data.status]?.label || dlg.data.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="仓库">{{ dlg.data.warehouse_name }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ dlg.data.created_at }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ dlg.data.remark || '-' }}</el-descriptions-item>
          </el-descriptions>
          <el-table v-if="dlg.data.items?.length" :data="dlg.data.items" border size="small" style="margin-top:16px">
            <el-table-column prop="product_name" label="商品" />
            <el-table-column prop="quantity" label="数量" width="80" align="right" />
            <el-table-column prop="remark" label="备注" />
          </el-table>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  getInventory, getTransfers, getTransfer,
  getStocktaking, getStocktakingDetail,
  getVehicleLoads, getVehicleLoad,
  getDamageReports, getDamageReport,
  getWarehouses
} from '../../api'
import { useAuthStore } from '../../stores/auth'
import { Box, Calendar, Van, Warning } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const activeType = ref('all')
const createDialogVisible = ref(false)
const dialogs = ref({})

const warehouses = ref([])
const list = ref([])
const total = ref(0)

const query = ref({ page: 1, page_size: 20, date_range: [], warehouse_id: '', keyword: '' })

const statusMap = {
  0: { label: '草稿', type: 'info' },
  1: { label: '进行中', type: 'warning' },
  2: { label: '已完成', type: 'success' },
  3: { label: '已关闭', type: '' },
  4: { label: '已作废', type: 'danger' },
  pending: { label: '待处理', type: 'warning' },
  confirmed: { label: '已确认', type: 'success' },
  settled: { label: '已结清', type: 'success' },
  voided: { label: '已作废', type: 'info' },
  transferring: { label: '调拨中', type: 'warning' },
  completed: { label: '已完成', type: 'success' },
}

const typeTagMap = {
  inventory: { label: '库存查询', type: '' },
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

const loadData = async () => {
  list.value = []
  total.value = 0
  if (activeType.value === 'all') {
    await Promise.all([loadTransfers(), loadStocktakes(), loadVehicles(), loadDamages()])
    list.value.sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
  } else if (activeType.value === 'inventory') { await loadInventory() }
  else if (activeType.value === 'transfer') { await loadTransfers() }
  else if (activeType.value === 'stocktake') { await loadStocktakes() }
  else if (activeType.value === 'vehicle') { await loadVehicles() }
  else if (activeType.value === 'damage') { await loadDamages() }
}

const loadInventory = async () => {
  try {
    const res = await getInventory(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'inventory'; i.no = i.product_name })
    list.value.push(...items)
    total.value += res.total || 0
  } catch {}
}

const loadTransfers = async () => {
  try {
    const res = await getTransfers(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'transfer'; i.no = i.transfer_no })
    list.value.push(...items)
    total.value += res.total || 0
  } catch {}
}

const loadStocktakes = async () => {
  try {
    const res = await getStocktaking(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'stocktake'; i.no = i.code })
    list.value.push(...items)
    total.value += res.total || 0
  } catch {}
}

const loadVehicles = async () => {
  try {
    const res = await getVehicleLoads(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'vehicle'; i.no = i.load_no })
    list.value.push(...items)
    total.value += res.total || 0
  } catch {}
}

const loadDamages = async () => {
  try {
    const res = await getDamageReports(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'damage'; i.no = i.report_no })
    list.value.push(...items)
    total.value += res.total || 0
  } catch {}
}

const openDocument = async (row) => {
  const key = `${row._type}_${row.id}`
  if (dialogs.value[key]) {
    dialogs.value[key].visible = true
    dialogs.value[key].data = row
    return
  }
  dialogs.value[key] = { visible: true, data: row, loading: true }
  try {
    const apiMap = {
      transfer: getTransfer,
      stocktake: getStocktakingDetail,
      vehicle: getVehicleLoad,
      damage: getDamageReport
    }
    const api = apiMap[row._type]
    if (api) {
      const res = await api(row.id)
      const data = res.data || res
      if (dialogs.value[key]) {
        dialogs.value[key].data = { ...row, ...data }
        dialogs.value[key].loading = false
      }
    } else {
      if (dialogs.value[key]) dialogs.value[key].loading = false
    }
  } catch {
    if (dialogs.value[key]) dialogs.value[key].loading = false
  }
}

const closeDialog = (key) => {
  if (dialogs.value[key]) {
    dialogs.value[key].visible = false
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
