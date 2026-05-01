<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>采购/销售趋势图</span>
          <div style="display:flex;gap:8px">
            <el-radio-group v-model="trendType" @change="loadData">
              <el-radio-button value="sales">销售</el-radio-button>
              <el-radio-button value="purchase">采购</el-radio-button>
            </el-radio-group>
            <el-radio-group v-model="period" @change="loadData">
              <el-radio-button value="month">按月</el-radio-button>
              <el-radio-button value="quarter">按季度</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>
      <div ref="chartRef" style="width:100%;height:400px"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getTrendReport } from '../../api'

const trendType = ref('sales')
const period = ref('month')
const chartRef = ref(null)
let chart = null

const loadData = async () => {
  const res = await getTrendReport({ trend_type: trendType.value, period: period.value, months: 12 })
  const items = res.data || []
  const labels = items.map(i => i.period)
  const amounts = items.map(i => i.amount)
  const counts = items.map(i => i.count)

  if (!chart && chartRef.value) {
    chart = echarts.init(chartRef.value)
  }
  if (!chart) return

  const title = trendType.value === 'sales' ? '销售' : '采购'
  chart.setOption({
    title: { text: `${title}趋势`, left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['金额', '单数'], top: 30 },
    grid: { left: 60, right: 60, bottom: 40, top: 70 },
    xAxis: { type: 'category', data: labels },
    yAxis: [
      { type: 'value', name: '金额(元)', position: 'left' },
      { type: 'value', name: '单数', position: 'right' }
    ],
    series: [
      {
        name: '金额', type: 'bar', data: amounts,
        itemStyle: { color: trendType.value === 'sales' ? '#409EFF' : '#67C23A' },
        yAxisIndex: 0
      },
      {
        name: '单数', type: 'line', data: counts,
        itemStyle: { color: '#E6A23C' },
        yAxisIndex: 1
      }
    ]
  })
}

const handleResize = () => { chart?.resize() }

onMounted(() => {
  nextTick(() => {
    loadData()
    window.addEventListener('resize', handleResize)
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>
