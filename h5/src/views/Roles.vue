<template>
  <div class="roles-page">
    <van-nav-bar title="角色权限" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startCreate" />
      </template>
    </van-nav-bar>

    <!-- 角色列表 -->
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <div v-for="role in roles" :key="role.id" class="role-card">
        <div class="role-header">
          <div class="role-name">{{ role.name }}</div>
          <van-tag :type="role.status === 1 ? 'success' : 'default'" size="small">
            {{ role.status === 1 ? '启用' : '停用' }}
          </van-tag>
        </div>
        <div class="role-desc">{{ role.description || '暂无描述' }}</div>
        <div class="role-permissions">
          <van-tag v-for="perm in (role.permissions || [])" :key="perm" size="small" plain>{{ perm }}</van-tag>
        </div>
        <div class="role-actions">
          <van-button size="small" @click="handleEdit(role)">编辑</van-button>
          <van-button v-if="authStore.isAdmin" size="small" type="danger" plain @click="handleDelete(role)">删除</van-button>
        </div>
      </div>
      <van-empty v-if="roles.length === 0 && !loading" description="暂无角色" />
    </van-pull-refresh>

    <!-- 编辑/新建弹窗 -->
    <van-popup v-model:show="showEditPopup" position="bottom" round style="max-height:85%">
      <div class="edit-popup">
        <div class="popup-title">{{ isCreate ? '新建角色' : '编辑角色' }}</div>
        <van-cell-group inset>
          <van-field v-model="editForm.name" label="角色名称" placeholder="请输入角色名称" />
          <van-field v-model="editForm.description" label="描述" placeholder="角色描述" />
          <van-cell title="状态">
            <template #extra>
              <van-radio-group v-model="editForm.status" direction="horizontal">
                <van-radio :name="1">启用</van-radio>
                <van-radio :name="0">停用</van-radio>
              </van-radio-group>
            </template>
          </van-cell>
        </van-cell-group>
        <div class="permission-section">
          <div class="section-label">权限分配</div>
          <van-checkbox-group v-model="editForm.permissions">
            <div class="perm-grid">
              <van-checkbox v-for="perm in allPermissions" :key="perm" :name="perm" shape="square">{{ perm }}</van-checkbox>
            </div>
          </van-checkbox-group>
        </div>
        <div class="popup-actions">
          <van-button @click="showEditPopup = false">取消</van-button>
          <van-button type="primary" :loading="submitting" @click="handleSave">保存</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getRoles, createRole, updateRole, deleteRole } from '../api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const roles = ref([])
const loading = ref(false)
const showEditPopup = ref(false)
const isCreate = ref(false)
const submitting = ref(false)
const currentRole = ref(null)

const editForm = ref({ name: '', description: '', status: 1, permissions: [] })

const allPermissions = [
  '客户管理', '销售开单', '业绩统计', '库存查询',
  '拜访记录', '应收应付', '仓库管理', '采购管理',
  '供应商管理', '打印小票', '审核中心', '员工管理',
  '数据看板', '系统设置', '报表查看'
]

const handleEdit = (role) => {
  currentRole.value = role
  isCreate.value = false
  editForm.value = {
    name: role.name,
    description: role.description || '',
    status: role.status || 1,
    permissions: role.permissions ? [...role.permissions] : []
  }
  showEditPopup.value = true
}

const startCreate = () => {
  isCreate.value = true
  currentRole.value = null
  editForm.value = { name: '', description: '', status: 1, permissions: [] }
  showEditPopup.value = true
}

const handleSave = async () => {
  if (!editForm.value.name) {
    showToast('请输入角色名称')
    return
  }
  submitting.value = true
  try {
    const payload = { ...editForm.value }
    if (isCreate.value) {
      await createRole(payload)
      showSuccessToast('创建成功')
    } else {
      await updateRole({ id: currentRole.value.id, ...payload })
      showSuccessToast('保存成功')
    }
    showEditPopup.value = false
    loadData()
  } catch (e) {
    showToast('保存失败')
  }
  submitting.value = false
}

const handleDelete = async (role) => {
  try {
    await showConfirmDialog({ title: '删除角色', message: `确认删除角色 ${role.name}？` })
    await deleteRole(role.id)
    showSuccessToast('已删除')
    loadData()
  } catch {}
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getRoles()
    roles.value = res.data || [
      { id: 1, name: '老板', description: '拥有所有权限', status: 1, permissions: allPermissions },
      { id: 2, name: '销售', description: '销售相关功能', status: 1, permissions: ['客户管理', '销售开单', '业绩统计', '拜访记录', '打印小票'] },
      { id: 3, name: '财务', description: '财务相关功能', status: 1, permissions: ['应收应付', '业绩统计', '数据看板'] },
      { id: 4, name: '库管', description: '仓库相关功能', status: 1, permissions: ['库存查询', '仓库管理', '打印小票'] }
    ]
  } catch {
    roles.value = [
      { id: 1, name: '老板', description: '拥有所有权限', status: 1, permissions: allPermissions }
    ]
  }
  loading.value = false
}

onMounted(loadData)
</script>

<style scoped>
.roles-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.role-card { background: #fff; margin: 12px; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.role-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.role-name { font-size: 16px; font-weight: bold; color: #333; }
.role-desc { font-size: 13px; color: #999; margin-bottom: 12px; }
.role-permissions { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.role-actions { display: flex; gap: 8px; }
.edit-popup { padding: 20px; }
.popup-title { font-size: 16px; font-weight: bold; text-align: center; margin-bottom: 16px; }
.permission-section { margin-top: 16px; padding: 0 16px; }
.section-label { font-size: 14px; color: #666; margin-bottom: 8px; }
.perm-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.popup-actions { display: flex; gap: 12px; margin-top: 16px; }
.popup-actions button { flex: 1; }
</style>