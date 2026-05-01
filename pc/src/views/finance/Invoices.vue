<template>
  <div>
    <el-tabs v-model="tabType" @tab-change="loadData">
      <el-tab-pane label="销售发票" name="sales" />
      <el-tab-pane label="采购发票" name="purchase" />
    </el-tabs>

    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div style="display:flex;gap:8px">
        <el-input v-model="query.keyword" placeholder="发票代码/号码" clearable style="width:200px" @keyup.enter="loadData" />
        <el-select v-model="query.status" placeholder="状态" clearable style="width:120px" @change="loadData">
          <el-option label="未认证" :value="1" />
          <el-option label="已认证" :value="2" />
          <el-option label="已作废" :value="3" />
        </el-select>
        <el-button type="primary" @click="loadData">查询</el-button>
      </div>
      <el-button type="primary" @click="openDialog()">新增发票</el-button>
    </div>

    <el-table :data="list" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="invoice_code" label="发票代码" width="120" />
      <el-table-column prop="invoice_no" label="发票号码" width="140" />
      <el-table-column :label="tabType === 'sales' ? '客户' : '供应商'" min-width="150">
        <template #default="{ row }">{{ tabType === 'sales' ? row.customer_name : row.supplier_name }}</template>
      </el-table-column>
      <el-table-column prop="amount" label="金额" width="100" />
      <el-table-column prop="tax_amount" label="税额" width="100" />
      <el-table-column prop="total_amount" label="价税合计" width="110" />
      <el-table-column prop="invoice_date" label="开票日期" width="110" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 2 ? 'success' : row.status === 3 ? 'info' : 'warning'" size="small">
            {{ statusMap[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button v-if="row.status === 1" size="small" type="success" @click="handleCertify(row)">认证</el-button>
          <el-button v-if="row.status !== 3" size="small" type="warning" @click="handleVoid(row)">作废</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="query.page"
      v-model:page-size="query.page_size"
      :total="total"
      layout="total, prev, pager, next"
      style="margin-top:16px;justify-content:flex-end"
      @current-change="loadData"
    />

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑发票' : '新增发票'" width="550px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="发票代码">
          <el-input v-model="form.invoice_code" />
        </el-form-item>
        <el-form-item label="发票号码">
          <el-input v-model="form.invoice_no" />
        </el-form-item>
        <el-form-item v-if="tabType === 'sales'" label="客户">
          <el-select v-model="form.customer_id" filterable placeholder="选择客户" style="width:100%">
            <el-option v-for="c in customerList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-else label="供应商">
          <el-select v-model="form.supplier_id" filterable placeholder="选择供应商" style="width:100%">
            <el-option v-for="s in supplierList" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="金额">
              <el-input-number v-model="form.amount" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="税额">
              <el-input-number v-model="form.tax_amount" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="价税合计">
              <el-input-number v-model="form.total_amount" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="开票日期">
          <el-date-picker v-model="form.invoice_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getInvoices, createInvoice, updateInvoice, deleteInvoice, certifyInvoice, voidInvoice, getCustomers, getSuppliers } from '../../api'

const tabType = ref('sales')
const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, keyword: '', status: null })
const dialogVisible = ref(false)
const form = ref({})
const customerList = ref([])
const supplierList = ref([])
const statusMap = { 1: '未认证', 2: '已认证', 3: '已作废' }

const loadData = async () => {
  const res = await getInvoices({ ...query.value, invoice_type: tabType.value })
  list.value = res.data || []
  total.value = res.total || 0
}

const loadDropdowns = async () => {
  const [c, s] = await Promise.all([
    getCustomers({ page: 1, page_size: 9999 }),
    getSuppliers({ page: 1, page_size: 9999 })
  ])
  customerList.value = c.data || []
  supplierList.value = s.data || []
}

const openDialog = (row) => {
  form.value = row ? { ...row } : { invoice_type: tabType.value, invoice_code: '', invoice_no: '', customer_id: null, supplier_id: null, amount: 0, tax_amount: 0, total_amount: 0, invoice_date: null, remark: '' }
  dialogVisible.value = true
}

const handleSave = async () => {
  form.value.invoice_type = tabType.value
  if (form.value.id) {
    await updateInvoice(form.value.id, form.value)
  } else {
    await createInvoice(form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
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

onMounted(() => { loadData(); loadDropdowns() })
</script>
