<template>
  <div>
    <el-row :gutter="16">
      <!-- 客户应收 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>客户应收</span>
              <span style="font-size:16px;color:#f56c6c;font-weight:bold">总计：¥{{ Number(receivables.total_receivable || 0).toFixed(2) }}</span>
            </div>
          </template>
          <el-input v-model="receivableKeyword" placeholder="搜索客户" clearable style="margin-bottom:12px" @input="loadReceivables" />
          <el-table :data="receivables.items || []" border size="small" @row-click="showReceivableDetail">
            <el-table-column prop="customer_name" label="客户" />
            <el-table-column prop="phone" label="电话" width="120" />
            <el-table-column prop="receivable_balance" label="应收余额" width="120" align="right">
              <template #default="{ row }">
                <span style="color:#f56c6c">¥{{ Number(row.receivable_balance).toFixed(2) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 供应商应付 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>供应商应付</span>
              <span style="font-size:16px;color:#e6a23c;font-weight:bold">总计：¥{{ Number(payables.total_payable || 0).toFixed(2) }}</span>
            </div>
          </template>
          <el-input v-model="payableKeyword" placeholder="搜索供应商" clearable style="margin-bottom:12px" @input="loadPayables" />
          <el-table :data="payables.items || []" border size="small" @row-click="showPayableDetail">
            <el-table-column prop="supplier_name" label="供应商" />
            <el-table-column prop="phone" label="电话" width="120" />
            <el-table-column prop="payable_balance" label="应付余额" width="120" align="right">
              <template #default="{ row }">
                <span style="color:#e6a23c">¥{{ Number(row.payable_balance).toFixed(2) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 客户收款明细弹窗 -->
    <el-dialog v-model="receivableDetailVisible" title="客户收款明细" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="客户">{{ receivableDetail.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="应收余额">
          <span style="color:#f56c6c">¥{{ Number(receivableDetail.receivable_balance||0).toFixed(2) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="累计已收">¥{{ Number(receivableDetail.total_received||0).toFixed(2) }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="receivableDetail.receipts || []" border size="small" style="margin-top:16px">
        <el-table-column prop="code" label="单号" width="150" />
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ Number(row.amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="payment_method" label="方式" width="100" />
        <el-table-column prop="status" label="状态" width="80" />
        <el-table-column prop="created_at" label="时间" width="170" />
      </el-table>
    </el-dialog>

    <!-- 供应商付款明细弹窗 -->
    <el-dialog v-model="payableDetailVisible" title="供应商付款明细" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="供应商">{{ payableDetail.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="应付余额">
          <span style="color:#e6a23c">¥{{ Number(payableDetail.payable_balance||0).toFixed(2) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="累计已付">¥{{ Number(payableDetail.total_paid||0).toFixed(2) }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="payableDetail.payments || []" border size="small" style="margin-top:16px">
        <el-table-column prop="code" label="单号" width="150" />
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ Number(row.amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="payment_method" label="方式" width="100" />
        <el-table-column prop="status" label="状态" width="80" />
        <el-table-column prop="created_at" label="时间" width="170" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getReceivablesSummary, getReceivableDetail, getPayablesSummary, getPayableDetail } from '../../api'

const receivables = ref({})
const payables = ref({})
const receivableKeyword = ref('')
const payableKeyword = ref('')

const receivableDetailVisible = ref(false)
const receivableDetail = ref({})
const payableDetailVisible = ref(false)
const payableDetail = ref({})

const loadReceivables = async () => {
  const res = await getReceivablesSummary()
  receivables.value = res.data || {}
}

const loadPayables = async () => {
  const res = await getPayablesSummary()
  payables.value = res.data || {}
}

const showReceivableDetail = async (row) => {
  const res = await getReceivableDetail(row.customer_id)
  receivableDetail.value = res.data || res
  receivableDetailVisible.value = true
}

const showPayableDetail = async (row) => {
  const res = await getPayableDetail(row.supplier_id)
  payableDetail.value = res.data || res
  payableDetailVisible.value = true
}

onMounted(() => { loadReceivables(); loadPayables() })
</script>
