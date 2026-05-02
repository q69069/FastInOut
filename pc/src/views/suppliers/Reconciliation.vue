<template>
  <div>
    <el-card style="margin-bottom:16px">
      <template #header>供应商应付汇总</template>
      <el-table :data="summaryList" border stripe @row-click="viewStatement">
        <el-table-column prop="supplier_name" label="供应商" />
        <el-table-column prop="payable_balance" label="应付余额" width="130">
          <template #default="{ row }">
            <span :style="{ color: row.payable_balance > 0 ? '#f56c6c' : '#67c23a' }">
              ¥{{ (row.payable_balance || 0).toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="contact" label="联系人" width="100" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="viewStatement(row)">对账</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="statementVisible" title="供应商对账单" width="900px" top="5vh">
      <div v-if="statement">
        <div style="display:flex;justify-content:space-between;margin-bottom:16px">
          <div>
            <strong>供应商：</strong>{{ statement.supplier_name }}
            <span style="margin-left:20px"><strong>期间：</strong>{{ statement.start_date }} 至 {{ statement.end_date }}</span>
          </div>
          <div>
            <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="margin-right:8px" @change="reloadStatement" />
          </div>
        </div>
        <el-table :data="statement.items" border stripe size="small" max-height="300">
          <el-table-column prop="date" label="日期" width="100" />
          <el-table-column prop="code" label="单号" width="160" />
          <el-table-column prop="type" label="类型" width="90" />
          <el-table-column prop="purchase" label="采购" width="100">
            <template #default="{ row }">{{ row.purchase ? '¥' + row.purchase.toFixed(2) : '¥0.00' }}</template>
          </el-table-column>
          <el-table-column prop="return" label="退货" width="100">
            <template #default="{ row }">{{ row.return ? '¥' + row.return.toFixed(2) : '¥0.00' }}</template>
          </el-table-column>
          <el-table-column prop="payment" label="付款" width="100">
            <template #default="{ row }">{{ row.payment ? '¥' + row.payment.toFixed(2) : '¥0.00' }}</template>
          </el-table-column>
          <el-table-column prop="balance" label="余额" width="110">
            <template #default="{ row }">
              <span style="font-weight:bold">¥{{ (row.balance || 0).toFixed(2) }}</span>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top:16px;display:flex;gap:24px">
          <span>期初应付：<b>¥{{ (statement.opening_balance || 0).toFixed(2) }}</b></span>
          <span>本期采购：<b>¥{{ (statement.purchase_amount || 0).toFixed(2) }}</b></span>
          <span>本期退货：<b>¥{{ (statement.return_amount || 0).toFixed(2) }}</b></span>
          <span>本期付款：<b>¥{{ (statement.payment_amount || 0).toFixed(2) }}</b></span>
          <span style="color:#f56c6c">期末应付：<b>¥{{ (statement.closing_balance || 0).toFixed(2) }}</b></span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSupplierReconSummary, getSupplierStatement } from '../../api'

const summaryList = ref([])
const statementVisible = ref(false)
const statement = ref(null)
const currentSupplierId = ref(null)
const dateRange = ref(null)

const loadSummary = async () => {
  const res = await getSupplierReconSummary()
  summaryList.value = res.data || []
}

const viewStatement = async (row) => {
  currentSupplierId.value = row.supplier_id
  dateRange.value = null
  await loadStatement()
  statementVisible.value = true
}

const loadStatement = async () => {
  const params = { supplier_id: currentSupplierId.value }
  if (dateRange.value) {
    params.start_date = dateRange.value[0]
    params.end_date = dateRange.value[1]
  }
  const res = await getSupplierStatement(params)
  statement.value = res.data
}

const reloadStatement = () => {
  loadStatement()
}

onMounted(() => loadSummary())
</script>
