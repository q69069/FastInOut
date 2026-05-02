<template>
  <div class="performance-page">
    <van-nav-bar title="业绩统计" />
    <van-tabs v-model:active="activeTab">
      <van-tab title="今日" name="today" />
      <van-tab title="本周" name="week" />
      <van-tab title="本月" name="month" />
    </van-tabs>
    <div class="stats">
      <van-cell-group>
        <van-cell title="销售额" :value="`¥${stats.sales_amount || 0}`" />
        <van-cell title="回款额" :value="`¥${stats.receive_amount || 0}`" />
        <van-cell title="订单数" :value="`${stats.order_count || 0}`" />
        <van-cell title="毛利" :value="`¥${stats.profit || 0}`" />
      </van-cell-group>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getSalesmanStats } from '../api'

const activeTab = ref('today')
const stats = ref({})

const loadData = async () => {
  try {
    const res = await getSalesmanStats({ period: activeTab.value })
    stats.value = res.data || {}
  } catch (e) {
    stats.value = {}
  }
}

watch(activeTab, loadData)
onMounted(loadData)
</script>

<style scoped>
.performance-page { background: #f7f8fa; min-height: 100vh; }
.stats { margin-top: 12px; }
</style>