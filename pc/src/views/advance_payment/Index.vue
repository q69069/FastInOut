<template>
  <div class="order-page">
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">预收付款</span>
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
        <el-select v-model="queryFilter.type" placeholder="类型" clearable style="width:120px" @change="loadData">
          <el-option label="预收款" value="receivable" />
          <el-option label="预付款" value="payable" />
        </el-select>
        <el-select v-model="queryFilter.status" placeholder="状态" clearable style="width:120px" @change="loadData">
          <el-option label="待确认" value="pending" />
          <el-option label="已确认" value="confirmed" />
        </el-select>
        <el-button @click="queryFilter.page=1;loadData()">查询</el-button>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="单号" width="160" />
        <el-table-column prop="type" label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.type==='receivable'?'success':'warning'" size="small">{{ row.type==='receivable'?'预收款':'预付款' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="party_name" label="对方" />
        <el-table-column prop="amount" label="金额" width="110" align="right">
          <template #default="{ row }">¥{{ Number(row.amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="remaining_amount" label="剩余" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.remaining_amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status==='confirmed'?'success':'info'" size="small">{{ row.status==='confirmed'?'已确认':'待确认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
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
    <el-dialog v-model="detailVisible" title="预收付款详情" width="500px">
      <el-descriptions :column="2" border v-if="detail">
        <el-descriptions-item label="单号">{{ detail.code }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="detail.type === 'receivable' ? 'success' : 'warning'" size="small">{{ detail.type === 'receivable' ? '预收款' : '预付款' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="对方">{{ detail.party_name }}</el-descriptions-item>
        <el-descriptions-item label="金额">¥{{ Number(detail.amount || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="已用">¥{{ Number(detail.used_amount || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="剩余">¥{{ Number(detail.remaining_amount || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="detail.status === 'confirmed' ? 'success' : 'info'" size="small">{{ detail.status === 'confirmed' ? '已确认' : '待确认' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdvancePayments, confirmAdvancePayment } from '../../api'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const list = ref([])
const total = ref(0)

const queryFilter = ref({ page: 1, page_size: 20 })

const detailVisible = ref(false)
const detail = ref({})

const loadData = async () => {
  const res = await getAdvancePayments(queryFilter.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDetail = (row) => {
  detail.value = row
  detailVisible.value = true
}

const handleConfirm = async (row) => {
  await ElMessageBox.confirm('确认此预收付款？', '确认', { type: 'warning' })
  await confirmAdvancePayment(row.id)
  ElMessage.success('确认成功')
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