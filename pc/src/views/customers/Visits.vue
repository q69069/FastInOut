<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>拜访记录</span>
          <el-button type="primary" @click="showDialog()">新增拜访</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="客户">
          <el-select v-model="query.customer_id" placeholder="全部客户" clearable filterable style="width:200px">
            <el-option v-for="c in customerList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="customer_name" label="客户" width="120" />
        <el-table-column prop="visit_date" label="拜访日期" width="170" />
        <el-table-column prop="content" label="拜访内容" show-overflow-tooltip />
        <el-table-column prop="result" label="拜访结果" show-overflow-tooltip />
        <el-table-column prop="next_plan" label="下次计划" show-overflow-tooltip />
        <el-table-column prop="operator" label="拜访人" width="80" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
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
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增拜访记录" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="客户" required>
          <el-select v-model="form.customer_id" placeholder="请选择客户" filterable style="width:100%">
            <el-option v-for="c in customerList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="拜访日期" required>
          <el-date-picker v-model="form.visit_date" type="datetime" style="width:100%" />
        </el-form-item>
        <el-form-item label="拜访内容">
          <el-input v-model="form.content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="拜访结果">
          <el-input v-model="form.result" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="下次计划">
          <el-input v-model="form.next_plan" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="拜访人">
          <el-input v-model="form.operator" />
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
import { getVisits, createVisit, deleteVisit, getCustomers } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, customer_id: null })
const dialogVisible = ref(false)
const form = ref({})
const customerList = ref([])
const customerMap = ref({})

const loadCustomers = async () => {
  const res = await getCustomers({ page: 1, page_size: 100 })
  customerList.value = res.data || []
  customerMap.value = Object.fromEntries(res.data.map(c => [c.id, c.name]))
}

const loadData = async () => {
  const params = { page: query.value.page, page_size: query.value.page_size }
  if (query.value.customer_id) params.customer_id = query.value.customer_id
  const res = await getVisits(params)
  list.value = (res.data || []).map(v => ({
    ...v,
    customer_name: customerMap.value[v.customer_id] || v.customer_id
  }))
  total.value = res.total || 0
}

const showDialog = () => {
  form.value = { customer_id: null, visit_date: new Date(), content: '', result: '', next_plan: '', operator: '' }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.customer_id) return ElMessage.warning('请选择客户')
  if (!form.value.visit_date) return ElMessage.warning('请选择拜访日期')
  await createVisit(form.value)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该拜访记录？', '提示', { type: 'warning' })
  await deleteVisit(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => {
  loadCustomers()
  loadData()
})
</script>
