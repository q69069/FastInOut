<template>
  <div class="print-page">
    <van-nav-bar title="打印小票" left-arrow @click-left="$router.back()" />

    <!-- 订单信息 -->
    <div class="order-info" v-if="orderData">
      <div class="shop-name">FastInOut 门店</div>
      <div class="divider-line">------------------------</div>
      <div class="info-row">单号: {{ orderData.order_no }}</div>
      <div class="info-row">日期: {{ orderData.date }}</div>
      <div class="info-row">客户: {{ orderData.customer_name }}</div>
      <div class="divider-line">------------------------</div>

      <!-- 商品明细 -->
      <div class="items-header">商品明细</div>
      <div class="item-row" v-for="item in orderData.items" :key="item.id">
        <div class="item-left">
          <span class="item-name">{{ item.name }}</span>
          <span class="item-qty">x{{ item.quantity }}</span>
        </div>
        <div class="item-right">¥{{ item.price }}</div>
      </div>
      <div class="divider-line">------------------------</div>

      <!-- 金额汇总 -->
      <div class="amount-row">
        <span>商品数量</span>
        <span>{{ orderData.total_qty }} 件</span>
      </div>
      <div class="amount-row">
        <span>订单金额</span>
        <span>¥{{ orderData.total_amount }}</span>
      </div>
      <div class="amount-row" v-if="orderData.discount > 0">
        <span>整单折扣</span>
        <span>-¥{{ orderData.discount }}</span>
      </div>
      <div class="amount-row total">
        <span>合计</span>
        <span>¥{{ orderData.final_amount }}</span>
      </div>
      <div class="divider-line">------------------------</div>

      <!-- 备注 -->
      <div class="info-row" v-if="orderData.remark">备注: {{ orderData.remark }}</div>
      <div class="footer">谢谢惠顾，欢迎下次光临！</div>
    </div>

    <!-- 打印设置 -->
    <van-cell-group inset title="打印设置">
      <van-cell title="纸张规格">
        <template #extra>
          <van-radio-group v-model="paperSize" direction="horizontal">
            <van-radio name="58mm">58mm</van-radio>
            <van-radio name="80mm">80mm</van-radio>
          </van-radio-group>
        </template>
      </van-cell>
      <van-cell title="打印份数">
        <template #extra>
          <van-stepper v-model="copies" min="1" max="5" />
        </template>
      </van-cell>
    </van-cell-group>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <van-button type="primary" block :loading="loading" @click="handlePrint">确认打印</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import { useRoute } from 'vue-router'
import { getSalesOrders } from '../api'

const route = useRoute()
const paperSize = ref('80mm')
const copies = ref(1)
const loading = ref(false)
const orderData = ref(null)

onMounted(async () => {
  const orderId = route.query.order_id
  if (orderId) {
    try {
      const res = await getSalesOrders({ id: orderId })
      if (res.data?.length > 0) {
        const order = res.data[0]
        orderData.value = {
          order_no: order.id,
          date: order.created_at?.split('T')[0] || new Date().toISOString().split('T')[0],
          customer_name: order.customer_name || '客户',
          items: order.items || [],
          total_qty: order.items?.reduce((s, i) => s + i.quantity, 0) || 0,
          total_amount: order.total_amount || 0,
          discount: order.discount || 0,
          final_amount: order.final_amount || order.total_amount || 0,
          remark: order.remark || ''
        }
      }
    } catch (e) {
      // 使用模拟数据
      orderData.value = {
        order_no: 'SO' + Date.now(),
        date: new Date().toISOString().split('T')[0],
        customer_name: '测试客户',
        items: [
          { id: 1, name: '商品A', quantity: 2, price: 10.00 },
          { id: 2, name: '商品B', quantity: 1, price: 25.00 }
        ],
        total_qty: 3,
        total_amount: 45.00,
        discount: 0,
        final_amount: 45.00,
        remark: ''
      }
    }
  } else {
    // 模拟数据
    orderData.value = {
      order_no: 'SO' + Date.now(),
      date: new Date().toISOString().split('T')[0],
      customer_name: '测试客户',
      items: [
        { id: 1, name: '商品A', quantity: 2, price: 10.00 },
        { id: 2, name: '商品B', quantity: 1, price: 25.00 }
      ],
      total_qty: 3,
      total_amount: 45.00,
      discount: 0,
      final_amount: 45.00,
      remark: ''
    }
  }
})

const handlePrint = async () => {
  if (!orderData.value) {
    showToast('无打印数据')
    return
  }
  loading.value = true
  try {
    // 调用浏览器打印
    const printContent = document.querySelector('.order-info')
    if (printContent) {
      const printWindow = window.open('', '_blank')
      printWindow.document.write('<html><head><title>打印小票</title>')
      printWindow.document.write('<style>')
      printWindow.document.write('body { font-family: monospace; font-size: 12px; padding: 10px; }')
      printWindow.document.write('.divider-line { margin: 8px 0; }')
      printWindow.document.write('</style>')
      printWindow.document.write('</head><body>')
      printWindow.document.write(printContent.innerHTML)
      printWindow.document.write('</body></html>')
      printWindow.document.close()
      printWindow.print()
    }
    showSuccessToast('已发送打印')
  } catch (e) {
    showToast('打印失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.print-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 80px; }
.order-info {
  background: #fff;
  margin: 12px;
  padding: 16px;
  border-radius: 12px;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.8;
}
.shop-name { font-size: 16px; font-weight: bold; text-align: center; margin-bottom: 8px; }
.divider-line { color: #999; }
.info-row { display: flex; justify-content: space-between; }
.items-header { font-weight: bold; margin: 8px 0; }
.item-row { display: flex; justify-content: space-between; padding: 4px 0; }
.item-left { display: flex; gap: 8px; }
.item-name { max-width: 150px; }
.item-qty { color: #999; }
.item-right { text-align: right; }
.amount-row { display: flex; justify-content: space-between; padding: 4px 0; }
.amount-row.total { font-weight: bold; font-size: 15px; margin-top: 8px; }
.footer { text-align: center; margin-top: 12px; color: #666; }
.action-bar { position: fixed; bottom: 50px; left: 0; right: 0; background: #fff; padding: 12px 16px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
</style>