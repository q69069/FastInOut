<template>
  <div class="print-page">
    <van-cell-group inset>
      <van-field v-model="form.order_id" label="单号" placeholder="输入销售单号" />
      <van-field v-model="form.template_id" label="模板" placeholder="选择打印模板" readonly @click="showTemplate = true" />
    </van-cell-group>
    <div style="margin:16px">
      <van-button round block type="primary" @click="handlePrint" :loading="loading">
        打印预览
      </van-button>
    </div>
    <van-popup v-model:show="showPreview" position="bottom" style="height:80%">
      <iframe :src="previewUrl" style="width:100%;height:100%;border:none" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'
import { previewPrint } from '../api'

const form = ref({ order_id: '', template_id: 1 })
const loading = ref(false)
const showPreview = ref(false)
const previewUrl = ref('')
const showTemplate = ref(false)

const handlePrint = async () => {
  if (!form.value.order_id) return showToast('请输入单号')
  loading.value = true
  try {
    previewUrl.value = `/api/print-templates/${form.value.template_id}/preview/sales/${form.value.order_id}`
    showPreview.value = true
  } catch (e) {
    showToast('预览失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.print-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-top: 16px;
}
</style>
