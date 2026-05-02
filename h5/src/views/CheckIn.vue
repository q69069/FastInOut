<template>
  <div class="checkin-page">
    <van-nav-bar title="门店打卡" />
    <div class="content">
      <van-button type="primary" size="large" :loading="loading" @click="handleCheckIn">打卡签到</van-button>
      <van-cell-group title="打卡记录" style="margin-top: 20px;">
        <van-cell v-for="item in records" :key="item.id" :title="item.customer_name" :label="item.checkin_time" />
      </van-cell-group>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'
import { checkIn } from '../api'

const loading = ref(false)
const records = ref([])

const handleCheckIn = async () => {
  loading.value = true
  try {
    await checkIn({ location: '当前位置' })
    showToast('打卡成功')
    records.value.unshift({ id: Date.now(), customer_name: '门店', checkin_time: new Date().toLocaleString() })
  } catch (e) {
    showToast('打卡失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.checkin-page { background: #f7f8fa; min-height: 100vh; }
.content { padding: 20px; }
</style>