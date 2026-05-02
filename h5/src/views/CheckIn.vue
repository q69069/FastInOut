<template>
  <div class="checkin-page">
    <div class="checkin-card">
      <van-icon name="location-o" size="48" color="#1989fa" />
      <div class="location">{{ location }}</div>
      <van-button type="primary" size="large" @click="handleCheckIn" :loading="loading">
        打卡
      </van-button>
    </div>
    <van-pull-refresh v-model="refreshing" @refresh="loadRecords">
      <van-cell-group inset title="打卡记录">
        <van-cell v-for="item in records" :key="item.id" :title="item.checkin_time" :value="item.type_text" />
      </van-cell-group>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast } from 'vant'
import { checkIn, getCheckinRecords } from '../api'

const location = ref('正在获取位置...')
const loading = ref(false)
const refreshing = ref(false)
const records = ref([])

const handleCheckIn = async () => {
  loading.value = true
  try {
    await checkIn({ location: location.value })
    showToast('打卡成功')
    loadRecords()
  } catch (e) {
    showToast('打卡失败')
  } finally {
    loading.value = false
  }
}

const loadRecords = async () => {
  try {
    const res = await getCheckinRecords()
    records.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    refreshing.value = false
  }
}

onMounted(() => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      location.value = `${pos.coords.latitude.toFixed(6)}, ${pos.coords.longitude.toFixed(6)}`
    }, () => {
      location.value = '位置获取失败'
    })
  }
  loadRecords()
})
</script>

<style scoped>
.checkin-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding: 16px;
}
.checkin-card {
  background: #fff;
  border-radius: 12px;
  padding: 32px 16px;
  text-align: center;
  margin-bottom: 16px;
}
.location {
  margin: 16px 0;
  color: #666;
  font-size: 14px;
}
</style>
