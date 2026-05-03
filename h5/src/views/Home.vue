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

    <!-- 快捷功能入口 -->
    <div class="quick-actions">
      <div class="action-item" @click="$router.push('/order')">
        <div class="action-icon orange"><van-icon name="orders-o" /></div>
        <span>快速下单</span>
      </div>
      <div class="action-item" @click="$router.push('/checkin')">
        <div class="action-icon green"><van-icon name="location-o" /></div>
        <span>门店打卡</span>
      </div>
      <div class="action-item" @click="$router.push('/visit')">
        <div class="action-icon blue"><van-icon name="friends-o" /></div>
        <span>拜访记录</span>
      </div>
      <div class="action-item" @click="$router.push('/print')">
        <div class="action-icon purple"><van-icon name="printer-o" /></div>
        <span>打印小票</span>
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

    <!-- 快捷入口卡片 -->
    <div class="shortcut-card">
      <div class="card-title">快捷功能</div>
      <div class="shortcut-grid">
        <div class="shortcut-item" @click="$router.push('/customers')">
          <van-icon name="friends-o" />
          <span>客户管理</span>
        </div>
        <div class="shortcut-item" @click="$router.push('/inventory')">
          <van-icon name="logistics" />
          <span>库存查询</span>
        </div>
        <div class="shortcut-item" @click="$router.push('/transfer')">
          <van-icon name="exchange" />
          <span>调拨单</span>
        </div>
        <div class="shortcut-item" @click="$router.push('/approve')">
          <van-icon name="passed" />
          <span>审核中心</span>
        </div>
        <div class="shortcut-item" @click="$router.push('/receivables')">
          <van-icon name="balance-o" />
          <span>应收应付</span>
        </div>
        <div class="shortcut-item" @click="$router.push('/employee')">
          <van-icon name="manager-o" />
          <span>员工管理</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { getTodos, getSalesmanStats } from '../api'

const authStore = useAuthStore()
const today = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
const todos = ref([])
const stats = ref({})

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

onMounted(loadData)
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
.quick-actions {
  display: flex;
  justify-content: space-around;
  background: #fff;
  padding: 16px 8px;
  margin: -20px 12px 0;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.action-item { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.action-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  color: #fff;
}
.action-icon.orange { background: linear-gradient(135deg, #ff6b35, #ff9a56); }
.action-icon.green { background: linear-gradient(135deg, #07c160, #4cd964); }
.action-icon.blue { background: linear-gradient(135deg, #1989fa, #396bec); }
.action-icon.purple { background: linear-gradient(135deg, #9c27b0, #ba68c8); }
.action-item span { font-size: 12px; color: #666; }
.stats-card {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.card-title { font-size: 15px; font-weight: bold; color: #333; margin-bottom: 12px; }
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
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.todo-list { display: flex; flex-direction: column; gap: 10px; }
.todo-item { display: flex; align-items: center; gap: 8px; }
.todo-icon { color: #ff9a56; }
.todo-text { font-size: 13px; color: #666; }
.shortcut-card {
  background: #fff;
  margin: 0 12px 12px;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.shortcut-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.shortcut-item {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 12px; background: #f7f8fa; border-radius: 8px;
}
.shortcut-item span { font-size: 12px; color: #666; }
.shortcut-item :deep(.van-icon) { font-size: 24px; color: #1989fa; }
</style>