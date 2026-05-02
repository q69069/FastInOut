<template>
  <div class="dashboard-page">
    <van-nav-bar title="数据看板" />

    <!-- 核心指标 -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-value orange">¥{{ kpiData.todaySales }}</div>
        <div class="kpi-label">今日销售额</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value green">¥{{ kpiData.todayReceive }}</div>
        <div class="kpi-label">今日回款</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value blue">¥{{ kpiData.receivable }}</div>
        <div class="kpi-label">应收余额</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value red">{{ kpiData.orderCount }}</div>
        <div class="kpi-label">待审核单</div>
      </div>
    </div>

    <!-- 销售趋势 -->
    <div class="chart-card">
      <div class="card-title">销售趋势（近7天）</div>
      <div class="trend-chart">
        <div v-for="(item, index) in salesTrend" :key="index" class="trend-item">
          <div class="trend-bar-wrap">
            <div class="trend-bar" :style="{ height: getBarHeight(item.amount) + 'px' }"></div>
          </div>
          <div class="trend-label">{{ item.date }}</div>
          <div class="trend-value">¥{{ item.amount }}</div>
        </div>
      </div>
    </div>

    <!-- 业绩排行 -->
    <div class="rank-card">
      <div class="card-title">员工业绩排行</div>
      <van-cell-group inset>
        <van-cell v-for="(item, index) in salesRanking" :key="index">
          <template #title>
            <span :class="['rank-badge', getRankClass(index)]">{{ index + 1 }}</span>
            {{ item.name }}
          </template>
          <template #value>
            <span class="rank-value">¥{{ item.amount }}</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 商品销量排行 -->
    <div class="rank-card">
      <div class="card-title">商品销量排行</div>
      <van-cell-group inset>
        <van-cell v-for="(item, index) in productRanking" :key="index">
          <template #title>{{ index + 1 }}. {{ item.name }}</template>
          <template #value>
            <span>{{ item.quantity }}件 / ¥{{ item.amount }}</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 仓库库存预警 -->
    <div class="alert-card" v-if="stockAlerts.length > 0">
      <div class="card-title red">库存预警</div>
      <van-cell-group inset>
        <van-cell v-for="item in stockAlerts" :key="item.id" :label="item.warehouse">
          <template #title>
            <span class="alert-product">{{ item.product_name }}</span>
          </template>
          <template #value>
            <van-tag type="danger">库存: {{ item.quantity }}</van-tag>
          </template>
        </van-cell>
      </van-cell-group>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboard } from '../api'

const kpiData = ref({
  todaySales: '0.00',
  todayReceive: '0.00',
  receivable: '0.00',
  orderCount: 0
})
const salesTrend = ref([])
const salesRanking = ref([])
const productRanking = ref([])
const stockAlerts = ref([])

const getBarHeight = (amount) => {
  if (!salesTrend.value.length) return 0
  const max = Math.max(...salesTrend.value.map(t => t.amount))
  if (!max) return 0
  return Math.max(10, (amount / max) * 60)
}

const getRankClass = (index) => {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}

const loadData = async () => {
  try {
    const res = await getDashboard()
    kpiData.value = res.data?.kpi || kpiData.value
    salesTrend.value = res.data?.salesTrend || []
    salesRanking.value = res.data?.salesRanking || []
    productRanking.value = res.data?.productRanking || []
    stockAlerts.value = res.data?.stockAlerts || []
  } catch (e) {
    // 模拟数据
    kpiData.value = { todaySales: '12580', todayReceive: '8600', receivable: '35800', orderCount: 3 }
    salesTrend.value = [
      { date: '05-01', amount: 8500 },
      { date: '05-02', amount: 12800 },
      { date: '05-03', amount: 9600 },
      { date: '05-04', amount: 15200 },
      { date: '05-05', amount: 7800 },
      { date: '05-06', amount: 11000 },
      { date: '05-07', amount: 12580 }
    ]
    salesRanking.value = [
      { name: '张三', amount: 15800 },
      { name: '李四', amount: 12600 },
      { name: '王五', amount: 9800 }
    ]
    productRanking.value = [
      { name: '可口可乐', quantity: 120, amount: 3600 },
      { name: '雪碧', quantity: 98, amount: 2940 },
      { name: '农夫山泉', quantity: 85, amount: 2550 }
    ]
    stockAlerts.value = [
      { id: 1, product_name: '农夫山泉', quantity: 5, warehouse: '主仓库' },
      { id: 2, product_name: '王老吉', quantity: 8, warehouse: '分仓库' }
    ]
  }
}

onMounted(loadData)
</script>

<style scoped>
.dashboard-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.kpi-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; padding: 12px; }
.kpi-card { background: #fff; border-radius: 12px; padding: 16px; text-align: center; }
.kpi-value { font-size: 22px; font-weight: bold; }
.kpi-label { font-size: 12px; color: #999; margin-top: 4px; }
.orange { color: #ff6b35; }
.green { color: #07c160; }
.blue { color: #1989fa; }
.red { color: #ee0a24; }
.chart-card, .rank-card, .alert-card { background: #fff; margin: 12px; border-radius: 12px; padding: 16px; }
.card-title { font-size: 15px; font-weight: bold; color: #333; margin-bottom: 12px; }
.card-title.red { color: #ee0a24; }
.trend-chart { display: flex; justify-content: space-between; height: 120px; }
.trend-item { flex: 1; display: flex; flex-direction: column; align-items: center; }
.trend-bar-wrap { height: 60px; display: flex; align-items: flex-end; }
.trend-bar { width: 20px; background: linear-gradient(135deg, #ff6b35, #ff9a56); border-radius: 4px 4px 0 0; min-height: 4px; }
.trend-label { font-size: 10px; color: #999; margin-top: 4px; }
.trend-value { font-size: 10px; color: #666; margin-top: 2px; }
.rank-badge { display: inline-block; width: 16px; height: 16px; line-height: 16px; text-align: center; border-radius: 50%; font-size: 10px; margin-right: 6px; }
.rank-badge.gold { background: #ffd700; color: #fff; }
.rank-badge.silver { background: #c0c0c0; color: #fff; }
.rank-badge.bronze { background: #cd7f32; color: #fff; }
.rank-value { color: #ff6b35; font-weight: bold; }
.alert-product { font-size: 13px; color: #333; }
</style>