<template>
  <div class="page">
    <van-nav-bar title="库存盘点" left-arrow @click-left="$router.back()" />

    <!-- 盘点列表 -->
    <div v-if="!showCreate && !showDetail">
      <van-button type="primary" block style="margin:12px 16px" @click="startCreate">
        新建盘点单
      </van-button>

      <van-tabs v-model:active="listTab" sticky>
        <van-tab title="进行中">
          <van-pull-refresh v-model="refreshing" @refresh="loadData(1)">
            <van-list :loading="loading" :finished="finished" finished-text="没有更多了" @load="loadData(1)">
              <div v-for="c in list" :key="c.id" class="check-card" @click="openDetail(c)">
                <div class="check-header">
                  <span class="check-no">{{ c.code }}</span>
                  <van-tag type="warning">盘点中</van-tag>
                </div>
                <div class="check-info">仓库: {{ c.warehouse_name }}</div>
                <div class="check-info">{{ c.created_at?.substring(0, 16) }}</div>
              </div>
              <van-empty v-if="list.length === 0 && !loading" description="暂无盘点任务" />
            </van-list>
          </van-pull-refresh>
        </van-tab>
        <van-tab title="已确认">
          <van-pull-refresh v-model="refreshing2" @refresh="loadData(2)">
            <van-list :loading="loading2" :finished="finished2" finished-text="没有更多了" @load="loadData(2)">
              <div v-for="c in list2" :key="c.id" class="check-card" @click="openDetail(c)">
                <div class="check-header">
                  <span class="check-no">{{ c.code }}</span>
                  <van-tag type="success">已确认</van-tag>
                </div>
                <div class="check-info">仓库: {{ c.warehouse_name }}</div>
                <div class="check-info">{{ c.confirmed_at?.substring(0, 16) }}</div>
              </div>
              <van-empty v-if="list2.length === 0 && !loading2" description="暂无已确认盘点" />
            </van-list>
          </van-pull-refresh>
        </van-tab>
      </van-tabs>
    </div>

    <!-- 新建盘点 -->
    <div v-else-if="showCreate" style="padding:12px 16px">
      <van-cell-group inset title="盘点信息">
        <van-cell title="仓库" is-link :value="form.warehouse_name || '请选择'" @click="showWhPicker = true" />
        <van-cell title="备注">
          <template #extra>
            <van-field v-model="form.remark" placeholder="可选" style="width:200px" />
          </template>
        </van-cell>
      </van-cell-group>

      <div style="display:flex;justify-content:space-between;align-items:center;margin:12px 0 8px">
        <span style="font-weight:bold">盘点明细</span>
        <van-button size="small" type="primary" @click="showProductPicker = true">添加商品</van-button>
      </div>

      <van-cell-group v-for="(item, idx) in form.items" :key="idx" style="margin-bottom:8px">
        <van-cell :title="item.product_name" :label="'系统库存: ' + item.system_qty" />
        <van-cell title="实盘数量">
          <template #extra>
            <van-stepper v-model="item.actual_qty" min="0" @change="calcDiff(item)" />
          </template>
        </van-cell>
        <van-cell title="差异">
          <template #value>
            <span :style="{ color: item.diff_qty === 0 ? '#999' : item.diff_qty > 0 ? '#07c160' : '#ee0a24', fontWeight: 'bold' }">
              {{ item.diff_qty > 0 ? '+' : '' }}{{ item.diff_qty }}
            </span>
          </template>
        </van-cell>
        <van-cell>
          <template #extra>
            <van-button size="small" type="danger" plain @click="form.items.splice(idx, 1)">删除</van-button>
          </template>
        </van-cell>
      </van-cell-group>

      <van-empty v-if="form.items.length === 0" description="请添加要盘点的商品" />

      <div style="display:flex;gap:8px;margin-top:16px">
        <van-button block @click="showCreate = false">取消</van-button>
        <van-button type="primary" block :loading="submitting" @click="handleCreate">提交盘点</van-button>
      </div>
    </div>

    <!-- 盘点详情 -->
    <div v-else-if="showDetail" style="padding:12px 16px">
      <div class="detail-header">
        <h3>{{ detail.code }}</h3>
        <van-tag :type="detail.status === 1 ? 'warning' : 'success'">{{ detail.status === 1 ? '盘点中' : '已确认' }}</van-tag>
      </div>
      <van-cell-group inset style="margin:8px 0">
        <van-cell title="仓库" :value="detail.warehouse_name" />
        <van-cell title="创建时间" :value="detail.created_at?.substring(0, 16)" />
        <van-cell v-if="detail.confirmed_at" title="确认时间" :value="detail.confirmed_at?.substring(0, 16)" />
      </van-cell-group>

      <div style="font-weight:bold;margin:8px 0">盘点明细</div>

      <div v-for="item in detail.items" :key="item.product_id" class="item-card">
        <div style="font-weight:bold;margin-bottom:4px">{{ item.product_name }}</div>
        <div style="display:flex;gap:16px;font-size:13px;color:#666">
          <span>系统: {{ item.system_qty }}</span>
          <span>差异: <span :style="{ color: item.diff_qty === 0 ? '#999' : item.diff_qty > 0 ? '#07c160' : '#ee0a24' }">{{ item.diff_qty > 0 ? '+' : '' }}{{ item.diff_qty }}</span></span>
        </div>
        <div v-if="detail.status === 1" style="margin-top:6px">
          <van-stepper v-model="item.actual_qty" min="0" @change="calcDetailDiff(item)" />
        </div>
        <div v-else style="margin-top:6px;font-weight:bold">实盘: {{ item.actual_qty }}</div>
      </div>

      <div style="display:flex;gap:8px;margin-top:12px">
        <van-button block @click="showDetail = false">返回</van-button>
        <van-button v-if="detail.status === 1" type="primary" block :loading="submitting" @click="handleAudit">确认盘点</van-button>
      </div>
    </div>

    <!-- 仓库选择 -->
    <van-popup v-model:show="showWhPicker" position="bottom" round>
      <van-picker title="选择仓库" :columns="whColumns" @confirm="onWhConfirm" @cancel="showWhPicker = false" />
    </van-popup>

    <!-- 商品选择 -->
    <van-popup v-model:show="showProductPicker" position="bottom" round style="max-height:70%">
      <van-search v-model="productSearch" placeholder="搜索商品" />
      <van-list>
        <van-cell v-for="p in filteredProducts" :key="p.id" :title="p.name" :label="p.code" clickable @click="addProduct(p)" />
        <van-empty v-if="filteredProducts.length === 0" description="无商品" />
      </van-list>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getStocktaking, createStocktaking, getStocktakingDetail, auditStocktaking, getWarehouses, getProducts, getInventory } from '../api'

const listTab = ref(0)
const list = ref([])
const list2 = ref([])
const loading = ref(false)
const loading2 = ref(false)
const finished = ref(false)
const finished2 = ref(false)
const refreshing = ref(false)
const refreshing2 = ref(false)
const page1 = ref(1)
const page2 = ref(1)

const showCreate = ref(false)
const showDetail = ref(false)
const submitting = ref(false)
const showWhPicker = ref(false)
const showProductPicker = ref(false)
const productSearch = ref('')

const form = ref({ warehouse_id: null, warehouse_name: '', remark: '', items: [] })
const detail = ref({})
const warehouses = ref([])
const products = ref([])

const whColumns = computed(() => warehouses.value.map(w => ({ text: w.name, value: w.id })))
const filteredProducts = computed(() => {
  if (!productSearch.value) return products.value.slice(0, 30)
  return products.value.filter(p => p.name.includes(productSearch.value) || p.code?.includes(productSearch.value)).slice(0, 30)
})

const loadData = async (status) => {
  if (status === 1) {
    loading.value = true
    try {
      const res = await getStocktaking({ status: 1, page: page1.value, page_size: 20 })
      if (page1.value === 1) list.value = res.data || []
      else list.value.push(...(res.data || []))
      finished.value = (res.data || []).length < 20
      page1.value++
    } catch {}
    loading.value = false
    refreshing.value = false
  } else {
    loading2.value = true
    try {
      const res = await getStocktaking({ status: 2, page: page2.value, page_size: 20 })
      if (page2.value === 1) list2.value = res.data || []
      else list2.value.push(...(res.data || []))
      finished2.value = (res.data || []).length < 20
      page2.value++
    } catch {}
    loading2.value = false
    refreshing2.value = false
  }
}

const startCreate = () => {
  form.value = { warehouse_id: null, warehouse_name: '', remark: '', items: [] }
  showCreate.value = true
}

const onWhConfirm = ({ selectedOptions }) => {
  form.value.warehouse_id = selectedOptions[0].value
  form.value.warehouse_name = selectedOptions[0].text
  showWhPicker.value = false
}

const addProduct = async (p) => {
  if (form.value.items.find(i => i.product_id === p.id)) {
    showToast('已添加')
    return
  }
  let system_qty = 0
  if (form.value.warehouse_id) {
    try {
      const res = await getInventory({ warehouse_id: form.value.warehouse_id, product_id: p.id })
      system_qty = res.data?.[0]?.quantity || 0
    } catch {}
  }
  form.value.items.push({ product_id: p.id, product_name: p.name, system_qty, actual_qty: system_qty, diff_qty: 0 })
  showProductPicker.value = false
}

const calcDiff = (item) => {
  item.diff_qty = (item.actual_qty || 0) - (item.system_qty || 0)
}

const calcDetailDiff = (item) => {
  item.diff_qty = (item.actual_qty || 0) - (item.system_qty || 0)
}

const handleCreate = async () => {
  if (!form.value.warehouse_id) return showToast('请选择仓库')
  submitting.value = true
  try {
    await createStocktaking({
      warehouse_id: form.value.warehouse_id,
      remark: form.value.remark,
      items: form.value.items.map(i => ({ product_id: i.product_id, count_num: i.actual_qty }))
    })
    showSuccessToast('盘点单已创建')
    showCreate.value = false
    page1.value = 1; loadData(1)
  } catch { showToast('创建失败') }
  submitting.value = false
}

const openDetail = async (c) => {
  try {
    const res = await getStocktakingDetail(c.id)
    detail.value = res.data
    showDetail.value = true
  } catch { showToast('加载失败') }
}

const handleAudit = async () => {
  try {
    await showConfirmDialog({ title: '确认盘点', message: '确认后将按实盘数量更新库存，是否继续？' })
    await auditStocktaking(detail.value.id)
    showSuccessToast('盘点已确认')
    showDetail.value = false
    page1.value = 1; page2.value = 1; loadData(1); loadData(2)
  } catch {}
}

onMounted(async () => {
  const [whRes, pRes] = await Promise.all([getWarehouses(), getProducts({ page_size: 500 })])
  warehouses.value = whRes.data || []
  products.value = pRes.data || []
  loadData(1)
  loadData(2)
})
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.check-card {
  background: #fff; margin: 8px 16px; border-radius: 10px;
  padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.check-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.check-no { font-weight: bold; color: #333; font-size: 15px; }
.check-info { font-size: 13px; color: #666; }
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.item-card {
  background: #fff; border-radius: 8px; padding: 12px; margin-bottom: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
</style>
