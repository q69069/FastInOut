<template>
  <div class="page">
    <van-nav-bar title="门店打卡" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="content">
      <div class="customer-info" v-if="customerName">
        <van-tag type="primary" size="large">{{ customerName }}</van-tag>
      </div>

      <!-- GPS 定位 -->
      <div class="section">
        <van-icon name="location-o" size="20" color="#1989fa" />
        <span>当前定位：{{ locationText }}</span>
        <van-button size="small" :loading="locating" @click="getLocation">重新定位</van-button>
      </div>

      <!-- 拍照 -->
      <div class="section photo-section">
        <div class="photo-box" @click="takePhoto">
          <img v-if="photoUrl" :src="photoUrl" alt="门店照片" />
          <van-icon v-else name="photograph" size="40" color="#ccc" />
          <span v-if="!photoUrl">点击拍照（必填）</span>
        </div>
      </div>

      <!-- 备注 -->
      <van-field v-model="remark" rows="2" type="textarea" placeholder="备注信息（如：老板在，订了冰红茶）" />

      <!-- 拜访目的 -->
      <div class="section radio-group">
        <span class="section-label">拜访目的：</span>
        <van-radio-group v-model="purpose" direction="horizontal">
          <van-radio name="maintain">常规维护</van-radio>
          <van-radio name="collect">催款</van-radio>
          <van-radio name="order">下单</van-radio>
          <van-radio name="after_sale">售后</van-radio>
        </van-radio-group>
      </div>

      <van-button round block type="primary" :loading="submitting" @click="submitCheckin"
        :disabled="!photoUrl || !lat" style="margin: 20px 16px;">
        ✅ 签到打卡
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import api from '@/api'

const route = useRoute()
const customerName = ref(route.query.customer_name || '')
const customerId = ref(route.query.customer_id || '')
const lat = ref(null); const lng = ref(null)
const locating = ref(false)
const locationText = ref('定位中...')
const photoUrl = ref('')
const remark = ref('')
const purpose = ref('maintain')
const submitting = ref(false)

const getLocation = () => {
  locating.value = true
  if (!navigator.geolocation) {
    locationText.value = '不支持定位'; locating.value = false; return
  }
  navigator.geolocation.getCurrentPosition(
    pos => { lat.value = pos.coords.latitude; lng.value = pos.coords.longitude; locationText.value = `${lat.value.toFixed(5)}, ${lng.value.toFixed(5)}`; locating.value = false },
    () => { locationText.value = '定位失败，请允许定位权限'; locating.value = false },
    { enableHighAccuracy: true, timeout: 10000 }
  )
}

const takePhoto = () => {
  const input = document.createElement('input')
  input.type = 'file'; input.accept = 'image/*'; input.capture = 'environment'
  input.onchange = (e) => {
    const file = e.target.files[0]
    if (file) photoUrl.value = URL.createObjectURL(file)
  }
  input.click()
}

const submitCheckin = async () => {
  if (!photoUrl.value) return showToast('请先拍照')
  if (!lat.value) return showToast('请先定位')
  submitting.value = true
  try {
    await api.post('/visits/checkin', {
      customer_id: customerId.value,
      lat: lat.value, lng: lng.value,
      photo: photoUrl.value,
      remark: remark.value,
      purpose: purpose.value
    })
    showSuccessToast('打卡成功！')
    setTimeout(() => window.history.back(), 1000)
  } catch (e) {
    showToast(e.response?.data?.detail || '打卡失败')
  } finally { submitting.value = false }
}

onMounted(getLocation)
</script>

<style scoped>
.page { min-height: 100vh; background: #f7f8fa; padding-bottom: 20px; }
.content { padding: 12px; }
.customer-info { text-align: center; margin-bottom: 16px; }
.section { display: flex; align-items: center; gap: 10px; padding: 12px; background: #fff; border-radius: 10px; margin: 8px 0; font-size: 14px; color: #666; }
.section.radio-group { flex-wrap: wrap; }
.section-label { font-size: 14px; color: #333; margin-right: 4px; }
.photo-section { justify-content: center; padding: 20px; }
.photo-box {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  width: 200px; height: 200px; border: 2px dashed #ddd; border-radius: 12px;
  cursor: pointer; color: #ccc; font-size: 14px;
}
.photo-box img { width: 100%; height: 100%; object-fit: cover; border-radius: 10px; }
</style>
