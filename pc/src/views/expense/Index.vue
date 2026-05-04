<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>费用管理</span>
              <el-button type="primary" @click="showDialog()">新增费用</el-button>
            </div>
          </template>
          <el-form inline style="margin-bottom:16px">
            <el-form-item label="状态">
              <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
                <el-option label="待审批" value="pending" />
                <el-option label="已通过" value="approved" />
                <el-option label="已驳回" value="rejected" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadData">查询</el-button>
            </el-form-item>
          </el-form>
          <el-table :data="list" border stripe>
            <el-table-column prop="expense_no" label="单号" width="150" />
            <el-table-column prop="category_name" label="类别" width="100" />
            <el-table-column prop="amount" label="金额" width="100" align="right">
              <template #default="{ row }">¥{{ Number(row.amount||0).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="payee" label="收款人" width="100" />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status==='approved'?'success':row.status==='rejected'?'danger':'info'">
                  {{ row.status==='approved'?'已通过':row.status==='rejected'?'已驳回':'待审批' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="showDetail(row)">详情</el-button>
                <el-button link type="success" v-if="row.status==='pending'" @click="handleApprove(row)">通过</el-button>
                <el-button link type="danger" v-if="row.status==='pending'" @click="handleReject(row)">驳回</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>费用类别</template>
          <div style="margin-bottom:12px">
            <el-input v-model="newCategory" placeholder="新类别名称" style="width:70%;margin-right:8px" />
            <el-button type="primary" @click="addCategory">添加</el-button>
          </div>
          <el-table :data="categories" border size="small">
            <el-table-column prop="name" label="类别名称" />
            <el-table-column label="操作" width="60">
              <template #default="{ row }">
                <el-button link type="danger" @click="deleteCategory(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新增费用弹窗 -->
    <el-dialog v-model="dialogVisible" title="新增费用" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="费用类别" required>
          <el-select v-model="form.category_id" placeholder="选择类别" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额" required>
          <el-input-number v-model="form.amount" :min="0.01" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="收款人">
          <el-input v-model="form.payee" placeholder="收款人姓名" />
        </el-form-item>
        <el-form-item label="是否员工">
          <el-switch v-model="form.payee_is_employee" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="费用说明" />
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

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="费用详情" width="500px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="单号">{{ detail.expense_no }}</el-descriptions-item>
        <el-descriptions-item label="类别">{{ detail.category_name }}</el-descriptions-item>
        <el-descriptions-item label="金额">¥{{ Number(detail.amount||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="收款人">{{ detail.payee || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="detail.status==='approved'?'success':detail.status==='rejected'?'danger':'info'">
            {{ detail.status==='approved'?'已通过':detail.status==='rejected'?'已驳回':'待审批' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="说明">{{ detail.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExpenses, createExpense, getExpense, approveExpense, rejectExpense, getExpenseCategories, createExpenseCategory, deleteExpenseCategory } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, status: '' })
const dialogVisible = ref(false)
const detailVisible = ref(false)
const saving = ref(false)
const detail = ref({})
const categories = ref([])
const newCategory = ref('')

const form = ref({ category_id: null, amount: 0, payee: '', payee_is_employee: false, description: '', remark: '' })

const loadData = async () => {
  const res = await getExpenses(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadCategories = async () => {
  const res = await getExpenseCategories()
  categories.value = res.data || []
}

const showDialog = () => {
  form.value = { category_id: null, amount: 0, payee: '', payee_is_employee: false, description: '', remark: '' }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.category_id) return ElMessage.warning('请选择费用类别')
  if (!form.value.amount) return ElMessage.warning('请输入金额')
  saving.value = true
  try {
    await createExpense(form.value)
    ElMessage.success('费用已创建')
    dialogVisible.value = false
    loadData()
  } finally {
    saving.value = false
  }
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

onMounted(() => { loadData(); loadCategories() })
</script>
