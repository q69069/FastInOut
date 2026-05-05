<template>
  <div class="page">
    <van-nav-bar title="报表中心" left-arrow @click-left="$router.back()" />

    <van-tabs v-model:active="tab" sticky>
      <van-tab title="销售报表">
        <div class="filter-bar">
          <van-cell title="时间范围" is-link :value="salesDateLabel" @click="showSalesDatePicker = true" />
          <van-cell title="分组方式">
            <template #extra>
              <van-picker :columns="groupByColumns" @change="onSalesGroupChange" style="width:100px" />
            </template>
          </van-cell>
        </div>
        <van-pull-refresh v-model="loading" @refresh="loadSales">
          <div v-for="item in salesData" :key="item.date" class="report-row">
            <span class="report-date">{{ item.date }}</span>
            <div class="report-stats">
              <div class="stat"><span class="lbl">订单</span><span class="val">{{ item.order_count }}</span></div>
              <div class="stat"><span class="lbl">销售额</span><span class="val primary">¥{{ (item.total_amount || 0).toFixed(0) }}</span></div>
              <div class="stat"><span class="lbl">成本</span><span class="val">¥{{ (item.cost_amount || 0).toFixed(0) }}</span></div>
              <div class="stat"><span class="lbl">利润</span><span :class="['val', item.profit >= 0 ? 'green' : 'red']">¥{{ (item.profit || 0).toFixed(0) }}</span></div>
            </div>
          </div>
          <van-empty v-if="salesData.length === 0 && !loading" description="暂无销售数据" />
        </van-pull-refresh>
      </van-tab>

      <van-tab title="采购报表">
        <div class="filter-bar">
          <van-cell title="时间范围" is-link :value="purchaseDateLabel" @click="showPurchaseDatePicker = true" />
        </div>
        <van-pull-refresh v-model="loading2" @refresh="loadPurchase">
          <div v-for="item in purchaseData" :key="item.date" class="report-row">
            <span class="report-date">{{ item.date }}</span>
            <div class="report-stats">
              <div class="stat"><span class="lbl">单数</span><span class="val">{{ item.order_count }}</span></div>
              <div class="stat"><span class="lbl">采购额</span><span class="val primary">¥{{ (item.total_amount || 0).toFixed(0) }}</span></div>
            </div>
          </div>
          <van-empty v-if="purchaseData.length === 0 && !loading2" description="暂无采购数据" />
        </van-pull-refresh>
      </van-tab>

      <van-tab title="趋势分析">
        <div class="filter-bar">
          <van-cell title="类型" is-link :value="trendTypeLabel" @click="showTrendTypePicker = true" />
          <van-cell title="周期" is-link :value="periodLabel" @click="showPeriodPicker = true" />
          <van-cell title="月份数">
            <template #extra>
              <van-stepper v-model="trendMonths" min="3" max="24" @change="loadTrend" />
            </template>
          </van-cell>
        </div>
        <div class="chart-placeholder">
          <div v-for="item in trendData" :key="item.period" class="trend-row">
            <span class="trend-period">{{ item.period }}</span>
            <div class="trend-bar-wrap">
              <div class="trend-bar" :style="{ width: getBarWidth(item.amount) + '%' }"></div>
            </div>
            <span class="trend-amount">¥{{ (item.amount || 0).toFixed(0) }}</span>
          </div>
        </div>
        <van-empty v-if="trendData.length === 0 && !loading3" description="暂无趋势数据" />
      </van-tab>

      <van-tab title="利润报表">
        <van-pull-refresh v-model="loading4" @refresh="loadProfit">
          <div class="profit-summary">
            <div class="p-item"><span class="p-label">总销售额</span><span class="p-val primary">¥{{ totalSalesAmount }}</span></div>
            <div class="p-item"><span class="p-label">总成本</span><span class="p-val">¥{{ totalCostAmount }}</span></div>
            <div class="p-item"><span class="p-label">总利润</span><span :class="['p-val', totalProfit >= 0 ? 'green' : 'red']">¥{{ totalProfit }}</span></div>
            <div class="p-item"><span class="p-label">毛利率</span><span :class="['p-val', grossRate >= 0 ? 'green' : 'red']">{{ grossRate }}%</span></div>
          </div>
          <div v-for="item in profitData" :key="item.date" class="report-row">
            <span class="report-date">{{ item.date }}</span>
            <div class="report-stats">
              <div class="stat"><span class="lbl">销售额</span><span class="val primary">¥{{ (item.sales_amount || 0).toFixed(0) }}</span></div>
              <div class="stat"><span class="lbl">成本</span><span class="val">¥{{ (item.cost_amount || 0).toFixed(0) }}</span></div>
              <div class="stat"><span class="lbl">利润</span><span :class="['val', item.profit >= 0 ? 'green' : 'red']">¥{{ (item.profit || 0).toFixed(0) }}</span></div>
              <div class="stat"><span class="lbl">毛利率</span><span :class="['val', (item.gross_rate || 0) >= 0 ? 'green' : 'red']">{{ (item.gross_rate || 0) }}%</span></div>
            </div>
          </div>
          <van-empty v-if="profitData.length === 0 && !loading4" description="暂无利润数据" />
        </van-pull-refresh>
      </van-tab>

      <van-tab title="销售明细">
        <div class="filter-bar">
          <van-cell title="时间范围" is-link :value="salesDetailDateLabel" @click="showSalesDetailDatePicker = true" />
          <van-cell title="分组">
            <template #extra>
              <van-picker :columns="detailGroupColumns" @change="onDetailGroupChange" style="width:100px" />
            </template>
          </van-cell>
        </div>
        <van-pull-refresh v-model="loading5" @refresh="loadSalesDetail">
          <div v-for="(item, idx) in salesDetailData" :key="idx" class="detail-row">
            <div class="detail-label">{{ item.label }}</div>
            <div class="detail-stats">
              <span>销量: {{ item.quantity }}</span>
              <span class="primary">¥{{ (item.amount || 0).toFixed(0) }}</span>
              <span>单数: {{ item.count }}</span>
            </div>
          </div>
          <van-empty v-if="salesDetailData.length === 0 && !loading5" description="暂无明细数据" />
        </van-pull-refresh>
      </van-tab>
    </van-tabs>

    <!-- Date Pickers -->
    <van-popup v-model:show="showSalesDatePicker" position="bottom" round>
      <van-date-picker v-model="salesDateRange" type="daterange" @confirm="onSalesDateConfirm" @cancel="showSalesDatePicker = false" />
    </van-popup>
    <van-popup v-model:show="showPurchaseDatePicker" position="bottom" round>
      <van-date-picker v-model="purchaseDateRange" type="daterange" @confirm="onPurchaseDateConfirm" @cancel="showPurchaseDatePicker = false" />
    </van-popup>
    <van-popup v-model:show="showSalesDetailDatePicker" position="bottom" round>
      <van-date-picker v-model="salesDetailDateRange" type="daterange" @confirm="onSalesDetailDateConfirm" @cancel="showSalesDetailDatePicker = false" />
    </van-popup>
    <van-popup v-model:show="showTrendTypePicker" position="bottom" round>
      <van-picker title="趋势类型" :columns="trendTypeColumns" @confirm="onTrendTypeConfirm" @cancel="showTrendTypePicker = false" />
    </van-popup>
    <van-popup v-model:show="showPeriodPicker" position="bottom" round>
      <van-picker title="周期" :columns="periodColumns" @confirm="onPeriodConfirm" @cancel="showPeriodPicker = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { showToast } from 'vant'
import { getSalesReport, getPurchaseReport, getTrendReport, getProfitReport, getSalesDetailReport } from '../api'

const tab = ref(0)
const loading = ref(false), loading2 = ref(false), loading3 = ref(false), loading4 = ref(false), loading5 = ref(false)

const salesData = ref([])
const purchaseData = ref([])
const trendData = ref([])
const profitData = ref([])
const salesDetailData = ref([])

// Sales filters
const salesDateRange = ref(['2024-01-01', '2026-12-31'])
const salesDateLabel = ref('全部时间')
const salesGroupBy = ref('day')
const groupByColumns = [
  { text: '按天', value: 'day' },
  { text: '按月', value: 'month' },
  { text: '按年', value: 'year' }
]

// Purchase filters
const purchaseDateRange = ref(['2024-01-01', '2026-12-31'])
const purchaseDateLabel = ref('全部时间')

// Trend filters
const trendType = ref('sales')
const trendMonths = ref(12)
const period = ref('month')
const trendTypeLabel = ref('销售趋势')
const periodLabel = ref('按月')
const trendTypeColumns = [
  { text: '销售趋势', value: 'sales' },
  { text: '采购趋势', value: 'purchase' }
]
const periodColumns = [
  { text: '按月', value: 'month' },
  { text: '按季度', value: 'quarter' }
]

// Sales Detail filters
const salesDetailDateRange = ref(['2024-01-01', '2026-12-31'])
const salesDetailDateLabel = ref('全部时间')
const detailGroup = ref('product')
const detailGroupColumns = [
  { text: '按商品', value: 'product' },
  { text: '按客户', value: 'customer' },
  { text: '按员工', value: 'employee' },
  { text: '按日期', value: 'date' }
]

// Pickers
const showSalesDatePicker = ref(false)
const showPurchaseDatePicker = ref(false)
const showSalesDetailDatePicker = ref(false)
const showTrendTypePicker = ref(false)
const showPeriodPicker = ref(false)

// Profit summary computed
const totalSalesAmount = computed(() => (profitData.value.reduce((s, i) => s + (i.sales_amount || 0), 0)).toFixed(0))
const totalCostAmount = computed(() => (profitData.value.reduce((s, i) => s + (i.cost_amount || 0), 0)).toFixed(0))
const totalProfit = computed(() => (profitData.value.reduce((s, i) => s + (i.profit || 0), 0)).toFixed(0))
const grossRate = computed(() => {
  const sales = parseFloat(totalSalesAmount.value) || 0
  if (sales === 0) return '0.00'
  return ((parseFloat(totalProfit.value) / sales) * 100).toFixed(2)
})

const maxTrendAmount = computed(() => Math.max(...trendData.value.map(i => i.amount || 0), 1))
const getBarWidth = (amount) => ((amount || 0) / maxTrendAmount.value * 100).toFixed(1)

const onSalesDateConfirm = ({ selectedValues }) => {
  salesDateLabel.value = selectedValues.join(' 至 ')
  showSalesDatePicker.value = false
  loadSales()
}
const onPurchaseDateConfirm = ({ selectedValues }) => {
  purchaseDateLabel.value = selectedValues.join(' 至 ')
  showPurchaseDatePicker.value = false
  loadPurchase()
}
const onSalesDetailDateConfirm = ({ selectedValues }) => {
  salesDetailDateLabel.value = selectedValues.join(' 至 ')
  showSalesDetailDatePicker.value = false
  loadSalesDetail()
}
const onSalesGroupChange = ({ selectedOptions }) => { salesGroupBy.value = selectedOptions[0].value; loadSales() }
const onDetailGroupChange = ({ selectedOptions }) => { detailGroup.value = selectedOptions[0].value; loadSalesDetail() }
const onTrendTypeConfirm = ({ selectedOptions }) => {
  trendType.value = selectedOptions[0].value
  trendTypeLabel.value = selectedOptions[0].text
  showTrendTypePicker.value = false
  loadTrend()
}
const onPeriodConfirm = ({ selectedOptions }) => {
  period.value = selectedOptions[0].value
  periodLabel.value = selectedOptions[0].text
  showPeriodPicker.value = false
  loadTrend()
}

const loadSales = async () => {
  loading.value = true
  try {
    const res = await getSalesReport({
      group_by: salesGroupBy.value,
      start_date: salesDateRange.value[0],
      end_date: salesDateRange.value[1]
    })
    salesData.value = res.data || []
  } catch {}
  loading.value = false
}

const loadPurchase = async () => {
  loading2.value = true
  try {
    const res = await getPurchaseReport({
      start_date: purchaseDateRange.value[0],
      end_date: purchaseDateRange.value[1]
    })
    purchaseData.value = res.data || []
  } catch {}
  loading2.value = false
}

const loadTrend = async () => {
  loading3.value = true
  try {
    const res = await getTrendReport({ trend_type: trendType.value, period: period.value, months: trendMonths.value })
    trendData.value = res.data || []
  } catch {}
  loading3.value = false
}

const loadProfit = async () => {
  loading4.value = true
  try {
    const res = await getProfitReport({ group_by: 'month' })
    profitData.value = res.data || []
  } catch {}
  loading4.value = false
}

const loadSalesDetail = async () => {
  loading5.value = true
  try {
    const res = await getSalesDetailReport({
      start_date: salesDetailDateRange.value[0],
      end_date: salesDetailDateRange.value[1],
      group_by: detailGroup.value
    })
    salesDetailData.value = res.data || []
  } catch {}
  loading5.value = false
}

// initial load
loadSales()
loadPurchase()
loadTrend()
loadProfit()
loadSalesDetail()
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.filter-bar { background: #fff; margin-bottom: 8px; }
.report-row { background: #fff; margin: 6px 16px; border-radius: 8px; padding: 12px; }
.report-date { font-weight: bold; font-size: 13px; color: #333; display: block; margin-bottom: 8px; }
.report-stats { display: flex; gap: 12px; }
.stat { display: flex; flex-direction: column; align-items: center; flex: 1; }
.stat .lbl { font-size: 10px; color: #999; }
.stat .val { font-size: 14px; font-weight: bold; color: #333; }
.stat .val.primary { color: #1989fa; }
.stat .val.green { color: #07c160; }
.stat .val.red { color: #ee0a24; }
.chart-placeholder { padding: 8px 16px; }
.trend-row { display: flex; align-items: center; margin-bottom: 12px; gap: 8px; }
.trend-period { font-size: 12px; color: #666; width: 70px; flex-shrink: 0; }
.trend-bar-wrap { flex: 1; background: #f0f0f0; border-radius: 4px; height: 20px; }
.trend-bar { background: linear-gradient(90deg, #1989fa, #396bec); height: 100%; border-radius: 4px; min-width: 4px; }
.trend-amount { font-size: 13px; font-weight: bold; color: #333; width: 80px; text-align: right; }
.profit-summary { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 12px 16px; }
.p-item { background: #fff; border-radius: 8px; padding: 12px; text-align: center; }
.p-label { font-size: 11px; color: #999; display: block; }
.p-val { font-size: 18px; font-weight: bold; display: block; }
.p-val.primary { color: #1989fa; }
.p-val.green { color: #07c160; }
.p-val.red { color: #ee0a24; }
.detail-row { background: #fff; margin: 6px 16px; border-radius: 8px; padding: 12px; }
.detail-label { font-weight: bold; font-size: 14px; color: #333; margin-bottom: 6px; }
.detail-stats { display: flex; gap: 16px; font-size: 13px; color: #666; }
.detail-stats .primary { color: #1989fa; font-weight: bold; }
</style>