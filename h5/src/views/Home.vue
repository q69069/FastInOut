<template>
  <div class="home">
    <!-- 头部区域 -->
    <div class="header">
      <div class="user-info">
        <span class="welcome">欢迎回来</span>
        <span class="username">{{ authStore.displayName || '业务员' }}</span>
      </div>
      <div class="date">{{ today }}</div>
    </div>

    <!-- 快捷模块入口 -->
    <div class="modules-card">
      <div class="card-header">
        <span class="card-title">快捷模块</span>
        <van-icon name="edit" size="16" @click="showEdit = true" />
      </div>
      <div class="modules-grid">
        <div
          v-for="key in visibleModules"
          :key="key"
          class="module-item"
          @click="navigate(key)"
        >
          <div class="module-icon" :style="{background: moduleMeta[key].color}">
            <van-icon :name="moduleMeta[key].icon" />
          </div>
          <span class="module-label">{{ moduleMeta[key].label }}</span>
        </div>
      </div>
    </div>

    <!-- 今日数据看板 -->
    <div class="stats-card">
      <div class="card-title">今日数据</div>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ stats.orderCount || 0 }}</div>
          <div class="stat-label">订单数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">¥{{ stats.salesAmount || 0 }}</div>
          <div class="stat-label">销售额</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">¥{{ stats.receiveAmount || 0 }}</div>
          <div class="stat-label">回款额</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.visitCount || 0 }}</div>
          <div class="stat-label">拜访数</div>
        </div>
      </div>
    </div>

    <!-- 待办提醒 -->
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
    <van-popup v-model:show="showEdit" position="bottom" round style="max-height:70%">
      <div style="padding:16px">
        <div style="font-weight:bold;text-align:center;margin-bottom:8px">编辑快捷模块</div>
        <p style="font-size:12px;color:#999;margin-bottom:12px">
          点击模块添加/移除，已按使用频率自动排序
        </p>
        <van-checkbox-group v-model="selected">
          <van-cell-group inset>
            <van-cell
              v-for="key in allKeys"
              :key="key"
              clickable
              @click="toggleModule(key)"
            >
              <template #title>
                <div style="display:flex;align-items:center;gap:8px">
                  <van-icon :name="moduleMeta[key].icon" :color="moduleMeta[key].color" size="18" />
                  <span>{{ moduleMeta[key].label }}</span>
                </div>
              </template>
              <template #right-icon>
                <van-checkbox :name="key" :ref="el => checkboxRefs[key] = el" />
              </template>
            </van-cell>
          </van-cell-group>
        </van-checkbox-group>
        <div style="display:flex;gap:12px;margin-top:16px">
          <van-button block @click="showEdit = false">取消</van-button>
          <van-button type="primary" block @click="saveModules">保存</van-button>
          <van-button block @click="resetModules">重置</van-button>
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
const selected = ref([])
const checkboxRefs = ref({})

const moduleMeta = MODULE_META
const allKeys = ALL_MODULE_KEYS

const visibleModules = computed(() => {
  const order = getModuleOrder()
  return order.filter(k => selected.value.includes(k))
})

const toggleModule = (key) => {
  if (selected.value.includes(key)) {
    if (selected.value.length > 4) {
      selected.value = selected.value.filter(k => k !== key)
    } else {
      showToast('至少保留4个模块')
    }
  } else {
    selected.value.push(key)
  }
}

const navigate = (key) => {
  recordModuleUsage(key)
  router.push(MODULE_META[key].path)
}

const saveModules = () => {
  saveModuleOrder(selected.value)
  showEdit.value = false
}

const resetModules = () => {
  selected.value = [...ALL_MODULE_KEYS]
}

const loadData = async () => {
  try {
    const [todoRes, statsRes] = await Promise.all([
      getTodos().catch(() => ({ data: [] })),
      getSalesmanStats({ period: 'today' }).catch(() => ({ data: {} }))
    ])
    todos.value = todoRes.data || []
    stats.value = statsRes.data || {}
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  selected.value = getModuleOrder().filter(k => ALL_MODULE_KEYS.includes(k))
  if (selected.value.length === 0) selected.value = [...ALL_MODULE_KEYS]
  loadData()
})
</script>

<style scoped>
.home { min-height: 100%; background: #f7f8fa; }
.header {
  background: linear-gradient(135deg, #ff6b35, #ff9a56);
  padding: 24px 16px;
  color: #fff;
}
.user-info { display: flex; flex-direction: column; }
.welcome { font-size: 13px; opacity: 0.9; }
.username { font-size: 22px; font-weight: bold; margin-top: 4px; }
.date { font-size: 12px; opacity: 0.8; margin-top: 8px; }
.modules-card {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-title { font-size: 15px; font-weight: bold; color: #333; }
.modules-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.module-item {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  cursor: pointer;
}
.module-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 20px;
}
.module-label { font-size: 11px; color: #666; text-align: center; }
.stats-card {
  background: #fff;
  margin: 0 12px 12px;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.stat-item { text-align: center; padding: 8px 0; }
.stat-value { font-size: 18px; font-weight: bold; color: #ff6b35; }
.stat-label { font-size: 11px; color: #999; margin-top: 4px; }
.todo-card {
  background: #fff;
  margin: 0 12px 12px;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.todo-list { display: flex; flex-direction: column; gap: 10px; }
.todo-item { display: flex; align-items: center; gap: 8px; }
.todo-icon { color: #ff9a56; }
.todo-text { font-size: 13px; color: #666; }
</style>
