<template>
  <div class="order-page">
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">客户对账</span>
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
          <el-option label="待确认" value="pending" />
          <el-option label="已确认" value="confirmed" />
        </el-select>
        <el-button @click="queryFilter.page=1;loadData()">查询</el-button>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="单号" width="160" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="total_sales" label="销售总额" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.total_sales||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="total_receipts" label="已收" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_receipts||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="balance" label="余额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.balance||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status==='confirmed'?'success':'info'" size="small">{{ row.status==='confirmed'?'已确认':'待确认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" :formatter="fmtDate" />
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="showDetail(row)">详情</el-button>
            <el-button v-if="row.status==='pending'" size="small" type="success" @click="handleConfirm(row)">确认</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:12px" :total="total" :page-size="queryFilter.page_size" background layout="prev,pager,next" v-model:current-page="queryFilter.page" @current-change="loadData" />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="对账单详情" width="600px">
      <el-descriptions :column="2" border v-if="detail">
        <el-descriptions-item label="单号">{{ detail.code }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ detail.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="销售总额">¥{{ Number(detail.total_sales || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="退货总额">¥{{ Number(detail.total_returns || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="已收">¥{{ Number(detail.total_receipts || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="余额">¥{{ Number(detail.balance || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="detail.status === 'confirmed' ? 'success' : 'info'" size="small">{{ detail.status === 'confirmed' ? '已确认' : '待确认' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ fmtDateVal(detail.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getReconciliations, confirmReconciliation } from '../../api'
import { useAuthStore } from '../../stores/auth'

const fmtDateVal = (v) => v ? String(v).replace("T", " ").slice(0, 16) : ""
const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const list = ref([])
const total = ref(0)

const queryFilter = ref({ page: 1, page_size: 20 })

const detailVisible = ref(false)
const detail = ref({})

const loadData = async () => {
  const res = await getReconciliations(queryFilter.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDetail = (row) => {
  detail.value = row
  detailVisible.value = true
}

const handleConfirm = async (row) => {
  await ElMessageBox.confirm('确认此对账单？', '确认', { type: 'warning' })
  await confirmReconciliation(row.id)
  ElMessage.success('对账确认成功')
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
</style>
