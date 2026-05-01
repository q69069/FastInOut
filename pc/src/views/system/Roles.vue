<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>角色管理</span>
          <el-button type="primary" @click="showDialog()">新增角色</el-button>
        </div>
      </template>
      <el-table :data="list" border stripe>
        <el-table-column prop="name" label="角色名称" width="160" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="权限" min-width="300">
          <template #default="{ row }">
            <el-tag v-for="p in row.permissions" :key="p" style="margin:2px 4px 2px 0">
              {{ permissionLabel(p) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑角色' : '新增角色'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="角色名称" required>
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入角色描述" />
        </el-form-item>
        <el-form-item label="权限">
          <el-checkbox-group v-model="form.permissions">
            <el-checkbox v-for="item in permissionOptions" :key="item.value" :label="item.value">
              {{ item.label }}
            </el-checkbox>
          </el-checkbox-group>
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
import { getRoles, createRole, updateRole, deleteRole } from '../../api'

const permissionOptions = [
  { value: '*', label: '全部权限' },
  { value: 'sales', label: '销售管理' },
  { value: 'customers', label: '客户管理' },
  { value: 'customers_view', label: '客户查看' },
  { value: 'suppliers', label: '供应商管理' },
  { value: 'suppliers_view', label: '供应商查看' },
  { value: 'products', label: '商品管理' },
  { value: 'products_view', label: '商品查看' },
  { value: 'inventory', label: '库存管理' },
  { value: 'warehouses', label: '仓库管理' },
  { value: 'purchases', label: '采购管理' },
  { value: 'transfers', label: '调拨管理' },
  { value: 'finance', label: '财务管理' },
  { value: 'reports', label: '报表查看' }
]

const permissionMap = Object.fromEntries(permissionOptions.map(o => [o.value, o.label]))

const permissionLabel = (val) => permissionMap[val] || val

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20 })
const dialogVisible = ref(false)
const form = ref({})

const loadData = async () => {
  const res = await getRoles(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDialog = (row) => {
  form.value = row
    ? { ...row, permissions: row.permissions ? [...row.permissions] : [] }
    : { name: '', description: '', permissions: [] }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入角色名称')
    return
  }
  if (form.value.id) {
    await updateRole(form.value.id, form.value)
  } else {
    await createRole(form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该角色？', '提示', { type: 'warning' })
  await deleteRole(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
