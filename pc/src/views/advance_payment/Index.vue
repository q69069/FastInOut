<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>预收付款管理</span>
          <el-button type="primary" @click="showDialog()">新建</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="类型">
          <el-select v-model="query.type" clearable placeholder="全部" style="width:120px">
            <el-option label="预收款" value="receivable" />
            <el-option label="预付款" value="payable" />
          </el-select>
        </el-form-item>
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
        <el-table-column label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.type==='receivable'?'success':'warning'" size="small">{{ row.type==='receivable'?'预收':'预付' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="party_name" label="对方" width="120" />
        <el-table-column prop="amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="used_amount" label="已用" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.used_amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="remaining_amount" label="剩余" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.remaining_amount||0).toFixed(2) }}</template>
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

    <el-dialog v-model="dialogVisible" title="新建预收付款" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="类型" required>
          <el-radio-group v-model="form.type">
            <el-radio value="receivable">预收款</el-radio>
            <el-radio value="payable">预付款</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="对方" required>
          <el-select v-model="form.party_id" filterable placeholder="选择客户/供应商" style="width:100%">
            <el-option v-for="p in parties" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额" required>
          <el-input-number v-model="form.amount" :min="0.01" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAdvancePayments, createAdvancePayment, confirmAdvancePayment, getCustomers, getSuppliers } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, type: '', status: '' })
const dialogVisible = ref(false)
const saving = ref(false)
const customers = ref([])
const suppliers = ref([])
const form = ref({ type: 'receivable', party_id: null, amount: 0, remark: '' })

const parties = computed(() => form.value.type === 'receivable' ? customers.value : suppliers.value)

const loadData = async () => {
  const res = await getAdvancePayments(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadParties = async () => {
  const [c, s] = await Promise.all([getCustomers(), getSuppliers()])
  customers.value = c.data || []
  suppliers.value = s.data || []
}

const showDialog = () => {
  form.value = { type: 'receivable', party_id: null, amount: 0, remark: '' }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.party_id) return ElMessage.warning('请选择对方')
  if (!form.value.amount) return ElMessage.warning('请输入金额')
  saving.value = true
  try {
    await createAdvancePayment({ ...form.value, party_type: form.value.type === 'receivable' ? 'customer' : 'supplier' })
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadData()
  } finally { saving.value = false }
}

const handleConfirm = async (row) => {
  await confirmAdvancePayment(row.id)
  ElMessage.success('确认成功')
  loadData()
}

onMounted(() => { loadData(); loadParties() })
</script>
