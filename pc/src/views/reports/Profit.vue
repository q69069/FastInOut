<template>
  <div>
    <!-- Summary Cards -->
    <el-row :gutter="20" style="margin-bottom:20px">
      <el-col :span="6" v-for="card in summaryCards" :key="card.title">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" :style="{background: card.color}">
              <el-icon :size="28"><component :is="card.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-title">{{ card.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Chart -->
    <el-card style="margin-bottom:20px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>利润趋势</span>
          <el-form :inline="true" :model="query" @submit.prevent="loadData">
            <el-form-item>
              <el-date-picker
                v-model="query.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item>
              <el-select v-model="query.group_by" style="width:100px">
                <el-option label="按日" value="day" />
                <el-option label="按月" value="month" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadData">查询</el-button>
            </el-form-item>
          </el-form>
        </div>
      </template>
      <div ref="chartRef" style="width:100%;height:400px"></div>
    </el-card>

    <!-- Table -->
    <el-card>
      <template #header>利润明细</template>
      <el-table :data="tableData" border stripe show-summary :summary-method="getSummary">
        <el-table-column prop="period" label="时间周期" width="150" />
        <el-table-column prop="sales_amount" label="销售金额" width="150">
          <template #default="{ row }">¥{{ formatNum(row.sales_amount) }}</template>
        </el-table-column>
        <el-table-column prop="cost_amount" label="成本金额" width="150">
          <template #default="{ row }">¥{{ formatNum(row.cost_amount) }}</template>
        </el-table-column>
        <el-table-column prop="profit" label="利润" width="150">
          <template #default="{ row }">
            <span :style="{color: row.profit >= 0 ? '#67C23A' : '#F56C6C'}">¥{{ formatNum(row.profit) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="margin_rate" label="利润率" width="120">
          <template #default="{ row }">{{ ((row.margin_rate || 0) * 100).toFixed(2) }}%</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getProfitReport } from '../../api'

const chartRef = ref(null)
let chartInstance = null
const tableData = ref([])
const query = ref({
  dateRange: [],
  group_by: 'day'
})

const summaryCards = computed(() => {
  const totalSales = tableData.value.reduce((s, r) => s + Number(r.sales_amount || 0), 0)
  const totalCost = tableData.value.reduce((s, r) => s + Number(r.cost_amount || 0), 0)
  const totalProfit = totalSales - totalCost
  const avgMargin = totalSales > 0 ? (totalProfit / totalSales) : 0
  return [
    { title: '总销售额', value: `¥${formatNum(totalSales)}`, icon: 'TrendCharts', color: '#409EFF' },
    { title: '总成本', value: `¥${formatNum(totalCost)}`, icon: 'Wallet', color: '#E6A23C' },
    { title: '总利润', value: `¥${formatNum(totalProfit)}`, icon: 'Coin', color: totalProfit >= 0 ? '#67C23A' : '#F56C6C' },
    { title: '平均利润率', value: `${(avgMargin * 100).toFixed(2)}%`, icon: 'DataAnalysis', color: '#909399' }
  ]
})

const formatNum = (n) => {
  if (!n && n !== 0) return '0.00'
  return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

const getSummary = ({ columns, data }) => {
  const sums = []
  columns.forEach((col, index) => {
    if (index === 0) { sums[index] = '合计'; return }
    const values = data.map(item => Number(item[col.property] || 0))
    const sum = values.reduce((a, b) => a + b, 0)
    if (col.property === 'margin_rate') {
      const totalSales = data.reduce((s, r) => s + Number(r.sales_amount || 0), 0)
      const totalProfit = data.reduce((s, r) => s + Number(r.profit || 0), 0)
      sums[index] = totalSales > 0 ? `${((totalProfit / totalSales) * 100).toFixed(2)}%` : '0.00%'
    } else {
      sums[index] = `¥${formatNum(sum)}`
    }
  })
  return sums
}

const initChart = () => {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)
  const periods = tableData.value.map(r => r.period)
  const salesData = tableData.value.map(r => Number(r.sales_amount || 0))
  const costData = tableData.value.map(r => Number(r.cost_amount || 0))
  const profitData = tableData.value.map(r => Number(r.profit || 0))
  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['销售额', '成本', '利润'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: periods },
    yAxis: { type: 'value', name: '金额 (元)' },
    series: [
      { name: '销售额', type: 'line', data: salesData, smooth: true, itemStyle: { color: '#409EFF' } },
      { name: '成本', type: 'line', data: costData, smooth: true, itemStyle: { color: '#E6A23C' } },
      { name: '利润', type: 'line', data: profitData, smooth: true, itemStyle: { color: '#67C23A' } }
    ]
  })
}

const loadData = async () => {
  const params = { group_by: query.value.group_by }
  if (query.value.dateRange && query.value.dateRange.length === 2) {
    params.start_date = query.value.dateRange[0]
    params.end_date = query.value.dateRange[1]
  }
  const res = await getProfitReport(params)
  tableData.value = res.data || []
  await nextTick()
  initChart()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => { chartInstance && chartInstance.resize() })
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
}
.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 16px;
}
.stat-info {
  flex: 1;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}
.stat-title {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}
</style>
