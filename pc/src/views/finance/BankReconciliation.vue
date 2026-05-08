<template>
  <div class="order-page">
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">银行对账</span>
        </div>
        <div class="header-info">
          <span class="info-item">制单人：{{ authStore.displayName }}</span>
          <span class="info-item">{{ now }}</span>
        </div>
        <div class="header-actions" />
      </div>
    </el-card>

    <!-- 对账汇总 -->
    <div class="summary-section">
      <el-descriptions :column="5" border size="small">
        <el-descriptions-item label="总收入">¥{{ summary.total_credit?.toFixed(2) || '0.00' }}</el-descriptions-item>
        <el-descriptions-item label="总支出">¥{{ summary.total_debit?.toFixed(2) || '0.00' }}</el-descriptions-item>
        <el-descriptions-item label="余额">
          <span :style="{ color: summary.balance >= 0 ? '#67c23a' : '#f56c6c' }">¥{{ summary.balance?.toFixed(2) || '0.00' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="已匹配">{{ summary.matched_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="未匹配">{{ summary.unmatched_count || 0 }}</el-descriptions-item>
      </el-descriptions>
    </div>
  <!-- 列表 -->
    <el-card class="form-card">
      <el-form inline :model="queryFilter" style="margin-bottom:12px">
        <el-select v-model="queryFilter.matched" placeholder="匹配状态" clearable style="width:120px" @change="loadData">
          <el-option label="已匹配" :value="true" />
          <el-option label="未匹配" :value="false" />
        </el-select>
        <el-date-picker v-model="queryFilter.date_range" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width:240px" @change="loadData" />
        <el-button @click="queryFilter.page=1;loadData()">查询</el-button>
        <el-button type="primary" @click="handleAutoMatch">自动匹配</el-button>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="transaction_date" label="交易日期" width="120" />
        <el-table-column prop="description" label="摘要" />
        <el-table-column prop="income" label="收入" width="100" align="right">
          <template #default="{ row }">¥{{ (row.income||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="expense" label="支出" width="100" align="right">
          <template #default="{ row }">¥{{ (row.expense||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="balance" label="余额" width="100" align="right">
          <template #default="{ row }">¥{{ (row.balance||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="matched" label="匹配状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.matched?'success':'warning'" size="small">{{ row.matched?'已匹配':'未匹配' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:12px" :total="total" :page-size="queryFilter.page_size" background layout="prev,pager,next" v-model:current-page="queryFilter.page" @current-change="loadData" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getBankStatements, autoMatchBankStatements, getBankSummary } from '../../api'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const list = ref([])
const total = ref(0)
const summary = ref({})

const queryFilter = ref({ page: 1, page_size: 20, matched: null, date_range: [] })

const loadData = async () => {
  const res = await getBankStatements(queryFilter.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadSummary = async () => {
  const res = await getBankSummary()
  summary.value = res.data || {}
}

const handleAutoMatch = async () => {
  const res = await autoMatchBankStatements()
  ElMessage.success(res.message || '自动匹配完成')
  loadData()
  loadSummary()
}

onMounted(() => {
  loadData()
  loadSummary()
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
.summary-section { margin-top: 16px }
</style>