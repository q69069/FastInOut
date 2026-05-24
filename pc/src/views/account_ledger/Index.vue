<template>
  <div class="order-page">
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">往来账</span>
        </div>
        <div class="header-info">
          <span class="info-item">{{ now }}</span>
        </div>
        <div class="header-actions" />
      </div>
    </el-card>

    <!-- 收款管理 -->
    <el-card class="form-card">
      <div class="section-title">收款管理</div>
      <el-table :data="receipts" border stripe>
        <el-table-column prop="code" label="单号" width="150" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ Number(row.amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="payment_method" label="方式" width="100" />
        <el-table-column prop="created_at" label="时间" width="180" :formatter="fmtDate" />
      </el-table>
    </el-card>

    <!-- 付款管理 -->
    <el-card class="form-card">
      <div class="section-title">付款管理</div>
      <el-table :data="payments" border stripe>
        <el-table-column prop="code" label="单号" width="150" />
        <el-table-column prop="supplier_name" label="供应商" />
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ Number(row.amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="payment_method" label="方式" width="100" />
        <el-table-column prop="created_at" label="时间" width="180" :formatter="fmtDate" />
      </el-table>
    </el-card>

    <!-- 应收账款 -->
    <el-card class="form-card">
      <div class="section-title">应收账款</div>
      <el-table :data="receivables" border stripe>
        <el-table-column prop="name" label="客户名称" />
        <el-table-column prop="balance" label="应收余额" width="150" align="right">
          <template #default="{ row }">¥{{ Number(row.balance || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="contact" label="联系人" width="120" />
        <el-table-column prop="phone" label="电话" width="150" />
      </el-table>
    </el-card>

    <!-- 应付账款 -->
    <el-card class="form-card">
      <div class="section-title">应付账款</div>
      <el-table :data="payables" border stripe>
        <el-table-column prop="name" label="供应商名称" />
        <el-table-column prop="balance" label="应付余额" width="150" align="right">
          <template #default="{ row }">¥{{ Number(row.balance || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="contact" label="联系人" width="120" />
        <el-table-column prop="phone" label="电话" width="150" />
      </el-table>
    </el-card>

    <!-- 收支流水 -->
    <el-card class="form-card">
      <div class="section-title">收支流水</div>
      <el-table :data="flowList" border stripe>
        <el-table-column prop="code" label="单号" width="150" />
        <el-table-column prop="type" label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.type === 'income' ? 'success' : 'danger'" size="small">
              {{ row.type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ Number(row.amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="party_name" label="对方" />
        <el-table-column prop="payment_method" label="方式" width="100" />
        <el-table-column prop="created_at" label="时间" width="180" :formatter="fmtDate" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getReceipts, getPayments, getReceivables, getPayables, getFinanceFlow } from '../../api'

const fmtDate = (_r, _c, v) => v ? String(v).replace("T", " ").slice(0, 16) : ""
const now = new Date().toLocaleString('zh-CN')

const receipts = ref([])
const payments = ref([])
const receivables = ref([])
const payables = ref([])
const flowList = ref([])

const loadData = async () => {
  const [r, p, rec, pay, f] = await Promise.all([
    getReceipts({ page_size: 100 }),
    getPayments({ page_size: 100 }),
    getReceivables(),
    getPayables(),
    getFinanceFlow({ page_size: 100 })
  ])
  receipts.value = r.data || []
  payments.value = p.data || []
  receivables.value = rec.data || []
  payables.value = pay.data || []
  flowList.value = f.data || []
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
.form-card { margin-top: 12px }
.section-title { font-size: 14px; font-weight: 600; color: #303133; margin: 0 0 16px; padding-left: 8px; border-left: 3px solid #409eff }
</style>