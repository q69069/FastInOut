<template>
  <div class="performance-page">
    <van-nav-bar title="业绩统计" />

    <!-- 时间切换 -->
    <div class="period-tabs">
      <div
        v-for="p in periods"
        :key="p.value"
        :class="['period-tab', { active: period === p.value }]"
        @click="changePeriod(p.value)"
      >
        {{ p.label }}
      </div>
    </div>

    <!-- 核心数据卡片 -->
    <div class="stats-card">
      <div class="main-stat">
        <div class="stat-label">销售额</div>
        <div class="stat-value orange">¥{{ stats.sales_amount || 0 }}</div>
      </div>
      <div class="stat-divider" />
      <div class="main-stat">
        <div class="stat-label">回款额</div>
        <div class="stat-value green">¥{{ stats.receive_amount || 0 }}</div>
      </div>
    </div>

    <!-- 详细数据 -->
    <div class="detail-card">
      <van-cell-group inset>
        <van-cell title="订单数" :value="`${stats.order_count || 0} 单`" />
        <van-cell title="销售毛利" :value="`¥${stats.profit || 0}`" />
        <van-cell title="毛利率" :value="`${stats.profit_rate || 0}%`" />
        <van-cell title="拜访次数" :value="`${stats.visit_count || 0} 次`" />
      </van-cell-group>
    </div>

    <!-- 排行 -->
    <div class="rank-card" v-if="rankList.length > 0">
      <div class="card-title">业绩排行</div>
      <van-cell-group inset>
        <van-cell v-for="(item, index) in rankList" :key="index">
          <template #title>
            <span :class="['rank-badge', getRankClass(index)]">{{ index + 1 }}</span>
            {{ item.product_name || item.customer_name }}
          </template>
          <template #value>
            <span class="rank-value">¥{{ item.amount }}</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 图表区域 -->
    <div class="chart-card">
      <div class="card-title">销售趋势</div>
      <div class="chart-placeholder">
        <van-loading v-if="loading" />
        <span v-else-if="!trendData.length">暂无数据</span>
        <div v-else class="trend-bars">
          <div v-for="(item, index) in trendData.slice(-7)" :key="index" class="trend-bar-wrap">
            <div class="trend-bar" :style="{ height: `${getBarHeight(item.amount)}px` }" />
            <div class="trend-label">{{ item.date }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSalesmanStats } from '../api'

const loading = ref(false)
const period = ref('today')
const stats = ref({})
const rankList = ref([])
const trendData = ref([])

const periods = [
  { label: '今日', value: 'today' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '本年', value: 'year' }
]

const changePeriod = async (p) => {
  period.value = p
  await loadData()
}

const getRankClass = (index) => {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}

const getBarHeight = (amount) => {
  if (!trendData.value.length) return 0
  const max = Math.max(...trendData.value.map(t => t.amount))
  if (!max) return 0
  return Math.max(10, (amount / max) * 80)
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getSalesmanStats({ period: period.value })
    stats.value = res.data || {}
    rankList.value = res.data?.ranking || []
    trendData.value = res.data?.trend || []
  } catch (e) {
    stats.value = {}
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.performance-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.period-tabs { display: flex; background: #fff; padding: 12px; gap: 8px; }
.period-tab {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  border-radius: 20px;
  font-size: 14px;
  color: #666;
  background: #f5f5f5;
}
.period-tab.active { background: #ff6b35; color: #fff; }
.stats-card {
  display: flex;
  background: linear-gradient(135deg, #ff6b35, #ff9a56);
  margin: 12px;
  border-radius: 12px;
  padding: 20px;
  color: #fff;
}
.main-stat { flex: 1; text-align: center; }
.stat-divider { width: 1px; background: rgba(255,255,255,0.3); }
.stat-label { font-size: 13px; opacity: 0.9; }
.stat-value { font-size: 26px; font-weight: bold; margin-top: 8px; }
.orange { color: #ff6b35; }
.green { color: #07c160; }
.detail-card, .rank-card, .chart-card { margin: 12px; }
.card-title { font-size: 15px; font-weight: bold; color: #333; margin-bottom: 8px; padding-left: 4px; }
.rank-badge { display: inline-block; width: 18px; height: 18px; line-height: 18px; text-align: center; border-radius: 50%; font-size: 11px; margin-right: 8px; }
.rank-badge.gold { background: #ffd700; color: #fff; }
.rank-badge.silver { background: #c0c0c0; color: #fff; }
.rank-badge.bronze { background: #cd7f32; color: #fff; }
.rank-value { color: #ff6b35; font-weight: bold; }
.chart-card { background: #fff; border-radius: 12px; padding: 16px; margin: 12px; }
.chart-placeholder { height: 120px; display: flex; align-items: flex-end; justify-content: center; }
.trend-bars { display: flex; align-items: flex-end; gap: 12px; width: 100%; height: 100px; }
.trend-bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; }
.trend-bar { width: 100%; max-width: 30px; background: linear-gradient(135deg, #ff6b35, #ff9a56); border-radius: 4px 4px 0 0; min-height: 4px; }
.trend-label { font-size: 10px; color: #999; margin-top: 4px; }
</style>