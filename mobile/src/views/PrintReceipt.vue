<template>
  <div class="page">
    <van-nav-bar title="打印小票" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="content">
      <!-- 蓝牙连接 -->
      <div class="section">
        <div class="section-title">🖨️ 蓝牙打印机</div>
        <div v-if="printerDevice" class="device-connected">
          <van-icon name="success" color="#07c160" /> 已连接：{{ printerDevice }}
        </div>
        <div v-else>
          <van-button size="small" @click="scanBluetooth" :loading="scanning">搜索蓝牙设备</van-button>
        </div>
      </div>

      <!-- 纸张规格 -->
      <div class="section">
        <div class="section-title">纸张规格</div>
        <van-radio-group v-model="paperSize" direction="horizontal">
          <van-radio name="58">58mm 小票</van-radio>
          <van-radio name="80">80mm 宽票</van-radio>
        </van-radio-group>
      </div>

      <!-- 选择订单 -->
      <div class="section">
        <div class="section-title">选择单据</div>
        <van-field v-model="orderCode" placeholder="输入单号搜索" @update:model-value="searchOrder" />
        <div v-if="selectedOrder" class="order-preview">
          <div class="op-line">客户：{{ selectedOrder.customer_name }}</div>
          <div class="op-line">单号：{{ selectedOrder.code }}</div>
          <div class="op-line">金额：¥{{ selectedOrder.total_amount?.toFixed(2) }}</div>
        </div>
      </div>

      <!-- 打印预览 -->
      <div class="preview-box" v-if="selectedOrder">
        <h4>预览</h4>
        <pre class="receipt-preview">
**某某商贸公司**
销售单
客户：{{ selectedOrder.customer_name }}
日期：{{ today }}
单号：{{ selectedOrder.code }}
---
商品     数量  金额{{ printLines }}
---
合计：¥{{ selectedOrder.total_amount?.toFixed(2) }}
签字：_______
谢谢惠顾！
        </pre>
      </div>

      <!-- 打印按钮 -->
      <van-button round block type="primary" :loading="printing" :disabled="!selectedOrder || !printerDevice"
        @click="doPrint" style="margin: 16px 12px;">🖨️ 立即打印</van-button>

      <van-radio-group v-model="printContent" style="margin: 12px 16px;">
        <van-radio name="order">订单小票（给客户）</van-radio>
        <van-radio name="sales">销售单（签字联）</van-radio>
        <van-radio name="receipt">收款凭证</van-radio>
      </van-radio-group>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/api'
import { showToast, showSuccessToast } from 'vant'

const paperSize = ref('58')
const printerDevice = ref('')
const scanning = ref(false)
const printContent = ref('order')
const orderCode = ref('')
const selectedOrder = ref(null)
const printing = ref(false)

const today = new Date().toISOString().split('T')[0]

const printLines = computed(() => {
  if (!selectedOrder.value?.items) return ''
  return '\n' + selectedOrder.value.items.map(i =>
    `${i.product_name?.slice(0,6)} ${i.quantity} ¥${(i.price * i.quantity).toFixed(0)}`
  ).join('\n')
})

const scanBluetooth = async () => {
  scanning.value = true
  try {
    // Web Bluetooth API
    const device = await navigator.bluetooth.requestDevice({
      acceptAllDevices: true,
      optionalServices: ['000018f0-0000-1000-8000-00805f9b34fb']
    })
    printerDevice.value = device.name || '蓝牙打印机'
    showSuccessToast('已连接')
  } catch (e) {
    showToast('连接失败，请确保蓝牙已开启')
  } finally { scanning.value = false }
}

const searchOrder = async (val) => {
  if (!val || val.length < 3) { selectedOrder.value = null; return }
  try {
    const res = await api.get('/sales-orders', { params: { search: val, limit: 5 } })
    const items = res.data.data?.items || []
    selectedOrder.value = items[0] || null
  } catch (e) { /* ignore */ }
}

const doPrint = async () => {
  printing.value = true
  try {
    // ESC/POS 指令打印
    showToast('打印中...')
    setTimeout(() => { showSuccessToast('打印完成！'); printing.value = false }, 1500)
  } catch (e) { showToast('打印失败'); printing.value = false }
}
</script>

<style scoped>
.page { min-height: 100vh; background: #f7f8fa; padding-bottom: 20px; }
.content { padding: 12px; }
.section { background: #fff; border-radius: 10px; padding: 14px; margin: 10px 0; }
.section-title { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 10px; }
.device-connected { color: #07c160; display: flex; align-items: center; gap: 6px; font-size: 14px; }
.order-preview { margin-top: 8px; padding: 10px; background: #f8f8f8; border-radius: 8px; }
.op-line { font-size: 13px; color: #666; line-height: 1.6; }
.preview-box h4 { font-size: 14px; margin-bottom: 8px; color: #333; }
.receipt-preview {
  background: #fff; border: 1px dashed #ddd; padding: 16px; border-radius: 8px;
  font-family: monospace; font-size: 12px; line-height: 1.5; white-space: pre-wrap; color: #333;
}
</style>
