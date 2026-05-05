<template>
  <div class="page">
    <van-nav-bar title="其他出入库" left-arrow @click-left="$router.back()" />

    <!-- 其他出库列表 -->
    <div v-if="!showCreate">
      <van-tabs v-model:active="tab" sticky>
        <van-tab title="其他出库">
          <div style="padding:8px 16px 0">
            <van-cell-group inset>
              <van-cell title="仓库" is-link :value="queryWhName || '全部'" @click="showWhPicker = true" />
              <van-cell>
                <template #title>原因筛选</template>
                <template #extra>
                  <van-picker :columns="reasonColumns" @confirm="onReasonConfirm" style="width:120px" />
                </template>
              </van-cell>
            </van-cell-group>
          </div>
          <van-pull-refresh v-model="refreshing" @refresh="loadData('out')">
            <van-list :loading="loading" :finished="finished" finished-text="没有更多了" @load="loadData('out')">
              <div v-for="r in records" :key="r.id" class="record-card">
                <div class="record-header">
                  <van-tag type="danger">其他出库</van-tag>
                  <span class="record-qty">-{{ r.quantity }}</span>
                </div>
                <div class="record-info">
                  <span>{{ r.product_name }}</span>
                  <span>{{ r.created_at?.substring(0, 16) }}</span>
                </div>
                <div class="record-reason">{{ r.reason || '' }}</div>
              </div>
              <van-empty v-if="records.length === 0 && !loading" description="暂无记录" />
            </van-list>
          </van-pull-refresh>
        </van-tab>

        <van-tab title="其他入库">
          <van-pull-refresh v-model="refreshing2" @refresh="loadData('in')">
            <van-list :loading="loading2" :finished="finished2" finished-text="没有更多了" @load="loadData('in')">
              <div v-for="r in records2" :key="r.id" class="record-card">
                <div class="record-header">
                  <van-tag type="success">其他入库</van-tag>
                  <span class="record-qty in">+{{ r.quantity }}</span>
                </div>
                <div class="record-info">
                  <span>{{ r.product_name }}</span>
                  <span>{{ r.created_at?.substring(0, 16) }}</span>
                </div>
                <div class="record-reason">{{ r.reason || '' }}</div>
              </div>
              <van-empty v-if="records2.length === 0 && !loading2" description="暂无记录" />
            </van-list>
          </van-pull-refresh>
        </van-tab>
      </van-tabs>

      <van-button type="primary" block style="margin:12px 16px" @click="showCreate = true">
        新建其他出入库
      </van-button>
    </div>

    <!-- 新建表单 -->
    <div v-else style="padding:12px 16px">
      <van-tabs v-model="formType" style="margin-bottom:12px">
        <van-tab title="其他出库" />
        <van-tab title="其他入库" />
      </van-tabs>

      <van-cell-group inset title="出库信息">
        <van-cell title="仓库" is-link :value="form.warehouse_name || '请选择'" @click="showWhPicker2 = true" />
        <van-cell title="原因" is-link :value="form.reason || '请选择'" @click="showReasonPicker = true" />
        <van-cell title="备注">
          <template #extra>
            <van-field v-model="form.remark" placeholder="可选" style="width:200px" />
          </template>
        </van-cell>
      </van-cell-group>

      <div style="display:flex;justify-content:space-between;align-items:center;margin:12px 0 8px">
        <span style="font-weight:bold">商品明细</span>
        <van-button size="small" type="primary" @click="showProductPicker = true" :disabled="!form.warehouse_id">添加商品</van-button>
      </div>

      <van-cell-group v-for="(item, idx) in form.items" :key="idx" style="margin-bottom:8px">
        <van-cell :title="item.product_name" :label="'可用: ' + item.available" />
        <van-cell title="数量">
          <template #extra>
            <van-stepper v-model="item.quantity" min="1" @change="onQtyChange(item)" />
          </template>
        </van-cell>
        <van-cell>
          <template #extra>
            <van-button size="small" type="danger" plain @click="form.items.splice(idx, 1)">删除</van-button>
          </template>
        </van-cell>
      </van-cell-group>

      <van-empty v-if="form.items.length === 0" description="请添加商品" />

      <div style="display:flex;gap:8px;margin-top:16px">
        <van-button block @click="showCreate = false">取消</van-button>
        <van-button :type="formType === 0 ? 'danger' : 'success'" block :loading="submitting" @click="handleSubmit">
          {{ formType === 0 ? '提交出库' : '提交入库' }}
        </van-button>
      </div>
    </div>

    <!-- 仓库选择 -->
    <van-popup v-model:show="showWhPicker" position="bottom" round>
      <van-picker title="选择仓库" :columns="whColumns" @confirm="onQueryWhConfirm" @cancel="showWhPicker = false" />
    </van-popup>
    <van-popup v-model:show="showWhPicker2" position="bottom" round>
      <van-picker title="选择仓库" :columns="whColumns" @confirm="onFormWhConfirm" @cancel="showWhPicker2 = false" />
    </van-popup>

    <!-- 原因选择 -->
    <van-popup v-model:show="showReasonPicker" position="bottom" round>
      <van-picker title="选择原因" :columns="reasonOptions" @confirm="onReasonSelect" @cancel="showReasonPicker = false" />
    </van-popup>

    <!-- 商品选择 -->
    <van-popup v-model:show="showProductPicker" position="bottom" round style="max-height:70%">
      <van-search v-model="productSearch" placeholder="搜索商品" />
      <van-list>
        <van-cell v-for="p in filteredProducts" :key="p.id" :title="p.name" :label="'可用: ' + (p.available || 0)" clickable @click="addProduct(p)" />
        <van-empty v-if="filteredProducts.length === 0" description="无商品" />
      </van-list>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import { getWarehouses, getProducts, getInventory, getOtherLog, createOtherIn, createOtherOut } from '../api'

const tab = ref(0)
const showCreate = ref(false)
const submitting = ref(false)
const showWhPicker = ref(false)
const showWhPicker2 = ref(false)
const showReasonPicker = ref(false)
const showProductPicker = ref(false)
const productSearch = ref('')
const formType = ref(0)

const queryWhId = ref(null)
const queryWhName = ref('')
const queryReason = ref('')
const records = ref([])
const records2 = ref([])
const loading = ref(false)
const loading2 = ref(false)
const finished = ref(false)
const finished2 = ref(false)
const refreshing = ref(false)
const refreshing2 = ref(false)
const page1 = ref(1)
const page2 = ref(1)

const form = ref({ warehouse_id: null, warehouse_name: '', reason: '', remark: '', items: [] })
const warehouses = ref([])
const products = ref([])

const reasonOptions = [
  { text: '报损', value: '报损' },
  { text: '过期', value: '过期' },
  { text: '破损', value: '破损' },
  { text: '盘亏', value: '盘亏' },
  { text: '其他', value: '其他' },
  { text: '盘盈', value: '盘盈' },
  { text: '退货入库', value: '退货入库' },
  { text: '其他', value: '其他' }
]

const reasonColumns = [
  { text: '全部', value: '' },
  ...reasonOptions
]

const whColumns = computed(() => [
  { text: '全部仓库', value: null },
  ...warehouses.value.map(w => ({ text: w.name, value: w.id }))
])

const filteredProducts = computed(() => {
  if (!productSearch.value) return products.value.filter(p => p.available > 0).slice(0, 30)
  return products.value.filter(p => (p.name.includes(productSearch.value) || p.code?.includes(productSearch.value)) && p.available > 0).slice(0, 30)
})

const loadData = async (type) => {
  if (type === 'out') {
    loading.value = true
    try {
      const res = await getOtherLog({ type: 'out', page: page1.value, page_size: 20, warehouse_id: queryWhId.value })
      if (page1.value === 1) records.value = res.data || []
      else records.value.push(...(res.data || []))
      finished.value = (res.data || []).length < 20
      page1.value++
    } catch {}
    loading.value = false
    refreshing.value = false
  } else {
    loading2.value = true
    try {
      const res = await getOtherLog({ type: 'in', page: page2.value, page_size: 20, warehouse_id: queryWhId.value })
      if (page2.value === 1) records2.value = res.data || []
      else records2.value.push(...(res.data || []))
      finished2.value = (res.data || []).length < 20
      page2.value++
    } catch {}
    loading2.value = false
    refreshing2.value = false
  }
}

const onQueryWhConfirm = ({ selectedOptions }) => {
  queryWhId.value = selectedOptions[0].value
  queryWhName.value = selectedOptions[0].text === '全部仓库' ? '' : selectedOptions[0].text
  showWhPicker.value = false
  page1.value = 1; page2.value = 1; loadData('out'); loadData('in')
}

const onFormWhConfirm = async ({ selectedOptions }) => {
  form.value.warehouse_id = selectedOptions[0].value
  form.value.warehouse_name = selectedOptions[0].text
  form.value.items = []
  showWhPicker2.value = false
  if (form.value.warehouse_id) {
    try {
      const res = await getInventory({ warehouse_id: form.value.warehouse_id, page_size: 100 })
      products.value = (res.data || []).map(i => ({ ...i, available: i.quantity }))
    } catch {}
  }
}

const onReasonConfirm = ({ selectedOptions }) => {
  queryReason.value = selectedOptions.value
  page1.value = 1; loadData('out')
}

const onReasonSelect = ({ selectedOptions }) => {
  form.value.reason = selectedOptions.value
  showReasonPicker.value = false
}

const addProduct = (p) => {
  if (form.value.items.find(i => i.product_id === p.id)) {
    showToast('已添加')
    return
  }
  form.value.items.push({ product_id: p.id, product_name: p.name, available: p.available || 0, quantity: 1 })
  showProductPicker.value = false
}

const onQtyChange = (item) => {
  if (item.quantity > item.available && formType.value === 0) {
    item.quantity = item.available
    showToast('超过可用库存')
  }
}

const handleSubmit = async () => {
  if (!form.value.warehouse_id) return showToast('请选择仓库')
  if (!form.value.reason) return showToast('请选择原因')
  const validItems = form.value.items.filter(i => i.quantity > 0)
  if (!validItems.length) return showToast('请添加商品')

  submitting.value = true
  try {
    for (const item of validItems) {
      if (formType.value === 0) {
        await createOtherOut({ warehouse_id: form.value.warehouse_id, product_id: item.product_id, quantity: item.quantity, reason: form.value.reason, remark: form.value.remark })
      } else {
        await createOtherIn({ warehouse_id: form.value.warehouse_id, product_id: item.product_id, quantity: item.quantity, reason: form.value.reason, remark: form.value.remark })
      }
    }
    showSuccessToast(formType.value === 0 ? '其他出库成功' : '其他入库成功')
    showCreate.value = false
    page1.value = 1; page2.value = 1; loadData('out'); loadData('in')
  } catch { showToast('操作失败') }
  submitting.value = false
}

onMounted(async () => {
  const [whRes] = await Promise.all([getWarehouses()])
  warehouses.value = whRes.data || []
  loadData('out')
  loadData('in')
})
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.record-card {
  background: #fff; margin: 8px 16px; border-radius: 8px;
  padding: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.record-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.record-qty { font-size: 18px; font-weight: bold; color: #ee0a24; }
.record-qty.in { color: #07c160; }
.record-info { display: flex; justify-content: space-between; font-size: 13px; color: #666; margin-bottom: 4px; }
.record-reason { font-size: 12px; color: #999; }
</style>
