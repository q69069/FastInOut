<template>
  <div class="employee-page">
    <van-nav-bar title="员工管理" />

    <!-- 筛选 -->
    <div class="filter-bar">
      <van-tag :type="filterRole === 'all' ? 'primary' : 'default'" size="large" @click="filterRole = 'all'">全部</van-tag>
      <van-tag :type="filterRole === '销售' ? 'primary' : 'default'" size="large" @click="filterRole = '销售'">销售</van-tag>
      <van-tag :type="filterRole === '财务' ? 'primary' : 'default'" size="large" @click="filterRole = '财务'">财务</van-tag>
      <van-tag :type="filterRole === '库管' ? 'primary' : 'default'" size="large" @click="filterRole = '库管'">库管</van-tag>
      <van-tag :type="filterRole === '老板' ? 'primary' : 'default'" size="large" @click="filterRole = '老板'">老板</van-tag>
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
          </div>
          <div class="card-actions">
            <van-button size="small" @click="handleEdit(item)">编辑</van-button>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 编辑弹窗 -->
    <van-popup v-model:show="showEditPopup" position="bottom" round>
      <div class="edit-popup">
        <div class="popup-title">{{ isAddNew ? '新增员工' : '编辑员工' }}</div>
        <van-cell-group inset>
          <van-field v-model="editForm.name" label="姓名" placeholder="请输入姓名" />
          <van-field v-model="editForm.phone" label="电话" placeholder="请输入电话" type="tel" />
          <van-field v-model="editForm.role" label="角色" placeholder="销售/财务/库管/老板" />
          <van-field v-model="editForm.remark" label="备注" placeholder="备注信息" />
        </van-cell-group>
        <div class="popup-actions">
          <van-button @click="showEditPopup = false">取消</van-button>
          <van-button type="primary" @click="handleSave">保存</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast } from 'vant'
import { getEmployees, createEmployee, updateEmployee } from '../api'

const loading = ref(false)
const finished = ref(false)
const filterRole = ref('all')
const showEditPopup = ref(false)
const isAddNew = ref(false)
const currentEmp = ref(null)

const list = ref([])
const editForm = ref({ name: '', phone: '', role: '', remark: '' })

const filteredList = computed(() => {
  if (filterRole.value === 'all') return list.value
  return list.value.filter(i => i.role === filterRole.value)
})

const getRoleType = (role) => {
  if (role === '老板') return 'danger'
  if (role === '销售') return 'primary'
  if (role === '财务') return 'warning'
  if (role === '库管') return 'success'
  return 'default'
}

const handleEdit = (item) => {
  currentEmp.value = item
  editForm.value = { name: item.name, phone: item.phone, role: item.role, remark: item.remark }
  isAddNew.value = false
  showEditPopup.value = true
}

const handleSave = async () => {
  if (!editForm.value.name) {
    showToast('请输入姓名')
    return
  }
  try {
    if (isAddNew.value) {
      await createEmployee(editForm.value)
      showToast('添加成功')
    } else {
      await updateEmployee({ id: currentEmp.value.id, ...editForm.value })
      showToast('更新成功')
    }
    showEditPopup.value = false
    loadData()
  } catch (e) {
    showToast('操作失败')
  }
}

const loadData = async () => {
  try {
    const res = await getEmployees()
    list.value = res.data || []
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
    finished.value = true
  }
}

onMounted(loadData)
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
.status-dot { width: 6px; height: 6px; border-radius: 50%; }
.status-dot.active { background: #07c160; }
.status-dot.inactive { background: #999; }
.card-actions { display: flex; align-items: center; }
.edit-popup { padding: 20px; }
.popup-title { font-size: 16px; font-weight: bold; text-align: center; margin-bottom: 16px; }
.popup-actions { display: flex; gap: 12px; margin-top: 16px; }
.popup-actions button { flex: 1; }
</style>