<template>
  <div class="order-page">
    <!-- 顶部：标题栏 -->
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">交账单据</span>
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
        <el-tab-pane label="交账记录" name="settlement" />
        <el-tab-pane label="异常监控" name="monitor" />
      </el-tabs>

      <el-form inline @submit.prevent="loadData">
        <el-form-item label="时间">
          <el-date-picker v-model="query.date_range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" clearable placeholder="单据号/业务员" style="width:150px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="clearFilter">清空</el-button>
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
        <el-table-column prop="no" label="单据号" width="160">
          <template #default="{ row }">{{ row.no || row.settlement_no }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="150" />
        <el-table-column prop="employee_name" label="业务员" />
        <el-table-column prop="total_amount" label="金额" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.total_sales || row.total_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label || row.status }}</el-tag>
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

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="单据详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="单号">{{ detail.no || detail.settlement_no }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag size="small" :type="typeTagMap[detail._type]?.type">{{ typeTagMap[detail._type]?.label }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="业务员">{{ detail.employee_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusMap[detail.status]?.type">{{ statusMap[detail.status]?.label }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detail.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSettlements, getSettlement } from '../../api'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const activeType = ref('all')
const detailVisible = ref(false)
const detail = ref({})

const list = ref([])
const total = ref(0)

const query = ref({ page: 1, page_size: 20, date_range: [], keyword: '' })

const statusMap = {
  pending: { label: '待审核', type: 'warning' },
  audited: { label: '已通过', type: 'success' },
  rejected: { label: '已驳回', type: 'danger' },
  normal: { label: '正常', type: 'success' },
  abnormal: { label: '异常', type: 'danger' },
}

const typeTagMap = {
  settlement: { label: '交账记录', type: '' },
  monitor: { label: '异常监控', type: 'warning' },
}

const onTypeChange = () => { query.value.page = 1; loadData() }

const clearFilter = () => {
  query.value = { page: 1, page_size: 20, date_range: [], keyword: '' }
  loadData()
}

const buildParams = () => {
  const p = { page: query.value.page, page_size: query.value.page_size }
  if (query.value.date_range?.length === 2) { p.start_date = query.value.date_range[0]; p.end_date = query.value.date_range[1] }
  if (query.value.keyword) p.keyword = query.value.keyword
  return p
}

const loadData = async () => {
  list.value = []
  total.value = 0
  if (activeType.value === 'all') {
    await loadSettlements()
  } else if (activeType.value === 'settlement') {
    await loadSettlements()
  }
}

const loadSettlements = async () => {
  try {
    const res = await getSettlements(buildParams())
    const items = (res.data?.list || res.data || [])
    items.forEach(i => { i._type = 'settlement'; i.no = i.settlement_no })
    list.value.push(...items)
    total.value += res.total || 0
  } catch {}
}

const getSummary = ({ columns, data }) => {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (col.property === 'total_amount' || col.property === 'total_sales') {
      const val = data.reduce((s, r) => s + Number(r[col.property] || 0), 0)
      sums[idx] = `¥${val.toFixed(2)}`
    } else { sums[idx] = '' }
  })
  return sums
}

const showDetail = (row) => { detail.value = row; detailVisible.value = true }

onMounted(() => { loadData() })
</script>

<style scoped>
.order-page { padding: 16px; background: #f5f5f5; min-height: 100vh }
.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px }
.page-title { display: flex; align-items: center; gap: 12px }
.title-text { font-size: 18px; font-weight: 600; color: #303133 }
.header-info { display: flex; gap: 24px; color: #909399; font-size: 13px }
.filter-card { margin-top: 12px }
.list-card { margin-top: 12px }
</style>
