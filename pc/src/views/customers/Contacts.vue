<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>客户联系人</span>
          <el-button type="primary" @click="showDialog()">新增联系人</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="客户">
          <el-select v-model="query.customer_id" placeholder="全部客户" clearable filterable style="width:200px">
            <el-option v-for="c in customerList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="姓名/电话" clearable style="width:160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="position" label="职位" width="100" />
        <el-table-column prop="wechat" label="微信" width="120" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column label="主要联系人" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_primary ? 'success' : 'info'" size="small">{{ row.is_primary ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="showDialog(row)">编辑</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑联系人' : '新增联系人'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="客户" required>
          <el-select v-model="form.customer_id" placeholder="请选择客户" filterable style="width:100%">
            <el-option v-for="c in customerList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="form.position" />
        </el-form-item>
        <el-form-item label="微信">
          <el-input v-model="form.wechat" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="主要联系人">
          <el-switch v-model="form.is_primary" :active-value="1" :inactive-value="0" />
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
import { getContacts, createContact, updateContact, deleteContact, getCustomers } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, customer_id: null, keyword: '' })
const dialogVisible = ref(false)
const form = ref({})
const customerList = ref([])

const loadCustomers = async () => {
  const res = await getCustomers({ page: 1, page_size: 100 })
  customerList.value = res.data || []
}

const loadData = async () => {
  const params = { page: query.value.page, page_size: query.value.page_size }
  if (query.value.customer_id) params.customer_id = query.value.customer_id
  if (query.value.keyword) params.keyword = query.value.keyword
  const res = await getContacts(params)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDialog = (row) => {
  form.value = row
    ? { ...row }
    : { customer_id: null, name: '', phone: '', position: '', wechat: '', email: '', is_primary: 0, remark: '' }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.customer_id) return ElMessage.warning('请选择客户')
  if (!form.value.name) return ElMessage.warning('请输入姓名')
  if (form.value.id) {
    await updateContact(form.value.id, form.value)
  } else {
    await createContact(form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该联系人？', '提示', { type: 'warning' })
  await deleteContact(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => {
  loadCustomers()
  loadData()
})
</script>
