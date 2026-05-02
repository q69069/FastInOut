<template>
  <div class="performance-page">
    <div class="stats-card">
      <div class="stat-item">
        <div class="value">{{ stats.today_amount || 0 }}</div>
        <div class="label">今日销售额</div>
      </div>
      <div class="stat-item">
        <div class="value">{{ stats.month_amount || 0 }}</div>
        <div class="label">本月销售额</div>
      </div>
    </div>
    <van-pull-refresh v-model="refreshing" @refresh="loadData">
      <van-cell-group inset title="业绩详情">
        <van-cell v-for="item in list" :key="item.id" :title="item.date" :value="`¥${item.amount}`" />
      </van-cell-group>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSalesmanStats } from '../api'

const stats = ref({})
const list = ref([])
const refreshing = ref(false)

const loadData = async () => {
  try {
    const res = await getSalesmanStats()
    stats.value = res.data?.stats || {}
    list.value = res.data?.list || []
  } catch (e) {
    console.error(e)
  } finally {
    refreshing.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.performance-page {
  min-height: 100vh;
  background: #f7f8fa;
}
.stats-card {
  display: flex;
  background: linear-gradient(135deg, #1989fa, #396bec);
  padding: 24px 16px;
  color: #fff;
}
.stat-item {
  flex: 1;
  text-align: center;
}
.value {
  font-size: 24px;
  font-weight: bold;
}
.label {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 4px;
}
</style>
