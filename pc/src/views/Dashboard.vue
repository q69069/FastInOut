<template>
  <div>
    <el-row :gutter="20" style="margin-bottom:20px">
      <el-col :span="6" v-for="card in cards" :key="card.title">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" :style="{background: card.color}">
              <el-icon :size="28"><component :is="card.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-title">{{ card.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>待处理事项</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="库存预警数">
              <el-tag type="danger">{{ data.alert_count || 0 }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="本月订单数">{{ data.month_orders || 0 }}</el-descriptions-item>
            <el-descriptions-item label="客户数">{{ data.customer_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="供应商数">{{ data.supplier_count || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>今日经营</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="今日销售额">¥{{ formatNum(data.today_sales) }}</el-descriptions-item>
            <el-descriptions-item label="今日采购额">¥{{ formatNum(data.today_purchase) }}</el-descriptions-item>
            <el-descriptions-item label="今日回款">¥{{ formatNum(data.today_receipt) }}</el-descriptions-item>
            <el-descriptions-item label="今日付款">¥{{ formatNum(data.today_payment) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDashboard } from '../api'

const data = ref({})

const cards = computed(() => [
  { title: '今日销售额', value: `¥${formatNum(data.value.today_sales)}`, icon: 'TrendCharts', color: '#409EFF' },
  { title: '库存总量', value: formatNum(data.value.total_stock_qty), icon: 'Box', color: '#67C23A' },
  { title: '应收账款', value: `¥${formatNum(data.value.total_receivable)}`, icon: 'Money', color: '#E6A23C' },
  { title: '应付账款', value: `¥${formatNum(data.value.total_payable)}`, icon: 'Wallet', color: '#F56C6C' }
])

const formatNum = (n) => {
  if (!n) return '0.00'
  return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

onMounted(async () => {
  try {
    const res = await getDashboard()
    data.value = res.data || {}
  } catch (e) {}
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
}
.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 16px;
}
.stat-info {
  flex: 1;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}
.stat-title {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}
</style>
