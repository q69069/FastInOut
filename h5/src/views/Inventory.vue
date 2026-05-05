<template>
  <div class="page">
    <van-nav-bar title="库存查询" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="setting-o" size="20" @click="showFilter = !showFilter" />
      </template>
    </van-nav-bar>

    <!-- 筛选栏 -->
    <van-popup v-model:show="showFilter" position="top" round>
      <div style="padding:16px">
        <van-cell title="仓库筛选" is-link :value="selectedWhName || '全部仓库'" @click="showWhPicker = true" />
        <van-cell title="商品搜索" >
          <template #extra>
            <van-field v-model="keyword" placeholder="商品名称/编码" clearable style="width:180px" />
          </template>
        </van-cell>
        <div style="display:flex;gap:8px;margin-top:12px">
          <van-button size="small" block @click="showFilter = false">取消</van-button>
          <van-button type="primary" size="small" block @click="applyFilter">确定</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 汇总卡片 -->
    <div class="summary-bar">
      <div class="summary-item">
        <span class="summary-value">{{ totalQty }}</span>
        <span class="summary-label">总数量</span>
      </div>
      <div class="summary-item">
        <span class="summary-value orange">¥{{ totalValue }}</span>
        <span class="summary-label">总价值</span>
      </div>
      <div class="summary-item">
        <span class="summary-value green">{{ alertCount }}</span>
        <span class="summary-label">预警数</span>
      </div>
    </div>

    <!-- Tab切换：库存/流水/预警 -->
    <van-tabs v-model:active="tab" sticky>
      <van-tab title="库存列表">
        <van-pull-refresh v-model="refreshing" @refresh="loadInventory">
          <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="loadInventory">
            <div v-for="item in list" :key="item.id" class="inv-card" @click="showDetail(item)">
              <div class="inv-header">
                <span class="product-name">{{ item.product_name }}</span>
                <van-tag :type="getStockType(item)" size="small">{{ getStockLabel(item) }}</van-tag>
              </div>
              <div class="inv-meta">{{ item.product_code }} {{ item.product_spec ? '| ' + item.product_spec : '' }}</div>
              <div class="inv-stats">
                <div class="stat">
                  <span class="stat-label">仓库</span>
                  <span class="stat-val">{{ item.warehouse_name }}</span>
                </div>
                <div class="stat">
                  <span class="stat-label">库存</span>
                  <span :class="['stat-val', { danger: item.quantity <= 0 }]">{{ item.quantity }} {{ item.product_unit }}</span>
                </div>
                <div class="stat">
                  <span class="stat-label">成本价</span>
                  <span class="stat-val">¥{{ (item.cost_price || 0).toFixed(2) }}</span>
                </div>
                <div class="stat">
                  <span class="stat-label">库存值</span>
                  <span class="stat-val">¥{{ (item.total_value || 0).toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </van-list>
        </van-pull-refresh>
      </van-tab>

      <van-tab title="库流水">
        <div style="padding:8px 16px">
          <van-cell title="仓库" is-link :value="selectedWhName || '全部'" @click="showWhPicker2 = true" style="margin-bottom:8px" />
          <van-cell title="类型">
            <template #extra>
              <van-picker :columns="flowTypeColumns" @confirm="onFlowTypeConfirm" style="width:120px" />
            </template>
          </van-cell>
        </div>
        <van-pull-refresh v-model="flowRefreshing" @refresh="loadFlow">
          <van-list v-model:loading="flowLoading" :finished="flowFinished" finished-text="没有更多了" @load="loadFlow">
            <div v-for="r in flowList" :key="r.id + r.type" class="flow-card">
              <div class="flow-header">
                <span :class="['flow-type', r.quantity >= 0 ? 'in' : 'out']">{{ getFlowTypeLabel(r.type) }}</span>
                <span class="flow-qty" :style="{ color: r.quantity >= 0 ? '#07c160' : '#ee0a24' }">
                  {{ r.quantity >= 0 ? '+' : '' }}{{ r.quantity }}
                </span>
              </div>
              <div class="flow-info">
                <span>{{ r.product_name }}</span>
                <span>{{ r.created_at?.substring(0, 16) }}</span>
              </div>
              <div class="flow-info">{{ r.reason || '' }} {{ r.code || '' }}</div>
            </div>
          </van-list>
        </van-pull-refresh>
      </van-tab>

      <van-tab title="库存预警">
        <van-pull-refresh v-model="alertRefreshing" @refresh="loadAlerts">
          <van-list v-model:loading="alertLoading" :finished="alertFinished" finished-text="没有更多了" @load="loadAlerts">
            <div v-for="a in alertList" :key="a.id" class="alert-card">
              <div class="alert-header">
                <span style="font-weight:bold">{{ a.product_name }}</span>
                <van-tag :type="a.alert_type === 'low' ? 'danger' : 'warning'">
                  {{ a.alert_type === 'low' ? '库存不足' : '库存积压' }}
                </van-tag>
              </div>
              <div class="alert-info">
                <span>当前: {{ a.current_qty }}</span>
                <span>下限: {{ a.min_qty }}</span>
                <span>上限: {{ a.max_qty }}</span>
              </div>
              <div class="alert-footer">
                <span>{{ a.created_at?.substring(0, 10) }}</span>
                <van-tag :type="a.is_handled ? 'success' : 'default'" size="small">{{ a.is_handled ? '已处理' : '未处理' }}</van-tag>
              </div>
            </div>
            <van-empty v-if="alertList.length === 0 && !alertLoading" description="暂无预警" />
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>

    <!-- 仓库选择 -->
    <van-popup v-model:show="showWhPicker" position="bottom" round>
      <van-picker title="选择仓库" :columns="whColumns" @confirm="onWhConfirm" @cancel="showWhPicker = false" />
    </van-popup>
    <van-popup v-model:show="showWhPicker2" position="bottom" round>
      <van-picker title="选择仓库" :columns="whColumns" @confirm="onWhConfirm2" @cancel="showWhPicker2 = false" />
    </van-popup>

    <!-- 库存详情 -->
    <van-popup v-model:show="showDetailPopup" position="bottom" round style="max-height:60%">
      <div style="padding:16px" v-if="detailItem">
        <h3>{{ detailItem.product_name }}</h3>
        <van-cell-group style="margin-top:12px">
          <van-cell title="仓库" :value="detailItem.warehouse_name" />
          <van-cell title="编码" :value="detailItem.product_code" />
          <van-cell title="规格" :value="detailItem.product_spec || '-'" />
          <van-cell title="单位" :value="detailItem.product_unit" />
          <van-cell title="当前库存" :value="detailItem.quantity + ' ' + detailItem.product_unit" />
          <van-cell title="成本价" :value="'¥' + (detailItem.cost_price || 0).toFixed(2)" />
          <van-cell title="库存价值" :value="'¥' + (detailItem.total_value || 0).toFixed(2)" />
        </van-cell-group>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast } from 'vant'
import { getInventory, getInventoryFlow, getInventoryAlerts, getWarehouses } from '../api'

const tab = ref(0)
const showFilter = ref(false)
const showWhPicker = ref(false)
const showWhPicker2 = ref(false)
const selectedWhId = ref(null)
const selectedWhName = ref('')
const selectedWhId2 = ref(null)
const keyword = ref('')
const list = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)

const flowList = ref([])
const flowLoading = ref(false)
const flowFinished = ref(false)
const flowRefreshing = ref(false)
const flowPage = ref(1)
const flowType = ref('')
const flowTypeColumns = [
  { text: '全部', value: '' },
  { text: '采购入库', value: 'purchase_in' },
  { text: '采购退货', value: 'purchase_return' },
  { text: '销售出库', value: 'sales_out' },
  { text: '销售退货', value: 'sales_return' },
  { text: '调拨', value: 'transfer' },
  { text: '其他', value: 'other' }
]

const alertList = ref([])
const alertLoading = ref(false)
const alertFinished = ref(false)
const alertRefreshing = ref(false)
const alertPage = ref(1)

const warehouses = ref([])
const showDetailPopup = ref(false)
const detailItem = ref(null)
const alertCount = ref(0)

const whColumns = computed(() => [
  { text: '全部仓库', value: null },
  ...warehouses.value.map(w => ({ text: w.name, value: w.id }))
])

const totalQty = computed(() => Math.round(list.value.reduce((s, i) => s + (i.quantity || 0), 0)))
const totalValue = computed(() => list.value.reduce((s, i) => s + (i.total_value || 0), 0).toFixed(2))

const getStockType = (item) => {
  if (!item.min_stock && !item.max_stock) return 'success'
  if (item.quantity <= 0) return 'danger'
  if (item.quantity <= (item.min_stock || 0) * 0.5) return 'danger'
  if (item.quantity <= item.min_stock || item.quantity > (item.max_stock || Infinity)) return 'warning'
  return 'success'
}

const getStockLabel = (item) => {
  if (item.quantity <= 0) return '已清零'
  if (item.quantity <= (item.min_stock || 0)) return '库存低'
  if (item.quantity > (item.max_stock || Infinity)) return '超上限'
  return '正常'
}

const getFlowTypeLabel = (type) => {
  const map = {
    purchase_in: '采购入库', purchase_return: '采购退货',
    sales_out: '销售出库', sales_return: '销售退货',
    transfer_out: '调拨出库', transfer_in: '调拨入库',
    other_in: '其他入库', other_out: '其他出库'
  }
  return map[type] || type
}

const loadInventory = async () => {
  try {
    const res = await getInventory({ page: page.value, page_size: 20, warehouse_id: selectedWhId.value, keyword: keyword.value })
    if (page.value === 1) list.value = res.data || []
    else list.value.push(...(res.data || []))
    finished.value = (res.data || []).length < 20
    page.value++
  } catch {}
  loading.value = false
  refreshing.value = false
}

const loadFlow = async () => {
  try {
    const res = await getInventoryFlow({ page: flowPage.value, page_size: 20, warehouse_id: selectedWhId2.value, flow_type: flowType.value })
    if (flowPage.value === 1) flowList.value = res.data || []
    else flowList.value.push(...(res.data || []))
    flowFinished.value = (res.data || []).length < 20
    flowPage.value++
  } catch {}
  flowLoading.value = false
  flowRefreshing.value = false
}

const loadAlerts = async () => {
  try {
    const res = await getInventoryAlerts({ is_handled: 0, page_size: 50 })
    alertList.value = res.data || []
    alertCount.value = (res.data || []).length
  } catch {}
  alertLoading.value = false
  alertRefreshing.value = false
  alertFinished.value = true
}

const onWhConfirm = ({ selectedOptions }) => {
  selectedWhId.value = selectedOptions[0].value
  selectedWhName.value = selectedOptions[0].text === '全部仓库' ? '' : selectedOptions[0].text
  showWhPicker.value = false
}

const onWhConfirm2 = ({ selectedOptions }) => {
  selectedWhId2.value = selectedOptions[0].value
  showWhPicker2.value = false
  flowPage.value = 1; loadFlow()
}

const onFlowTypeConfirm = ({ selectedOptions }) => {
  flowType.value = selectedOptions.value
  flowPage.value = 1; loadFlow()
}

const applyFilter = () => {
  showFilter.value = false
  page.value = 1; loadInventory()
}

const showDetail = (item) => {
  detailItem.value = item
  showDetailPopup.value = true
}

onMounted(async () => {
  const res = await getWarehouses()
  warehouses.value = res.data || []
  loadInventory()
  loadAlerts()
})
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; }
.summary-bar {
  display: flex; background: linear-gradient(135deg, #1989fa, #396bec);
  margin: 8px 16px; border-radius: 12px; padding: 14px; color: #fff;
}
.summary-item { flex: 1; text-align: center; }
.summary-value { font-size: 22px; font-weight: bold; display: block; }
.summary-label { font-size: 11px; opacity: 0.9; }
.orange { color: #ff9a56; }
.green { color: #07c160; }
.inv-card {
  background: #fff; margin: 8px 16px; border-radius: 10px;
  padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.inv-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.product-name { font-size: 15px; font-weight: bold; color: #333; }
.inv-meta { font-size: 12px; color: #999; margin-bottom: 8px; }
.inv-stats { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px; }
.stat { display: flex; flex-direction: column; }
.stat-label { font-size: 10px; color: #999; }
.stat-val { font-size: 13px; font-weight: bold; color: #333; }
.danger { color: #ee0a24; }
.flow-card {
  background: #fff; margin: 6px 16px; border-radius: 8px;
  padding: 10px 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.flow-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.flow-type { font-size: 12px; padding: 2px 8px; border-radius: 4px; }
.flow-type.in { background: #e6f7ed; color: #07c160; }
.flow-type.out { background: #fff0f0; color: #ee0a24; }
.flow-qty { font-size: 16px; font-weight: bold; }
.flow-info { display: flex; justify-content: space-between; font-size: 12px; color: #666; }
.alert-card {
  background: #fff; margin: 8px 16px; border-radius: 8px;
  padding: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.alert-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.alert-info { display: flex; gap: 16px; font-size: 13px; color: #666; margin-bottom: 6px; }
.alert-footer { display: flex; justify-content: space-between; font-size: 12px; color: #999; }
</style>
