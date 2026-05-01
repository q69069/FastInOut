<template>
  <div>
    <!-- Filters -->
    <el-card style="margin-bottom:20px">
      <template #header>销售排行</template>
      <el-form :inline="true" :model="query" @submit.prevent="loadData">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="query.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="显示数量">
          <el-select v-model="query.limit" style="width:120px">
            <el-option label="Top 10" :value="10" />
            <el-option label="Top 20" :value="20" />
            <el-option label="Top 50" :value="50" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Chart -->
    <el-card style="margin-bottom:20px">
      <template #header>销售额排行</template>
      <div ref="chartRef" style="width:100%;height:500px"></div>
    </el-card>

    <!-- Table -->
    <el-card>
      <template #header>排行明细</template>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="rank" label="排名" width="80" align="center">
          <template #default="{ row, $index }">
            <el-tag :type="$index < 3 ? 'danger' : 'info'" effect="dark" round size="small">
              {{ row.rank || $index + 1 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="quantity" label="销售数量" width="120" sortable />
        <el-table-column prop="amount" label="销售金额" width="150" sortable>
          <template #default="{ row }">¥{{ formatNum(row.amount) }}</template>
        </el-table-column>
        <el-table-column prop="profit" label="利润" width="150" sortable>
          <template #default="{ row }">
            <span :style="{color: row.profit >= 0 ? '#67C23A' : '#F56C6C'}">¥{{ formatNum(row.profit) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getSalesReport } from '../../api'

const chartRef = ref(null)
let chartInstance = null
const tableData = ref([])
const query = ref({
  dateRange: [],
  limit: 10
})

const formatNum = (n) => {
  if (!n && n !== 0) return '0.00'
  return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

const initChart = () => {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)
  const sorted = [...tableData.value]
  const names = sorted.map(r => r.product_name).reverse()
  const amounts = sorted.map(r => Number(r.amount || 0)).reverse()
  chartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', name: '销售额 (元)' },
    yAxis: { type: 'category', data: names, axisLabel: { width: 120, overflow: 'truncate' } },
    series: [
      {
        name: '销售额',
        type: 'bar',
        data: amounts,
        itemStyle: {
          color: (params) => {
            const colors = ['#F56C6C', '#E6A23C', '#409EFF', '#67C23A']
            const idx = amounts.length - 1 - params.dataIndex
            return idx < 3 ? colors[idx] : colors[3]
          }
        },
        label: { show: true, position: 'right', formatter: (p) => `¥${formatNum(p.value)}` }
      }
    ]
  })
}

const loadData = async () => {
  const params = { group_by: 'day' }
  if (query.value.dateRange && query.value.dateRange.length === 2) {
    params.start_date = query.value.dateRange[0]
    params.end_date = query.value.dateRange[1]
  }
  const res = await getSalesReport(params)
  let data = res.data || []
  // Sort by amount desc and limit
  data = data.sort((a, b) => Number(b.amount || 0) - Number(a.amount || 0)).slice(0, query.value.limit)
  // Add rank
  data.forEach((item, index) => { item.rank = index + 1 })
  tableData.value = data
  await nextTick()
  initChart()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => { chartInstance && chartInstance.resize() })
})
</script>
