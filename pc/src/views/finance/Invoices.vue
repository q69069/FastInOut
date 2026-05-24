<template>
  <div class="order-page">
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">发票管理</span>
        </div>
        <div class="header-info">
          <span class="info-item">制单人：{{ authStore.displayName }}</span>
          <span class="info-item">{{ now }}</span>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="openForm(null)">新增发票</el-button>
        </div>
      </div>
    </el-card>

    <!-- 筛选区域 -->
    <el-card style="margin-top: 12px">
      <el-row :gutter="12">
        <el-col :span="4">
          <el-select v-model="tabType" @change="loadData" style="width:100%">
            <el-option label="销售发票" value="sales" />
            <el-option label="采购发票" value="purchase" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input v-model="queryFilter.keyword" placeholder="发票号码/代码" clearable @clear="loadData" @keyup.enter="loadData" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="queryFilter.status" placeholder="状态" clearable @change="loadData">
            <el-option label="未认证" :value="1" />
            <el-option label="已认证" :value="2" />
            <el-option label="已作废" :value="3" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 表格 -->
    <el-card style="margin-top: 12px">
      <el-table :data="list" border stripe>
        <el-table-column prop="invoice_code" label="发票代码" width="120" />
        <el-table-column prop="invoice_no" label="发票号码" width="120" />
        <el-table-column prop="amount" label="金额" width="100" align="right">
          <template #default="{ row }">{{ (row.amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="tax_amount" label="税额" width="100" align="right">
          <template #default="{ row }">{{ (row.tax_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="total_amount" label="价税合计" width="100" align="right">
          <template #default="{ row }">{{ (row.total_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="invoice_date" label="开票日期" width="110" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 2 ? 'success' : row.status === 3 ? 'danger' : 'info'" size="small">
              {{ statusMap[row.status] || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 1" type="primary" link size="small" @click="openForm(row)">编辑</el-button>
            <el-button v-if="row.status === 1" type="success" link size="small" @click="handleCertify(row)">认证</el-button>
            <el-button v-if="row.status === 1" type="warning" link size="small" @click="handleVoid(row)">作废</el-button>
            <el-button v-if="row.status !== 2" type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 16px; display: flex; justify-content: flex-end">
        <el-pagination
          v-model:current-page="queryFilter.page"
          v-model:page-size="queryFilter.page_size"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadData"
          @size-change="loadData"
        />
      </div>
    </el-card>

    <!-- 发票号码编辑弹窗 -->
    <el-dialog v-model="editDialogVisible" :title="editForm.id ? '编辑发票' : '新增发票'" width="550px">
      <el-form :model="editForm" label-width="90px">
        <el-form-item label="发票代码">
          <el-input v-model="editForm.invoice_code" />
        </el-form-item>
        <el-form-item label="发票号码">
          <el-input v-model="editForm.invoice_no" />
        </el-form-item>
        <el-form-item v-if="tabType === 'sales'" label="客户">
          <el-select v-model="editForm.customer_id" filterable placeholder="选择客户" style="width:100%">
            <el-option v-for="c in customerList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-else label="供应商">
          <el-select v-model="editForm.supplier_id" filterable placeholder="选择供应商" style="width:100%">
            <el-option v-for="s in supplierList" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="金额">
              <el-input-number v-model="editForm.amount" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="税额">
              <el-input-number v-model="editForm.tax_amount" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="价税合计">
              <el-input-number v-model="editForm.total_amount" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="开票日期">
          <el-date-picker v-model="editForm.invoice_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getInvoices, createInvoice, updateInvoice, deleteInvoice, certifyInvoice, voidInvoice, getCustomers, getSuppliers } from '../../api'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const tabType = ref('sales')
const saving = ref(false)
const list = ref([])
const total = ref(0)
const statusMap = { 1: '未认证', 2: '已认证', 3: '已作废' }

const queryFilter = ref({ page: 1, page_size: 20, keyword: '', status: null })

const customerList = ref([])
const supplierList = ref([])

const editDialogVisible = ref(false)
const editForm = ref({})

const loadData = async () => {
  try {
    const params = { ...queryFilter.value }
    if (!params.keyword) delete params.keyword
    if (!params.status) delete params.status
    const res = await getInvoices({ ...params, invoice_type: tabType.value })
    list.value = res.data || []
    total.value = res.total || 0
  } catch (e) { console.error(e) }
}

const loadDropdowns = async () => {
  try {
    const [c, s] = await Promise.all([
      getCustomers({ page: 1, page_size: 100 }),
      getSuppliers({ page: 1, page_size: 100 })
    ])
    customerList.value = c.data || []
    supplierList.value = s.data || []
  } catch (e) { console.error(e) }
}

const openForm = (row) => {
  editForm.value = row ? { ...row } : {
    invoice_type: tabType.value,
    invoice_code: '',
    invoice_no: '',
    customer_id: null,
    supplier_id: null,
    amount: 0,
    tax_amount: 0,
    total_amount: 0,
    invoice_date: null,
    remark: ''
  }
  editDialogVisible.value = true
}

const handleEditSave = async () => {
  if (editForm.value.id) {
    await updateInvoice(editForm.value.id, { ...editForm.value, invoice_type: tabType.value })
  } else {
    await createInvoice({ ...editForm.value, invoice_type: tabType.value })
  }
  ElMessage.success('保存成功')
  editDialogVisible.value = false
  loadData()
}

const handleCertify = async (row) => {
  await ElMessageBox.confirm('确认认证该发票？', '提示', { type: 'warning' })
  await certifyInvoice(row.id)
  ElMessage.success('认证成功')
  loadData()
}

const handleVoid = async (row) => {
  await ElMessageBox.confirm('确认作废该发票？', '提示', { type: 'warning' })
  await voidInvoice(row.id)
  ElMessage.success('已作废')
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  await deleteInvoice(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(async () => {
  await loadDropdowns()
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