<template>
  <div class="employee-page">
    <van-nav-bar title="员工管理" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startAdd" v-if="authStore.can('employees', 'create')" />
      </template>
    </van-nav-bar>

    <!-- 筛选 -->
    <div class="filter-bar">
      <van-tag :type="filterRole === 'all' ? 'primary' : 'default'" size="large" @click="filterRole = 'all'">全部</van-tag>
      <van-tag v-for="r in roleOptions" :key="r" :type="filterRole === r ? 'primary' : 'default'" size="large" @click="filterRole = r">{{ r }}</van-tag>
    </div>

    <!-- 员工列表 -->
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadData">
        <div v-for="item in filteredList" :key="item.id" class="employee-card">
          <div class="card-left">
            <div class="avatar">{{ item.name?.charAt(0) || 'U' }}</div>
          </div>
          <div class="card-body">
            <div class="emp-name">{{ item.name }}</div>
            <div class="emp-info">
              <van-tag :type="getRoleType(item.role)" size="small">{{ item.role || '员工' }}</van-tag>
              <span class="emp-phone">{{ item.phone || '无电话' }}</span>
            </div>
            <div class="emp-status">
              <span :class="['status-dot', item.status === 1 ? 'active' : 'inactive']"></span>
              {{ item.status === 1 ? '在职' : '离职' }}
            </div>
            <div v-if="item.warehouse_name" class="emp-warehouse">仓库: {{ item.warehouse_name }}</div>
          </div>
          <div class="card-actions">
            <van-button v-if="authStore.can('employees', 'edit')" size="small" @click="handleEdit(item)">编辑</van-button>
            <van-button v-if="authStore.isAdmin" size="small" :type="item.status === 1 ? 'default' : 'success'" @click="toggleStatus(item)">{{ item.status === 1 ? '离职' : '在职' }}</van-button>
            <van-button v-if="authStore.isAdmin" size="small" type="danger" plain @click="handleDelete(item)">删除</van-button>
          </div>
        </div>
        <van-empty v-if="filteredList.length === 0 && !loading" description="暂无员工" />
      </van-list>
    </van-pull-refresh>

    <!-- 编辑弹窗 -->
    <van-popup v-model:show="showEditPopup" position="bottom" round>
      <div class="edit-popup">
        <div class="popup-title">{{ isAddNew ? '新增员工' : '编辑员工' }}</div>
        <van-cell-group inset>
          <van-field v-model="editForm.name" label="姓名" placeholder="请输入姓名" />
          <van-field v-model="editForm.phone" label="电话" placeholder="请输入电话" type="tel" />
          <van-cell title="角色" is-link :value="editForm.role || '请选择'" @click="showRolePicker = true" />
          <van-cell title="仓库" is-link :value="editForm.warehouse_name || '请选择'" @click="showWhPicker = true" />
          <van-field v-model="editForm.username" label="用户名" placeholder="登录用户名" />
          <van-field v-if="isAddNew" v-model="editForm.password" label="密码" type="password" placeholder="请输入密码" />
          <van-field v-model="editForm.remark" label="备注" placeholder="备注信息" />
        </van-cell-group>
        <div class="popup-actions">
          <van-button @click="showEditPopup = false">取消</van-button>
          <van-button type="primary" :loading="submitting" @click="handleSave">保存</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 角色选择 -->
    <van-popup v-model:show="showRolePicker" position="bottom" round>
      <van-picker title="选择角色" :columns="roleColumns" @confirm="onRoleConfirm" @cancel="showRolePicker = false" />
    </van-popup>

    <!-- 仓库选择 -->
    <van-popup v-model:show="showWhPicker" position="bottom" round>
      <van-picker title="选择仓库" :columns="whColumns" @confirm="onWhConfirm" @cancel="showWhPicker = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getEmployees, createEmployee, updateEmployee, deleteEmployee, getWarehouses, getRoles } from '../api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const finished = ref(false)
const filterRole = ref('all')
const showEditPopup = ref(false)
const showRolePicker = ref(false)
const showWhPicker = ref(false)
const isAddNew = ref(false)
const submitting = ref(false)
const currentEmp = ref(null)

const list = ref([])
const warehouses = ref([])
const roles = ref([])
const roleOptions = ['老板', '销售', '财务', '库管', '文员']

const editForm = ref({ name: '', phone: '', role: '', warehouse_id: null, warehouse_name: '', username: '', password: '', remark: '' })

const filteredList = computed(() => {
  if (filterRole.value === 'all') return list.value
  return list.value.filter(i => i.role === filterRole.value)
})

const roleColumns = computed(() => roleOptions.map(r => ({ text: r, value: r })))
const whColumns = computed(() => [
  { text: '无', value: null },
  ...warehouses.value.map(w => ({ text: w.name, value: w.id }))
])

const getRoleType = (role) => {
  if (role === '老板') return 'danger'
  if (role === '销售') return 'primary'
  if (role === '财务') return 'warning'
  if (role === '库管') return 'success'
  return 'default'
}

const startAdd = () => {
  isAddNew.value = true
  editForm.value = { name: '', phone: '', role: '', warehouse_id: null, warehouse_name: '', username: '', password: '', remark: '' }
  showEditPopup.value = true
}

const handleEdit = (item) => {
  currentEmp.value = item
  isAddNew.value = false
  editForm.value = {
    name: item.name, phone: item.phone, role: item.role,
    warehouse_id: item.warehouse_id, warehouse_name: item.warehouse_name || '',
    username: item.username || '', password: '', remark: item.remark || ''
  }
  showEditPopup.value = true
}

const onRoleConfirm = ({ selectedOptions }) => {
  editForm.value.role = selectedOptions[0].value
  showRolePicker.value = false
}

const onWhConfirm = ({ selectedOptions }) => {
  editForm.value.warehouse_id = selectedOptions[0].value
  editForm.value.warehouse_name = selectedOptions[0].text === '无' ? '' : selectedOptions[0].text
  showWhPicker.value = false
}

const handleSave = async () => {
  if (!editForm.value.name) return showToast('请输入姓名')
  submitting.value = true
  try {
    const payload = { ...editForm.value }
    if (!isAddNew.value) delete payload.password
    if (isAddNew.value) {
      await createEmployee(payload)
      showSuccessToast('添加成功')
    } else {
      await updateEmployee({ id: currentEmp.value.id, ...payload })
      showSuccessToast('更新成功')
    }
    showEditPopup.value = false
    loadData()
  } catch { showToast('操作失败') }
  submitting.value = false
}

const toggleStatus = async (item) => {
  const newStatus = item.status === 1 ? 0 : 1
  try {
    await showConfirmDialog({ title: '切换状态', message: `确认将 ${item.name} 设为 ${newStatus === 1 ? '在职' : '离职'}？` })
    await updateEmployee({ id: item.id, status: newStatus })
    showSuccessToast('已更新')
    loadData()
  } catch {}
}

const handleDelete = async (item) => {
  try {
    await showConfirmDialog({ title: '删除员工', message: `确认删除员工 ${item.name}？此操作不可恢复。` })
    await deleteEmployee(item.id)
    showSuccessToast('已删除')
    loadData()
  } catch {}
}

const loadData = async () => {
  try {
    const res = await getEmployees()
    list.value = res.data || []
  } catch {
    list.value = []
  } finally {
    loading.value = false
    finished.value = true
  }
}

onMounted(async () => {
  loadData()
  try {
    const [whRes, roleRes] = await Promise.all([getWarehouses(), getRoles()])
    warehouses.value = whRes.data || []
    const serverRoles = (roleRes.data || []).map(r => r.name).filter(Boolean)
    if (serverRoles.length > 0) roleOptions.splice(0, roleOptions.length, ...serverRoles)
  } catch {}
})
</script>

<style scoped>
.employee-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.filter-bar { display: flex; gap: 8px; padding: 12px; background: #fff; margin-bottom: 12px; }
.employee-card { display: flex; background: #fff; margin: 0 12px 12px; border-radius: 12px; padding: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card-left { margin-right: 12px; }
.avatar { width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #1989fa, #396bec); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; }
.card-body { flex: 1; }
.emp-name { font-size: 15px; font-weight: bold; color: #333; margin-bottom: 6px; }
.emp-info { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.emp-phone { font-size: 12px; color: #999; }
.emp-status { display: flex; align-items: center; gap: 4px; font-size: 12px; color: #666; }
.emp-warehouse { font-size: 11px; color: #999; margin-top: 2px; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; }
.status-dot.active { background: #07c160; }
.status-dot.inactive { background: #999; }
.card-actions { display: flex; flex-direction: column; gap: 4px; align-items: flex-end; justify-content: center; }
.edit-popup { padding: 20px; }
.popup-title { font-size: 16px; font-weight: bold; text-align: center; margin-bottom: 16px; }
.popup-actions { display: flex; gap: 12px; margin-top: 16px; }
.popup-actions button { flex: 1; }
</style>