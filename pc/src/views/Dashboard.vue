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

    <!-- 快捷模块 -->
    <el-card>
      <template #header>
        <div style="display:flex;align-items:center;justify-content:space-between">
          <span>快捷模块</span>
          <el-button size="small" @click="showEditDialog = true">
            <el-icon><Edit /></el-icon> 编辑
          </el-button>
        </div>
      </template>
      <div class="quick-actions">
        <div
          v-for="key in visibleModules"
          :key="key"
          class="qa-item"
          @click="navigate(key)"
        >
          <div class="qa-icon" :style="{background: MODULE_META[key].color}">
            <el-icon :size="20"><component :is="MODULE_META[key].icon" /></el-icon>
          </div>
          <div class="qa-label">{{ MODULE_META[key].label }}</div>
        </div>
      </div>
    </el-card>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑快捷模块" width="500px">
      <p style="color:#999;font-size:12px;margin-bottom:12px">
        点击模块可添加/移除，已按使用频率自动排序（点击越多次越靠前）
      </p>
      <el-checkbox-group v-model="selectedKeys" class="module-checkboxes">
        <el-row :gutter="8">
          <el-col :span="8" v-for="key in ALL_MODULE_KEYS" :key="key" style="margin-bottom:8px">
            <el-checkbox :value="key" :disabled="selectedKeys.length < 4 && selectedKeys.includes(key)">
              <div class="edit-module-item">
                <el-icon><component :is="MODULE_META[key].icon" /></el-icon>
                <span>{{ MODULE_META[key].label }}</span>
                <el-tag size="small" type="info" v-if="getUsageCount(key) > 0">{{ getUsageCount(key) }}次</el-tag>
              </div>
            </el-checkbox>
          </el-col>
        </el-row>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveModules">保存</el-button>
        <el-button @click="resetModules">重置默认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboard } from '../api'
import { MODULE_META, ALL_MODULE_KEYS, getModuleOrder, saveModuleOrder, recordModuleUsage } from '../utils/modulePrefs'
import { Edit } from '@element-plus/icons-vue'

const router = useRouter()
const data = ref({})
const showEditDialog = ref(false)
const selectedKeys = ref([])
const usageCount = ref({})

const visibleModules = computed(() => getModuleOrder().filter(k => selectedKeys.value.includes(k)))

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

const navigate = (key) => {
  recordModuleUsage(key)
  usageCount.value[key] = (usageCount.value[key] || 0) + 1
  router.push(MODULE_META[key].path)
}

const getUsageCount = (key) => {
  try {
    const raw = localStorage.getItem('home_module_prefs')
    if (!raw) return 0
    const prefs = JSON.parse(raw)
    return prefs.usageCount?.[key] || 0
  } catch { return 0 }
}

const saveModules = () => {
  saveModuleOrder(selectedKeys.value)
  showEditDialog.value = false
}

const resetModules = () => {
  selectedKeys.value = [...ALL_MODULE_KEYS]
}

onMounted(() => {
  // 加载数据
  getDashboard().then(res => { data.value = res.data || {} }).catch(() => {})
  // 加载当前选中模块
  selectedKeys.value = getModuleOrder().filter(k => ALL_MODULE_KEYS.includes(k))
  if (selectedKeys.value.length === 0) selectedKeys.value = [...ALL_MODULE_KEYS]
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
.module-checkboxes { display: block; }
.edit-module-item {
  display: flex; align-items: center; gap: 4px;
  font-size: 13px;
}
</style>
