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
          <el-button size="small" @click="openEdit">
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
    <el-dialog v-model="showEditDialog" title="编辑快捷模块" width="560px">
      <p style="color:#999;font-size:12px;margin-bottom:12px">
        已按使用频率排序，最多选12个模块（至少选4个）
      </p>
      <div class="edit-list">
        <div
          v-for="key in ALL_MODULE_KEYS"
          :key="key"
          class="edit-row"
          :class="{ dimmed: !draftKeys.includes(key) }"
        >
          <el-checkbox
            :model-value="draftKeys.includes(key)"
            :disabled="draftKeys.length >= 12 && !draftKeys.includes(key)"
            @change="toggleDraft(key)"
          />
          <div class="edit-icon" :style="{background: MODULE_META[key].color}">
            <el-icon :size="14"><component :is="MODULE_META[key].icon" /></el-icon>
          </div>
          <span class="edit-label">{{ MODULE_META[key].label }}</span>
          <span class="edit-usage" v-if="getUsageCount(key) > 0">{{ getUsageCount(key) }}次</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" @click="confirmSave">保存</el-button>
        <el-button @click="resetToDefault">重置默认</el-button>
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
const draftKeys = ref([])
const savedKeys = ref([])

const visibleModules = computed(() =>
  getModuleOrder().filter(k => savedKeys.value.includes(k))
)

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
  router.push(MODULE_META[key].path)
}

const getUsageCount = (key) => {
  try {
    const raw = localStorage.getItem('pc_home_module_prefs')
    if (!raw) return 0
    return JSON.parse(raw).usageCount?.[key] || 0
  } catch { return 0 }
}

const openEdit = () => {
  draftKeys.value = [...visibleModules.value]
  showEditDialog.value = true
}

const cancelEdit = () => {
  showEditDialog.value = false
}

const toggleDraft = (key) => {
  const idx = draftKeys.value.indexOf(key)
  if (idx >= 0) {
    if (draftKeys.value.length > 4) draftKeys.value.splice(idx, 1)
  } else if (draftKeys.value.length < 12) {
    draftKeys.value.push(key)
  }
}

const confirmSave = () => {
  saveModuleOrder(draftKeys.value)
  savedKeys.value = [...draftKeys.value]
  showEditDialog.value = false
}

const resetToDefault = () => {
  draftKeys.value = [...ALL_MODULE_KEYS]
}

onMounted(() => {
  getDashboard().then(res => { data.value = res.data || {} }).catch(() => {})
  savedKeys.value = getModuleOrder().filter(k => ALL_MODULE_KEYS.includes(k))
  if (savedKeys.value.length === 0) savedKeys.value = [...ALL_MODULE_KEYS]
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
.edit-list { max-height: 400px; overflow-y: auto; }
.edit-row {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 4px; border-radius: 6px; transition: background 0.15s;
}
.edit-row:hover { background: #f5f7fa; }
.edit-row.dimmed { opacity: 0.5; }
.edit-icon {
  width: 28px; height: 28px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; color: #fff;
  flex-shrink: 0;
}
.edit-label { flex: 1; font-size: 13px; color: #333; }
.edit-usage { font-size: 11px; color: #999; background: #f5f5f5; padding: 1px 6px; border-radius: 10px; }
</style>
