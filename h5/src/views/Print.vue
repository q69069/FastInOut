<template>
  <div class="print-page">
    <van-nav-bar title="打印小票" />
    <div class="content">
      <van-cell-group title="打印设置">
        <van-cell title="纸张规格">
          <template #extra>
            <van-radio-group v-model="paperSize" direction="horizontal">
              <van-radio name="58mm">58mm</van-radio>
              <van-radio name="80mm">80mm</van-radio>
            </van-radio-group>
          </template>
        </van-cell>
      </van-cell-group>
      <div style="padding: 20px;">
        <van-button type="primary" block :loading="loading" @click="handlePrint">开始打印</van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'

const paperSize = ref('80mm')
const loading = ref(false)

const handlePrint = async () => {
  loading.value = true
  try {
    showToast('打印功能开发中')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.print-page { background: #f7f8fa; min-height: 100vh; }
.content { padding-top: 12px; }
</style>