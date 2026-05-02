<template>
  <div class="page">
    <van-nav-bar title="拜访计划" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="summary-bar">
      <span>今日拜访 <b>{{ customers.length }}</b> 家</span>
      <span>已完成 <b>{{ doneCount }}</b> 家</span>
    </div>
    <van-pull-refresh v-model="refreshing" @refresh="loadPlan">
      <div v-if="customers.length === 0" class="empty">
        <van-empty description="今日无拜访计划" />
      </div>
      <div v-for="(c, i) in customers" :key="c.id" class="card"
        :class="{ done: c.visited }" @click="visit(c)">
        <div class="rank">{{ i + 1 }}</div>
        <div class="info">
          <div class="name">{{ c.name }}</div>
          <div class="meta">
            <span class="dist">📍 {{ c.distance || '--' }}km</span>
            <span>上次: {{ c.last_visit || '--' }}</span>
          </div>
        </div>
        <div class="badge" :class="c.visited ? 'done' : 'todo'">
          {{ c.visited ? '🟢' : '⚪' }}
        </div>
      </div>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const refreshing = ref(false)
const customers = ref([])

const doneCount = computed(() => customers.value.filter(c => c.visited).length)

const loadPlan = async () => {
  try {
    const res = await api.get('/customers', {
      params: { route_ids: auth.routeIds.join(','), page: 1, limit: 100 }
    })
    customers.value = (res.data.data?.items || []).map(c => ({
      ...c, visited: false, distance: (Math.random() * 3).toFixed(1), last_visit: '--'
    }))
  } catch (e) { /* ignore */ } finally { refreshing.value = false }
}

const visit = (c) => {
  // 跳转打卡页面
  import('@/router').then(m => m.default.push({ name: 'StoreCheckin', query: { customer_id: c.id, customer_name: c.name } }))
}

onMounted(loadPlan)
</script>

<style scoped>
.page { min-height: 100vh; background: #f7f8fa; }
.summary-bar { display: flex; justify-content: space-around; padding: 12px; background: #fff; font-size: 14px; color: #666; }
.summary-bar b { color: #1989fa; }
.card { display: flex; align-items: center; gap: 12px; margin: 8px 12px; padding: 14px; background: #fff; border-radius: 10px; }
.card.done { opacity: .6; }
.rank { width: 28px; height: 28px; border-radius: 50%; background: #1989fa; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; }
.info { flex: 1; }
.name { font-size: 15px; font-weight: 600; color: #333; }
.meta { font-size: 12px; color: #999; margin-top: 3px; }
.meta .dist { margin-right: 10px; }
.badge { font-size: 20px; flex-shrink: 0; }
.empty { padding-top: 80px; }
</style>
