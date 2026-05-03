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
        <el-table-column label="模块权限" min-width="200">
          <template #default="{ row }">
            <span v-if="!row.module_permissions || row.module_permissions.length === 0">无</span>
            <el-tag v-for="mp in getModuleNames(row.module_permissions)" :key="mp" style="margin:2px 4px 2px 0">
              {{ mp }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作权限" min-width="150">
          <template #default="{ row }">
            <span v-if="!row.operations || row.operations.length === 0">无</span>
            <el-tag v-for="op in row.operations.slice(0, 3)" :key="op" type="info" style="margin:2px 4px 2px 0">
              {{ op }}
            </el-tag>
            <el-tag v-if="row.operations && row.operations.length > 3" type="info" style="margin:2px 4px 2px 0">
              +{{ row.operations.length - 3 }}
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑角色' : '新增角色'" width="800px" @closed="resetForm">
      <el-form :model="form" label-width="90px">
        <el-form-item label="角色名称" required>
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色标识">
          <el-input v-model="form.role_key" placeholder="如：admin/sales/warehouse" :disabled="!!form.id" />
          <div style="color:#999;font-size:12px">英文标识，系统唯一，如 sales、warehouse</div>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入角色描述" />
        </el-form-item>

        <el-divider content-position="left">模块权限</el-divider>
        <el-form-item label="模块权限">
          <div class="module-permissions">
            <el-table :data="modulePermissionTable" border size="small" style="width:100%">
              <el-table-column label="模块" width="120">
                <template #default="{ row }">
                  {{ row.module_name }}
                </template>
              </el-table-column>
              <el-table-column label="查看" width="60" align="center">
                <template #default="{ row }">
                  <el-checkbox v-model="row.can_view" @change="onModuleCheck(row)" />
                </template>
              </el-table-column>
              <el-table-column label="新增" width="60" align="center">
                <template #default="{ row }">
                  <el-checkbox v-model="row.can_create" :disabled="!row.can_view" />
                </template>
              </el-table-column>
              <el-table-column label="编辑" width="60" align="center">
                <template #default="{ row }">
                  <el-checkbox v-model="row.can_edit" :disabled="!row.can_view" />
                </template>
              </el-table-column>
              <el-table-column label="删除" width="60" align="center">
                <template #default="{ row }">
                  <el-checkbox v-model="row.can_delete" :disabled="!row.can_view" />
                </template>
              </el-table-column>
              <el-table-column label="审核" width="60" align="center">
                <template #default="{ row }">
                  <el-checkbox v-model="row.can_audit" :disabled="!row.can_view" />
                </template>
              </el-table-column>
              <el-table-column label="导出" width="60" align="center">
                <template #default="{ row }">
                  <el-checkbox v-model="row.can_export" :disabled="!row.can_view" />
                </template>
              </el-table-column>
              <el-table-column label="数据范围" min-width="100">
                <template #default="{ row }">
                  <el-select v-model="row.data_scope" size="small" style="width:90px" :disabled="!row.can_view">
                    <el-option value="all" label="全部" />
                    <el-option value="warehouse" label="仓库" />
                    <el-option value="route" label="路线" />
                    <el-option value="self" label="仅自己" />
                  </el-select>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-form-item>

        <el-divider content-position="left">操作权限</el-divider>
        <el-form-item label="操作权限">
          <div class="operation-permissions">
            <el-checkbox-group v-model="selectedOperations">
              <el-row :gutter="10">
                <el-col v-for="op in operationOptions" :key="op.value" :span="8" style="margin-bottom:8px">
                  <el-checkbox :label="op.value">{{ op.label }}</el-checkbox>
                </el-col>
              </el-row>
            </el-checkbox-group>
          </div>
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRoles, createRole, updateRole, deleteRole } from '../../api'

const modulePermissionTable = ref([])
const selectedOperations = ref([])

const moduleOptions = [
  { module_key: 'home', module_name: '首页' },
  { module_key: 'dashboard', module_name: '数据看板' },
  { module_key: 'customers', module_name: '客户管理' },
  { module_key: 'sales', module_name: '销售订单' },
  { module_key: 'inventory', module_name: '库存管理' },
  { module_key: 'purchases', module_name: '采购管理' },
  { module_key: 'suppliers', module_name: '供应商' },
  { module_key: 'finance', module_name: '财务管理' },
  { module_key: 'employees', module_name: '员工管理' },
  { module_key: 'roles', module_name: '角色权限' },
  { module_key: 'products', module_name: '商品管理' },
  { module_key: 'warehouses', module_name: '仓库管理' },
  { module_key: 'batches', module_name: '批次管理' },
  { module_key: 'promotions', module_name: '促销管理' },
  { module_key: 'reports', module_name: '报表统计' },
  { module_key: 'performance', module_name: '业绩查看' },
  { module_key: 'tools', module_name: '工具' },
  { module_key: 'profile', module_name: '我的' },
]

const operationOptions = [
  { value: 'customers:create', label: '新增客户' },
  { value: 'customers:edit', label: '编辑客户' },
  { value: 'customers:delete', label: '删除客户' },
  { value: 'customers:export', label: '导出客户' },
  { value: 'sales:create', label: '创建订单' },
  { value: 'sales:edit', label: '编辑订单' },
  { value: 'sales:delete', label: '删除订单' },
  { value: 'sales:audit', label: '审核订单' },
  { value: 'sales:export', label: '导出订单' },
  { value: 'inventory:view', label: '查看库存' },
  { value: 'inventory:adjust', label: '调整库存' },
  { value: 'inventory:transfer', label: '调拨库存' },
  { value: 'purchases:create', label: '创建采购' },
  { value: 'purchases:edit', label: '编辑采购' },
  { value: 'finance:view', label: '查看财务' },
  { value: 'finance:create', label: '财务收款' },
  { value: 'finance:audit', label: '财务审核' },
  { value: 'reports:view', label: '查看报表' },
  { value: 'warehouse:view', label: '查看仓库' },
  { value: 'warehouse:manage', label: '管理仓库' },
  { value: 'batches:view', label: '查看批次' },
  { value: 'products:export', label: '导出商品' },
  { value: 'performance:view', label: '查看业绩' },
]

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20 })
const dialogVisible = ref(false)
const form = ref({})

const getModuleNames = (modulePermissions) => {
  if (!modulePermissions || modulePermissions.length === 0) return []
  return modulePermissions.filter(mp => mp.can_view).map(mp => {
    const mod = moduleOptions.find(m => m.module_key === mp.module_key)
    return mod ? mod.module_name : mp.module_key
  })
}

const initModuleTable = () => {
  modulePermissionTable.value = moduleOptions.map(m => ({
    module_key: m.module_key,
    module_name: m.module_name,
    can_view: false,
    can_create: false,
    can_edit: false,
    can_delete: false,
    can_audit: false,
    can_export: false,
    data_scope: 'self',
  }))
}

const onModuleCheck = (row) => {
  if (!row.can_view) {
    row.can_create = false
    row.can_edit = false
    row.can_delete = false
    row.can_audit = false
    row.can_export = false
    row.data_scope = 'self'
  }
}

const loadData = async () => {
  const res = await getRoles(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDialog = (row) => {
  initModuleTable()
  selectedOperations.value = []
  if (row) {
    form.value = { ...row }
    // 填充模块权限
    if (row.module_permissions && row.module_permissions.length > 0) {
      row.module_permissions.forEach(mp => {
        const item = modulePermissionTable.value.find(t => t.module_key === mp.module_key)
        if (item) {
          item.can_view = mp.can_view
          item.can_create = mp.can_create
          item.can_edit = mp.can_edit
          item.can_delete = mp.can_delete
          item.can_audit = mp.can_audit
          item.can_export = mp.can_export
          item.data_scope = mp.data_scope || 'self'
        }
      })
    }
    // 填充操作权限
    if (row.operations && row.operations.length > 0) {
      selectedOperations.value = [...row.operations]
    }
  } else {
    form.value = { name: '', description: '', role_key: '' }
  }
  dialogVisible.value = true
}

const resetForm = () => {
  initModuleTable()
  selectedOperations.value = []
}

const handleSave = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入角色名称')
    return
  }

  const module_permissions = modulePermissionTable.value
    .filter(m => m.can_view)
    .map(m => ({
      module_key: m.module_key,
      can_view: m.can_view,
      can_create: m.can_create,
      can_edit: m.can_edit,
      can_delete: m.can_delete,
      can_audit: m.can_audit,
      can_export: m.can_export,
      data_scope: m.data_scope,
    }))

  const payload = {
    name: form.value.name,
    description: form.value.description || '',
    role_key: form.value.role_key || '',
    module_permissions,
    operations: selectedOperations.value,
  }

  if (form.value.id) {
    await updateRole(form.value.id, payload)
  } else {
    await createRole(payload)
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

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.module-permissions :deep(.el-table) {
  font-size: 12px;
}
.operation-permissions :deep(.el-checkbox) {
  margin-right: 0;
  width: 100%;
}
</style>