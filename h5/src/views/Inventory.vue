<template>
  <div class="inventory-page">
    <van-nav-bar title="库存查询" />
    <van-search v-model="keyword" placeholder="搜索商品名称/编码" @search="loadData" />

    <!-- 库存汇总 -->
    <div class="summary-bar">
      <div class="summary-item">
        <span class="summary-value">{{ totalQty }}</span>
        <span class="summary-label">总数量</span>
      </div>
      <div class="summary-item">
        <span class="summary-value orange">¥{{ totalValue }}</span>
        <span class="summary-label">总价值</span>
      </div>
    </div>

    <!-- 库存列表 -->
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadData">
        <div v-for="item in list" :key="item.id" class="inventory-card">
          <div class="inventory-header">
            <div class="product-name">{{ item.product_name }}</div>
            <van-tag :type="getStockType(item.quantity, item.min_stock)" size="small">
              {{ getStockStatus(item.quantity, item.min_stock) }}
            </van-tag>
          </div>
          <div class="product-detail">
            <span>编码: {{ item.product_code }}</span>
            <span>规格: {{ item.product_spec || '-' }}</span>
          </div>
          <div class="inventory-stats">
            <div class="stat-item">
              <span class="stat-label">仓库</span>
              <span class="stat-value">{{ item.warehouse_name }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">库存</span>
              <span :class="['stat-value', { red: item.quantity <= item.min_stock }]">
                {{ item.quantity }} {{ item.product_unit }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">成本</span>
              <span class="stat-value">¥{{ item.cost_price || 0 }}</span>
            </div>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getInventory } from '../api'

const list = ref([])
const loading = ref(false)
const finished = ref(false)
const keyword = ref('')

const totalQty = computed(() => {
  const sum = list.value.reduce((acc, item) => acc + (item.quantity || 0), 0)
  return Math.round(sum)
})

const totalValue = computed(() => {
  const sum = list.value.reduce((acc, item) => acc + (item.total_value || 0), 0)
  return sum.toFixed(2)
})

const getStockType = (qty, minStock) => {
  if (!minStock) return 'success'
  if (qty <= minStock * 0.5) return 'danger'
  if (qty <= minStock) return 'warning'
  return 'success'
}

const getStockStatus = (qty, minStock) => {
  if (!minStock) return '充足'
  if (qty <= minStock * 0.5) return '紧急'
  if (qty <= minStock) return '预警'
  return '充足'
}

const loadData = async () => {
  try {
    const res = await getInventory({ keyword: keyword.value })
    list.value = res.data || []
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
    finished.value = true
  }
}

onMounted(loadData)
</script>

<style scoped>
.inventory-page { background: #f7f8fa; min-height: 100vh; }
.summary-bar {
  display: flex;
  background: linear-gradient(135deg, #1989fa, #396bec);
  margin: 0 12px;
  border-radius: 12px;
  padding: 16px;
  color: #fff;
}
.summary-item { flex: 1; text-align: center; }
.summary-value { font-size: 24px; font-weight: bold; display: block; }
.summary-label { font-size: 12px; opacity: 0.9; }
.orange { color: #ff9a56; }
.inventory-card {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  padding: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.inventory-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.product-name { font-size: 15px; font-weight: bold; color: #333; }
.product-detail { display: flex; gap: 12px; font-size: 12px; color: #999; margin-bottom: 10px; }
.inventory-stats { display: flex; justify-content: space-between; }
.stat-item { display: flex; flex-direction: column; gap: 2px; }
.stat-label { font-size: 11px; color: #999; }
.stat-value { font-size: 14px; font-weight: bold; color: #333; }
.red { color: #ee0a24; }
</style>