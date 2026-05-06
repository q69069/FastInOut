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
    <el-row :gutter="20" style="margin-bottom:20px">
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
            <el-descriptions-item label="今日销售额">¥{{ fmt(data.today_sales) }}</el-descriptions-item>
            <el-descriptions-item label="今日采购额">¥{{ fmt(data.today_purchase) }}</el-descriptions-item>
            <el-descriptions-item label="今日回款">¥{{ fmt(data.today_receipt) }}</el-descriptions-item>
            <el-descriptions-item label="今日付款">¥{{ fmt(data.today_payment) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>快捷操作</template>
          <div class="quick-actions">
            <div v-for="a in quickActions" :key="a.path" class="qa-item" @click="router.push(a.path)">
              <div class="qa-icon" :style="{background: a.color}">
                <el-icon :size="20"><component :is="a.icon" /></el-icon>
              </div>
              <div class="qa-label">{{ a.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboard } from '../api'

const router = useRouter()
const data = ref({})

const fmt = (n) => {
  if (!n && n !== 0) return '0.00'
  return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

const cards = computed(() => [
  { title: '今日销售额', value: `¥${fmt(data.value.today_sales)}`, icon: 'TrendCharts', color: '#409EFF' },
  { title: '库存总量', value: fmt(data.value.total_stock_qty), icon: 'Box', color: '#67C23A' },
  { title: '应收账款', value: `¥${fmt(data.value.total_receivable)}`, icon: 'Money', color: '#E6A23C' },
  { title: '应付账款', value: `¥${fmt(data.value.total_payable)}`, icon: 'Wallet', color: '#F56C6C' }
])

const quickActions = [
  { label: '销售开单', path: '/sales', icon: 'Sell', color: '#409EFF' },
  { label: '采购开单', path: '/purchases', icon: 'ShoppingCart', color: '#67C23A' },
  { label: '库存查询', path: '/inventory', icon: 'Box', color: '#E6A23C' },
  { label: '客户管理', path: '/customers', icon: 'User', color: '#F56C6C' },
  { label: '供应商管理', path: '/suppliers', icon: 'Shop', color: '#909399' },
  { label: '费用报销', path: '/expense', icon: 'Finance', color: '#9c27b0' },
  { label: '收款登记', path: '/finance', icon: 'Money', color: '#07c160' },
  { label: '报表统计', path: '/reports/profit', icon: 'DataAnalysis', color: '#00bcd4' },
]

onMounted(async () => {
  try {
    const res = await getDashboard()
    data.value = res.data || {}
  } catch {}
})
</script>

<style scoped>
.stat-card { display: flex; align-items: center; }
.stat-icon {
  width: 56px; height: 56px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; margin-right: 16px;
}
.stat-info { flex: 1; }
.stat-value { font-size: 24px; font-weight: bold; color: #333; }
.stat-title { font-size: 14px; color: #999; margin-top: 4px; }
.quick-actions { display: flex; flex-wrap: wrap; gap: 12px; }
.qa-item {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  width: 80px; cursor: pointer; padding: 10px 4px; border-radius: 8px;
  transition: background 0.2s;
}
.qa-item:hover { background: #f5f7fa; }
.qa-icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; color: #fff;
}
.qa-label { font-size: 12px; color: #666; }
</style>
