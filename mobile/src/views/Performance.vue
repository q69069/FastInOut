<template>
  <div class="page">
    <van-nav-bar title="业绩查看" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="content">
      <!-- 今日 -->
      <div class="stat-card">
        <div class="stat-title">📅 今日</div>
        <div class="stat-row">
          <div class="stat-item"><span class="val">¥{{ todaySales.toFixed(2) }}</span><span class="lbl">销售额</span></div>
          <div class="stat-item"><span class="val">{{ todayOrders }}</span><span class="lbl">订单</span></div>
          <div class="stat-item"><span class="val">¥{{ todayCollected.toFixed(2) }}</span><span class="lbl">回款</span></div>
          <div class="stat-item"><span class="val">{{ todayVisits }}</span><span class="lbl">拜访</span></div>
        </div>
      </div>

      <!-- 本周 -->
      <div class="stat-card">
        <div class="stat-title">📊 本周</div>
        <div class="stat-row">
          <div class="stat-item"><span class="val">¥{{ weekSales.toFixed(2) }}</span><span class="lbl">销售额</span></div>
          <div class="stat-item"><span class="val">{{ weekOrders }}</span><span class="lbl">订单</span></div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: weekPercent + '%' }"></div>
        </div>
        <span class="progress-text">周目标完成率 {{ weekPercent }}%</span>
      </div>

      <!-- 本月 -->
      <div class="stat-card highlight">
        <div class="stat-title">🏆 本月</div>
        <div class="stat-row">
          <div class="stat-item"><span class="val">¥{{ monthSales.toFixed(2) }}</span><span class="lbl">销售额</span></div>
          <div class="stat-item"><span class="val">¥{{ commission.toFixed(2) }}</span><span class="lbl">预估提成</span></div>
        </div>
        <div class="rank-badge">🥈 排名第2/8</div>
      </div>

      <van-button round block plain @click="$router.back()" style="margin: 20px 12px;">返回工作台</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const todaySales = ref(3200); const todayOrders = ref(5); const todayCollected = ref(2800); const todayVisits = ref(8)
const weekSales = ref(15600); const weekOrders = ref(23); const weekPercent = ref(78)
const monthSales = ref(68000); const commission = ref(2040)

onMounted(async () => {
  try {
    const res = await api.get('/salesmen/performance')
    if (res.data.data) Object.assign({}, res.data.data)
  } catch (e) { /* 使用默认数据 */ }
})
</script>

<style scoped>
.page { min-height: 100vh; background: #f7f8fa; padding-bottom: 20px; }
.content { padding: 12px; }
.stat-card { background: #fff; border-radius: 12px; padding: 16px; margin: 8px 0; }
.stat-card.highlight { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
.stat-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; }
.stat-row { display: flex; gap: 12px; flex-wrap: wrap; }
.stat-item { display: flex; flex-direction: column; align-items: center; min-width: 60px; }
.stat-item .val { font-size: 20px; font-weight: 700; }
.stat-item .lbl { font-size: 11px; opacity: .7; margin-top: 2px; }
.highlight .stat-item .val { font-size: 22px; }
.progress-bar { height: 6px; background: #e5e5e5; border-radius: 3px; margin-top: 10px; }
.progress-fill { height: 100%; background: #1989fa; border-radius: 3px; transition: width .5s; }
.progress-text { font-size: 12px; color: #999; margin-top: 4px; display: block; }
.rank-badge { margin-top: 8px; font-size: 14px; font-weight: 600; }
</style>
