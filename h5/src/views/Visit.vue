<template>
  <div class="visit-page">
    <van-nav-bar title="拜访记录" left-arrow @click-left="$router.back()" />

    <!-- 拜访计划 -->
    <div class="visit-plan" v-if="todayPlan.length > 0">
      <div class="section-title">今日拜访计划</div>
      <div v-for="item in todayPlan" :key="item.id" class="visit-card">
        <div class="visit-header">
          <div class="customer-name">{{ item.customer_name }}</div>
          <van-tag :type="item.status === '已完成' ? 'success' : 'warning'" size="small">
            {{ item.status || '待拜访' }}
          </van-tag>
        </div>
        <div class="visit-info">
          <van-icon name="location-o" /> {{ item.address || '地址待定' }}
        </div>
        <div class="visit-actions">
          <van-button size="small" type="primary" @click="handleCheckin(item)">打卡</van-button>
          <van-button size="small" @click="handleOrder(item)">下单</van-button>
        </div>
      </div>
    </div>

    <!-- 拜访记录 -->
    <div class="visit-history">
      <div class="section-title">拜访记录</div>
      <van-cell-group inset>
        <van-cell v-for="item in records" :key="item.id">
          <template #title>
            <div class="record-title">{{ item.customer_name }}</div>
            <div class="record-time">{{ item.visit_time }}</div>
          </template>
          <template #value>
            <van-tag :type="item.status === '已打卡' ? 'success' : 'default'" size="small">
              {{ item.status }}
            </van-tag>
          </template>
        </van-cell>
      </van-cell-group>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast } from 'vant'
import { getVisits } from '../api'

const todayPlan = ref([])
const records = ref([])

const handleCheckin = (item) => {
  showToast('打卡功能开发中')
}

const handleOrder = (item) => {
  window.location.href = `/order?customer_id=${item.customer_id}`
}

const loadData = async () => {
  try {
    const res = await getVisits()
    records.value = res.data || []
    todayPlan.value = records.value.slice(0, 3)
  } catch (e) {
    records.value = []
  }
}

onMounted(loadData)
</script>

<style scoped>
.visit-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.section-title { font-size: 15px; font-weight: bold; color: #333; margin: 16px 12px 8px; }
.visit-card {
  background: #fff;
  margin: 0 12px 12px;
  border-radius: 12px;
  padding: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.visit-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.customer-name { font-size: 15px; font-weight: bold; color: #333; }
.visit-info { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #999; margin-bottom: 12px; }
.visit-actions { display: flex; gap: 8px; }
.visit-history { margin-top: 8px; }
.record-title { font-size: 14px; color: #333; }
.record-time { font-size: 12px; color: #999; margin-top: 4px; }
</style>