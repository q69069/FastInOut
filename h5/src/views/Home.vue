<template>
  <div class="home">
    <div class="header">
      <div class="user-info">
        <span class="welcome">欢迎回来</span>
        <span class="username">{{ authStore.displayName || '业务员' }}</span>
      </div>
      <div class="date">{{ today }}</div>
    </div>

    <div class="modules-card">
      <div class="card-header">
        <span class="card-title">快捷模块</span>
        <van-icon name="edit" size="16" @click="openEdit" />
      </div>
      <div class="modules-grid">
        <div
          v-for="key in displayKeys"
          :key="key"
          class="module-item"
          @click="navigate(key)"
        >
          <div class="module-icon" :style="{background: MODULE_META[key].color}">
            <van-icon :name="MODULE_META[key].icon" />
          </div>
          <span class="module-label">{{ MODULE_META[key].label }}</span>
        </div>
      </div>
    </div>

    <div class="stats-card">
      <div class="card-title">今日数据</div>
      <div class="stats-grid">
        <div class="stat-item"><div class="stat-value">{{ stats.orderCount || 0 }}</div><div class="stat-label">订单数</div></div>
        <div class="stat-item"><div class="stat-value">¥{{ stats.salesAmount || 0 }}</div><div class="stat-label">销售额</div></div>
        <div class="stat-item"><div class="stat-value">¥{{ stats.receiveAmount || 0 }}</div><div class="stat-label">回款额</div></div>
        <div class="stat-item"><div class="stat-value">{{ stats.visitCount || 0 }}</div><div class="stat-label">拜访数</div></div>
      </div>
    </div>

    <div class="todo-card" v-if="todos.length > 0">
      <div class="card-header">
        <span class="card-title">待办事项</span>
        <van-tag type="warning">{{ todos.length }}项</van-tag>
      </div>
      <div class="todo-list">
        <div class="todo-item" v-for="todo in todos.slice(0, 3)" :key="todo.id">
          <van-icon name="clock-o" class="todo-icon" />
          <span class="todo-text">{{ todo.title }}</span>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <van-popup v-model:show="showEdit" position="bottom" round style="max-height:80%">
      <div style="padding:16px">
        <div style="font-weight:bold;text-align:center;margin-bottom:4px">编辑快捷模块</div>
        <p style="font-size:12px;color:#999;margin-bottom:12px;text-align:center">
          点击模块切换选中状态，已选{{ draft.length }}/12个
        </p>
        <div class="edit-grid">
          <div
            v-for="key in allKeys"
            :key="key"
            class="edit-item"
            :class="{ selected: draft.includes(key) }"
            @click="toggleKey(key)"
          >
            <div class="edit-check">
              <van-icon v-if="draft.includes(key)" name="passed" color="#1989fa" size="16" />
              <span v-else style="width:16px;display:inline-block"></span>
            </div>
            <div class="edit-icon-wrap" :style="{background: MODULE_META[key].color}">
              <van-icon :name="MODULE_META[key].icon" size="16" color="#fff" />
            </div>
            <span class="edit-label">{{ MODULE_META[key].label }}</span>
          </div>
        </div>
        <div style="display:flex;gap:10px;margin-top:16px">
          <van-button block @click="showEdit = false">取消</van-button>
          <van-button type="primary" block @click="doSave">保存</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useAuthStore } from '../stores/auth'
import { getTodos, getSalesmanStats } from '../api'
import { MODULE_META, ALL_MODULE_KEYS, getModuleOrder, saveModuleOrder, recordModuleUsage } from '../utils/modulePrefs'

const router = useRouter()
const authStore = useAuthStore()
const today = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
const todos = ref([])
const stats = ref({})
const showEdit = ref(false)
const draft = ref([])

const allKeys = ALL_MODULE_KEYS

const displayKeys = computed(() => getModuleOrder().filter(k => draft.value.includes(k)))

const toggleKey = (key) => {
  const idx = draft.value.indexOf(key)
  if (idx >= 0) {
    if (draft.value.length > 4) {
      draft.value.splice(idx, 1)
    } else {
      showToast('至少保留4个')
    }
  } else {
    if (draft.value.length >= 12) {
      showToast('最多12个')
      return
    }
    draft.value.push(key)
  }
}

const openEdit = () => {
  draft.value = [...displayKeys.value]
  showEdit.value = true
}

const doSave = () => {
  saveModuleOrder(draft.value)
  showEdit.value = false
}

const navigate = (key) => {
  recordModuleUsage(key)
  router.push(MODULE_META[key].path)
}

const loadData = async () => {
  try {
    const [todoRes, statsRes] = await Promise.all([
      getTodos().catch(() => ({ data: [] })),
      getSalesmanStats({ period: 'today' }).catch(() => ({ data: {} }))
    ])
    todos.value = todoRes.data || []
    stats.value = statsRes.data || {}
  } catch {}
}

onMounted(() => {
  draft.value = getModuleOrder().filter(k => ALL_MODULE_KEYS.includes(k))
  if (draft.value.length === 0) draft.value = [...ALL_MODULE_KEYS]
  loadData()
})
</script>

<style scoped>
.home { min-height: 100%; background: #f7f8fa; }
.header { background: linear-gradient(135deg, #ff6b35, #ff9a56); padding: 24px 16px; color: #fff; }
.user-info { display: flex; flex-direction: column; }
.welcome { font-size: 13px; opacity: 0.9; }
.username { font-size: 22px; font-weight: bold; margin-top: 4px; }
.date { font-size: 12px; opacity: 0.8; margin-top: 8px; }
.modules-card { background: #fff; margin: 12px; border-radius: 12px; padding: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-title { font-size: 15px; font-weight: bold; color: #333; }
.modules-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.module-item { display: flex; flex-direction: column; align-items: center; gap: 6px; cursor: pointer; }
.module-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 20px; }
.module-label { font-size: 11px; color: #666; text-align: center; }
.stats-card { background: #fff; margin: 0 12px 12px; border-radius: 12px; padding: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.stat-item { text-align: center; padding: 8px 0; }
.stat-value { font-size: 18px; font-weight: bold; color: #ff6b35; }
.stat-label { font-size: 11px; color: #999; margin-top: 4px; }
.todo-card { background: #fff; margin: 0 12px 12px; border-radius: 12px; padding: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.todo-list { display: flex; flex-direction: column; gap: 10px; }
.todo-item { display: flex; align-items: center; gap: 8px; }
.todo-icon { color: #ff9a56; }
.todo-text { font-size: 13px; color: #666; }
.edit-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; max-height: 400px; overflow-y: auto; }
.edit-item {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 10px 4px; border-radius: 8px; cursor: pointer;
  background: #f5f5f5; transition: all 0.15s;
  border: 2px solid transparent;
}
.edit-item.selected { background: #ecf5ff; border-color: #1989fa; }
.edit-check { height: 16px; display: flex; align-items: center; }
.edit-icon-wrap { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.edit-label { font-size: 11px; color: #666; text-align: center; }
.edit-item.selected .edit-label { color: #1989fa; font-weight: 500; }
</style>
