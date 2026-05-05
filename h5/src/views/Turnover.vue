<template>
  <div class="page">
    <van-nav-bar title="周转率分析" left-arrow @click-left="$router.back()" />

    <div class="filter-bar">
      <van-cell title="仓库" is-link :value="whName || '全部仓库'" @click="showWhPicker = true" />
    </div>

    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadData">
        <div v-for="item in list" :key="item.product_id" class="turn-card">
          <div class="turn-header">
            <span class="product-name">{{ item.product_name }}</span>
            <van-tag :type="item.turnover_rate >= 2 ? 'success' : item.turnover_rate >= 1 ? 'warning' : 'danger'" size="small">
              {{ item.turnover_rate.toFixed(2) }}次
            </van-tag>
          </div>
          <div class="turn-stats">
            <div class="stat">
              <span class="s-val">{{ item.total_out }}</span>
              <span class="s-lbl">总出库</span>
            </div>
            <div class="stat">
              <span class="s-val">{{ item.avg_stock.toFixed(0) }}</span>
              <span class="s-lbl">平均库存</span>
            </div>
            <div class="stat">
              <span class="s-val">{{ item.days }}</span>
              <span class="s-lbl">分析天数</span>
            </div>
            <div class="stat">
              <span class="s-val red">{{ item.turnover_rate >= 2 ? '优秀' : item.turnover_rate >= 1 ? '一般' : '偏低' }}</span>
              <span class="s-lbl">评价</span>
            </div>
          </div>
        </div>
        <van-empty v-if="list.length === 0 && !loading" description="暂无周转数据" />
      </van-list>
    </van-pull-refresh>

    <van-popup v-model:show="showWhPicker" position="bottom" round>
      <van-picker title="选择仓库" :columns="whColumns" @confirm="onWhConfirm" @cancel="showWhPicker = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getWarehouses, getTurnover } from '../api'

const loading = ref(false)
const finished = ref(false)
const list = ref([])
const warehouses = ref([])
const selectedWhId = ref(null)
const whName = ref('')
const showWhPicker = ref(false)
const startDate = ref('2024-01-01')
const endDate = ref('2026-12-31')

const whColumns = computed(() => [
  { text: '全部仓库', value: null },
  ...warehouses.value.map(w => ({ text: w.name, value: w.id }))
])

const loadData = async () => {
  loading.value = true
  try {
    const res = await getTurnover({
      start_date: startDate.value,
      end_date: endDate.value,
      warehouse_id: selectedWhId.value,
      per_product: 1
    })
    list.value = res.data || []
  } catch {
    list.value = []
  }
  loading.value = false
  finished.value = true
}

const onWhConfirm = ({ selectedOptions }) => {
  selectedWhId.value = selectedOptions[0].value
  whName.value = selectedOptions[0].text === '全部仓库' ? '' : selectedOptions[0].text
  showWhPicker.value = false
  loadData()
}

onMounted(async () => {
  const whRes = await getWarehouses()
  warehouses.value = whRes.data || []
  loadData()
})
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.filter-bar { background: #fff; margin-bottom: 8px; }
.turn-card { background: #fff; margin: 8px 16px; border-radius: 10px; padding: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.turn-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.product-name { font-size: 14px; font-weight: bold; color: #333; }
.turn-stats { display: flex; gap: 12px; }
.stat { display: flex; flex-direction: column; align-items: center; flex: 1; }
.s-val { font-size: 14px; font-weight: bold; color: #333; }
.s-val.red { color: #ee0a24; }
.s-lbl { font-size: 11px; color: #999; margin-top: 2px; }
</style>