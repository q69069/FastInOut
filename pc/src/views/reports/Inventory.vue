<template>
  <div>
    <!-- Summary Cards -->
    <el-row :gutter="20" style="margin-bottom:20px">
      <el-col :span="8" v-for="card in summaryCards" :key="card.title">
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
          <span>库存价值 Top 10</span>
          <el-form :inline="true" :model="query" @submit.prevent="loadData">
            <el-form-item label="仓库">
              <el-select v-model="query.warehouse_id" clearable placeholder="全部仓库" style="width:160px">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
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
      <template #header>库存明细</template>
      <el-table :data="tableData" border stripe>
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="warehouse_name" label="所属仓库" width="150" />
        <el-table-column prop="quantity" label="库存数量" width="120" sortable />
        <el-table-column prop="cost_price" label="成本单价" width="130">
          <template #default="{ row }">¥{{ formatNum(row.cost_price) }}</template>
        </el-table-column>
        <el-table-column prop="total_value" label="库存价值" width="150" sortable>
          <template #default="{ row }">¥{{ formatNum(row.total_value) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getInventoryReport, getWarehouses } from '../../api'

const chartRef = ref(null)
let chartInstance = null
const tableData = ref([])
const warehouses = ref([])
const query = ref({ warehouse_id: null })

const summaryCards = computed(() => {
  const totalProducts = tableData.value.length
  const totalQuantity = tableData.value.reduce((s, r) => s + Number(r.quantity || 0), 0)
  const totalValue = tableData.value.reduce((s, r) => s + Number(r.total_value || 0), 0)
  return [
    { title: '商品种类', value: totalProducts, icon: 'Goods', color: '#409EFF' },
    { title: '库存总量', value: formatNum(totalQuantity), icon: 'Box', color: '#67C23A' },
    { title: '库存总价值', value: `¥${formatNum(totalValue)}`, icon: 'Coin', color: '#E6A23C' }
  ]
})

const formatNum = (n) => {
  if (!n && n !== 0) return '0.00'
  return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

const initChart = () => {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)
  // Sort by total_value desc and take top 10
  const sorted = [...tableData.value].sort((a, b) => Number(b.total_value || 0) - Number(a.total_value || 0)).slice(0, 10)
  const names = sorted.map(r => r.product_name).reverse()
  const values = sorted.map(r => Number(r.total_value || 0)).reverse()
  chartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', name: '价值 (元)' },
    yAxis: { type: 'category', data: names },
    series: [
      {
        name: '库存价值',
        type: 'bar',
        data: values,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#409EFF' },
            { offset: 1, color: '#67C23A' }
          ])
        },
        label: { show: true, position: 'right', formatter: (p) => `¥${formatNum(p.value)}` }
      }
    ]
  })
}

const loadWarehouses = async () => {
  const res = await getWarehouses({ page_size: 100 })
  warehouses.value = res.data || []
}

const loadData = async () => {
  const params = {}
  if (query.value.warehouse_id) params.warehouse_id = query.value.warehouse_id
  const res = await getInventoryReport(params)
  tableData.value = res.data || []
  await nextTick()
  initChart()
}

onMounted(() => {
  loadData()
  loadWarehouses()
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
