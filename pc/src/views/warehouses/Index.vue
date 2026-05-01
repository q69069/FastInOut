<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>仓库管理</span>
          <el-button type="primary" @click="showDialog()">新增仓库</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="搜索仓库名称/编码" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="query.warehouse_type" clearable placeholder="仓库类型" style="width:120px" @change="loadData">
            <el-option label="普通仓库" value="normal" />
            <el-option label="车仓" value="vehicle" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="编码" width="100" />
        <el-table-column prop="name" label="仓库名称" min-width="200" />
        <el-table-column prop="warehouse_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.warehouse_type === 'vehicle' ? 'warning' : row.warehouse_type === 'other' ? 'info' : ''">
              {{ warehouseTypeMap[row.warehouse_type] || '普通仓库' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="manager" label="负责人" width="100" />
        <el-table-column prop="phone" label="电话" width="120" />
        <el-table-column prop="is_default" label="默认" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success">是</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="showDialog(row)">编辑</el-button>
            <el-button v-if="!row.is_default" size="small" type="success" @click="handleSetDefault(row)">设为默认</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑仓库' : '新增仓库'" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" placeholder="如：WH001" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="仓库全名" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.warehouse_type" style="width:100%">
            <el-option label="普通仓库" value="normal" />
            <el-option label="车仓" value="vehicle" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="form.manager" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="默认仓库">
          <el-switch v-model="form.is_default" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
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
import { getWarehouses, createWarehouse, updateWarehouse, deleteWarehouse, setWarehouseDefault } from '../../api'

const warehouseTypeMap = {
  normal: '普通仓库',
  vehicle: '车仓',
  other: '其他'
}

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, keyword: '', warehouse_type: '' })
const dialogVisible = ref(false)
const form = ref({})
const formRef = ref(null)

const rules = {
  code: [{ required: true, message: '请输入仓库编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入仓库名称', trigger: 'blur' }]
}

const loadData = async () => {
  const params = { ...query.value }
  if (!params.warehouse_type) delete params.warehouse_type
  const res = await getWarehouses(params)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDialog = (row) => {
  form.value = row ? { ...row } : {
    code: '', name: '', warehouse_type: 'normal', address: '', manager: '', phone: '', description: '', is_default: false, status: 1
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  if (form.value.id) {
    await updateWarehouse(form.value.id, form.value)
  } else {
    await createWarehouse(form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

const handleSetDefault = async (row) => {
  await setWarehouseDefault(row.id)
  ElMessage.success('已设为默认仓库')
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该仓库？', '提示', { type: 'warning' })
  await deleteWarehouse(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
