<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>客户对账</span>
          <el-button type="primary" @click="showDialog()">生成对账单</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="待确认" value="pending" />
            <el-option label="已确认" value="confirmed" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" @click="loadData">查询</el-button></el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="单号" width="150" />
        <el-table-column prop="customer_name" label="客户" width="120" />
        <el-table-column prop="total_sales" label="销售" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_sales||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="total_returns" label="退货" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_returns||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="total_receipts" label="已收" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_receipts||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="balance" label="余额" width="100" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.balance > 0 ? '#f56c6c' : '' }">¥{{ Number(row.balance||0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status==='confirmed'?'success':'info'" size="small">{{ row.status==='confirmed'?'已确认':'待确认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="success" v-if="row.status==='pending'" @click="handleConfirm(row)">确认</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>

    <el-dialog v-model="dialogVisible" title="生成对账单" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="客户" required>
          <el-select v-model="form.customer_id" filterable placeholder="选择客户" style="width:100%">
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="期间" required>
          <el-date-picker v-model="form.date_range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="handleGenerate" :loading="saving">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getReconciliations, createReconciliation, confirmReconciliation, getCustomers } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, status: '' })
const dialogVisible = ref(false)
const saving = ref(false)
const customers = ref([])
const form = ref({ customer_id: null, date_range: [], remark: '' })

const loadData = async () => {
  const res = await getReconciliations(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadCustomers = async () => {
  const res = await getCustomers()
  customers.value = res.data || []
}

const showDialog = () => {
  form.value = { customer_id: null, date_range: [], remark: '' }
  dialogVisible.value = true
}

const handleGenerate = async () => {
  if (!form.value.customer_id) return ElMessage.warning('请选择客户')
  if (!form.value.date_range?.length) return ElMessage.warning('请选择期间')
  saving.value = true
  try {
    await createReconciliation({
      customer_id: form.value.customer_id,
      period_start: form.value.date_range[0],
      period_end: form.value.date_range[1],
      remark: form.value.remark
    })
    ElMessage.success('对账单生成成功')
    dialogVisible.value = false
    loadData()
  } finally { saving.value = false }
}

const handleConfirm = async (row) => {
  await confirmReconciliation(row.id)
  ElMessage.success('对账确认成功')
  loadData()
}

onMounted(() => { loadData(); loadCustomers() })
</script>
