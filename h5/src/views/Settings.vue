<template>
  <div class="page">
    <van-nav-bar title="系统设置" left-arrow @click-left="$router.back()" />

    <!-- 个人信息 -->
    <van-cell-group inset title="个人信息">
      <van-cell title="用户名" :value="userInfo.username || '-'" />
      <van-cell title="姓名" :value="userInfo.name || '-'" />
      <van-cell title="角色" :value="userInfo.role_name || '-'" />
    </van-cell-group>

    <!-- 公司信息 -->
    <van-cell-group inset title="公司信息">
      <van-cell title="公司名称" :value="company.name || '未设置'" is-link @click="editField = 'name'; editValue = company.name; showEditPopup = true" />
      <van-cell title="联系电话" :value="company.phone || '未设置'" is-link @click="editField = 'phone'; editValue = company.phone; showEditPopup = true" />
      <van-cell title="公司地址" :value="company.address || '未设置'" is-link @click="editField = 'address'; editValue = company.address; showEditPopup = true" />
    </van-cell-group>

    <!-- 业务设置 -->
    <van-cell-group inset title="业务设置">
      <van-cell title="默认仓库" is-link :value="settings.defaultWarehouseName || '未设置'" @click="showWhPicker = true" />
      <van-cell title="价格精度" :value="settings.priceDecimal + ' 位小数'" />
      <van-cell title="打印模板" is-link value="80mm" @click="showToast('打印模板配置')" />
    </van-cell-group>

    <!-- 权限设置 -->
    <van-cell-group inset title="系统管理" v-if="authStore.isAdmin">
      <van-cell title="角色管理" is-link @click="$router.push('/roles')">
        <template #icon><van-icon name="setting-o" style="margin-right:8px" /></template>
      </van-cell>
      <van-cell title="员工管理" is-link @click="$router.push('/employee')">
        <template #icon><van-icon name="friends-o" style="margin-right:8px" /></template>
      </van-cell>
      <van-cell title="操作日志" is-link @click="showLogs">
        <template #icon><van-icon name="records" style="margin-right:8px" /></template>
      </van-cell>
    </van-cell-group>

    <!-- 数据管理 -->
    <van-cell-group inset title="数据管理">
      <van-cell title="数据备份" is-link @click="handleBackup">
        <template #icon><van-icon name="upgrade" style="margin-right:8px" /></template>
      </van-cell>
      <van-cell title="清理缓存" is-link @click="handleClearCache">
        <template #icon><van-icon name="clear" style="margin-right:8px" /></template>
      </van-cell>
    </van-cell-group>

    <!-- 退出登录 -->
    <div style="padding:16px">
      <van-button type="danger" block @click="handleLogout">退出登录</van-button>
    </div>

    <!-- 系统信息 -->
    <div class="system-info">
      <div>FastInOut 进销存管理系统</div>
      <div style="color:#999;font-size:12px;margin-top:4px">v3.0.0 | 2026</div>
    </div>

    <!-- 编辑弹窗 -->
    <van-popup v-model:show="showEditPopup" position="bottom" round>
      <div style="padding:20px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">编辑{{ getFieldLabel(editField) }}</div>
        <van-cell-group inset>
          <van-field v-model="editValue" :placeholder="'请输入' + getFieldLabel(editField)" />
        </van-cell-group>
        <div style="display:flex;gap:12px;margin-top:16px">
          <van-button block @click="showEditPopup = false">取消</van-button>
          <van-button type="primary" block :loading="submitting" @click="saveField">保存</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 操作日志弹窗 -->
    <van-popup v-model:show="showLogPopup" position="bottom" round style="max-height:80%">
      <div style="padding:16px">
        <div style="font-weight:bold;text-align:center;margin-bottom:12px">操作日志</div>
        <van-list :finished="logFinished" finished-text="没有更多了" @load="loadLogs">
          <div v-for="log in logs" :key="log.id" style="padding:8px 0;border-bottom:1px solid #f5f5f5">
            <div style="font-size:13px;color:#333">{{ log.action }}</div>
            <div style="font-size:12px;color:#999;margin-top:2px">{{ log.created_at?.substring(0, 16) }}</div>
          </div>
        </van-list>
      </div>
    </van-popup>

    <!-- 仓库选择 -->
    <van-popup v-model:show="showWhPicker" position="bottom" round>
      <van-picker title="选择默认仓库" :columns="whColumns" @confirm="onWhConfirm" @cancel="showWhPicker = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getCompanySettings, updateCompanySettings, backupData, getWarehouses, getOperationLogs } from '../api'

const router = useRouter()
const authStore = useAuthStore()
const submitting = ref(false)
const showEditPopup = ref(false)
const showLogPopup = ref(false)
const showWhPicker = ref(false)
const editField = ref('')
const editValue = ref('')

const userInfo = ref({})
const company = ref({})
const settings = ref({ defaultWarehouseName: '', priceDecimal: 2 })
const warehouses = ref([])
const logs = ref([])
const logFinished = ref(false)

const whColumns = computed(() => warehouses.value.map(w => ({ text: w.name, value: w.id })))

const getFieldLabel = (field) => ({ name: '公司名称', phone: '联系电话', address: '公司地址' }[field] || field)

const saveField = async () => {
  submitting.value = true
  try {
    await updateCompanySettings({ [editField.value]: editValue.value })
    company.value[editField.value] = editValue.value
    showEditPopup.value = false
    showSuccessToast('保存成功')
  } catch { showToast('保存失败') }
  submitting.value = false
}

const handleBackup = async () => {
  try {
    await showConfirmDialog({ title: '数据备份', message: '确认执行数据备份？' })
    await backupData()
    showSuccessToast('备份成功')
  } catch {}
}

const handleClearCache = async () => {
  try {
    await showConfirmDialog({ title: '清理缓存', message: '确认清理本地缓存？' })
    localStorage.clear()
    showSuccessToast('缓存已清除')
  } catch {}
}

const handleLogout = async () => {
  try {
    await showConfirmDialog({ title: '退出登录', message: '确认退出登录？' })
    authStore.logout()
    router.replace('/login')
  } catch {}
}

const showLogs = async () => {
  showLogPopup.value = true
  logs.value = []
  logFinished.value = false
  await loadLogs()
}

const loadLogs = async () => {
  try {
    const res = await getOperationLogs({ page_size: 50 })
    logs.value = res.data || []
  } catch {}
  logFinished.value = true
}

const onWhConfirm = async ({ selectedOptions }) => {
  settings.value.defaultWarehouseName = selectedOptions[0].text
  showWhPicker.value = false
  try {
    await updateCompanySettings({ default_warehouse_id: selectedOptions[0].value })
    showSuccessToast('默认仓库已设置')
  } catch {}
}

onMounted(async () => {
  userInfo.value = authStore.user || {}
  try {
    const [compRes, whRes] = await Promise.all([getCompanySettings(), getWarehouses()])
    company.value = compRes.data || {}
    warehouses.value = whRes.data || []
  } catch {}
})
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.system-info { text-align: center; padding: 20px 0; color: #666; font-size: 14px; }
</style>
