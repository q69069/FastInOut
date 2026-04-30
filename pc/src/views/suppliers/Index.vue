<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>供应商管理</span>
          <el-button type="primary" @click="showDialog()">新增供应商</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="搜索供应商名称" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="contact" label="联系人" width="100" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="payable_balance" label="应付余额" width="120" />
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
    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑供应商' : '新增供应商'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="编码" required>
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" />
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
import { getSuppliers, createSupplier, updateSupplier, deleteSupplier } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, keyword: '' })
const dialogVisible = ref(false)
const form = ref({})

const loadData = async () => {
  const res = await getSuppliers(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDialog = (row) => {
  form.value = row ? { ...row } : { code: '', name: '', contact: '', phone: '', address: '' }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (form.value.id) {
    await updateSupplier(form.value.id, form.value)
  } else {
    await createSupplier(form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该供应商？', '提示', { type: 'warning' })
  await deleteSupplier(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
