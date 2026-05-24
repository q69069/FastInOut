<template>
  <div class="order-page">
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">费用管理</span>
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
          <el-option label="待审批" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
        <el-button @click="queryFilter.page=1;loadData()">查询</el-button>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="expense_no" label="单号" width="160" />
        <el-table-column prop="category_name" label="类别" />
        <el-table-column prop="amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="payee" label="收款人" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status==='approved'?'success':row.status==='rejected'?'danger':'info'" size="small">
              {{ row.status==='approved'?'已通过':row.status==='rejected'?'已驳回':'待审批' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" :formatter="fmtDate" />
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="showDetail(row)">详情</el-button>
            <el-button v-if="row.status==='pending'" size="small" type="success" @click="handleApprove(row)">通过</el-button>
            <el-button v-if="row.status==='pending'" size="small" type="danger" @click="handleReject(row)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:12px" :total="total" :page-size="queryFilter.page_size" background layout="prev,pager,next" v-model:current-page="queryFilter.page" @current-change="loadData" />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="费用详情" width="500px">
      <el-descriptions :column="1" border v-if="detail">
        <el-descriptions-item label="单号">{{ detail.expense_no }}</el-descriptions-item>
        <el-descriptions-item label="类别">{{ detail.category_name }}</el-descriptions-item>
        <el-descriptions-item label="金额">¥{{ Number(detail.amount || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="收款人">{{ detail.payee || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="detail.status === 'approved' ? 'success' : detail.status === 'rejected' ? 'danger' : 'info'">
            {{ detail.status === 'approved' ? '已通过' : detail.status === 'rejected' ? '已驳回' : '待审批' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="说明">{{ detail.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ fmtDateVal(detail.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExpenses, getExpense, approveExpense, rejectExpense, getExpenseCategories, createExpenseCategory, deleteExpenseCategory } from '../../api'
import { useAuthStore } from '../../stores/auth'

const fmtDateVal = (v) => v ? String(v).replace("T", " ").slice(0, 16) : ""
const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const list = ref([])
const total = ref(0)
const categories = ref([])
const newCategory = ref('')
const detail = ref({})
const detailVisible = ref(false)

const queryFilter = ref({ page: 1, page_size: 20, status: '' })

const loadData = async () => {
  const res = await getExpenses(queryFilter.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadCategories = async () => {
  const res = await getExpenseCategories()
  categories.value = res.data || []
}

const showDetail = async (row) => {
  const res = await getExpense(row.id)
  detail.value = res.data || res
  detailVisible.value = true
}

const handleApprove = async (row) => {
  await ElMessageBox.confirm('确认通过此费用？', '审批', { type: 'success' })
  await approveExpense(row.id)
  ElMessage.success('已通过')
  loadData()
}

const handleReject = async (row) => {
  await ElMessageBox.confirm('确认驳回此费用？', '驳回', { type: 'warning' })
  await rejectExpense(row.id)
  ElMessage.success('已驳回')
  loadData()
}

const addCategory = async () => {
  if (!newCategory.value) return
  await createExpenseCategory({ name: newCategory.value })
  newCategory.value = ''
  loadCategories()
}

const deleteCategory = async (row) => {
  await ElMessageBox.confirm(`确认删除类别"${row.name}"？`, '删除', { type: 'warning' })
  await deleteExpenseCategory(row.id)
  loadCategories()
}

onMounted(() => {
  loadCategories()
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
