<template>
  <div class="page">
    <van-nav-bar title="库存调拨" left-arrow @click-left="$router.back()" />

    <!-- 调拨列表 -->
    <div v-if="!showCreate && !showDetail">
      <van-button type="primary" block style="margin:12px 16px" @click="startCreate">
        新建调拨单
      </van-button>

      <van-tabs v-model:active="listTab" sticky>
        <van-tab title="调拨中">
          <van-pull-refresh v-model="refreshing" @refresh="loadData(1)">
            <van-list :loading="loading" :finished="finished" finished-text="没有更多了" @load="loadData(1)">
              <div v-for="t in list" :key="t.id" class="transfer-card" @click="openDetail(t)">
                <div class="transfer-header">
                  <span class="transfer-no">{{ t.code }}</span>
                  <van-tag type="warning">调拨中</van-tag>
                </div>
                <div class="transfer-route">
                  {{ t.from_warehouse_name }} → {{ t.to_warehouse_name }}
                </div>
                <div class="transfer-info">
                  <span>{{ t.created_at?.substring(0, 16) }}</span>
                  <span v-if="t.remark">{{ t.remark }}</span>
                </div>
              </div>
              <van-empty v-if="list.length === 0 && !loading" description="暂无调拨任务" />
            </van-list>
          </van-pull-refresh>
        </van-tab>
        <van-tab title="已完成">
          <van-pull-refresh v-model="refreshing2" @refresh="loadData(2)">
            <van-list :loading="loading2" :finished="finished2" finished-text="没有更多了" @load="loadData(2)">
              <div v-for="t in list2" :key="t.id" class="transfer-card" @click="openDetail(t)">
                <div class="transfer-header">
                  <span class="transfer-no">{{ t.code }}</span>
                  <van-tag type="success">已完成</van-tag>
                </div>
                <div class="transfer-route">
                  {{ t.from_warehouse_name }} → {{ t.to_warehouse_name }}
                </div>
                <div class="transfer-info">
                  <span>{{ t.confirmed_at?.substring(0, 16) }}</span>
                </div>
              </div>
              <van-empty v-if="list2.length === 0 && !loading2" description="暂无已完成调拨" />
            </van-list>
          </van-pull-refresh>
        </van-tab>
      </van-tabs>
    </div>

    <!-- 新建调拨 -->
    <div v-else-if="showCreate" style="padding:12px 16px">
      <van-cell-group inset title="调拨信息">
        <van-cell title="调出仓库" is-link :value="form.from_warehouse_name || '请选择'" @click="showFromPicker = true" />
        <van-cell title="调入仓库" is-link :value="form.to_warehouse_name || '请选择'" @click="showToPicker = true" />
        <van-cell title="备注">
          <template #extra>
            <van-field v-model="form.remark" placeholder="可选" style="width:200px" />
          </template>
        </van-cell>
      </van-cell-group>

      <div style="display:flex;justify-content:space-between;align-items:center;margin:12px 0 8px">
        <span style="font-weight:bold">调拨商品</span>
        <van-button size="small" type="primary" @click="showProductPicker = true" :disabled="!form.from_warehouse_id">添加商品</van-button>
      </div>

      <van-cell-group v-for="(item, idx) in form.items" :key="idx" style="margin-bottom:8px">
        <van-cell :title="item.product_name" :label="'可调拨: ' + item.available" />
        <van-cell title="调拨数量">
          <template #extra>
            <van-stepper v-model="item.quantity" min="1" :max="item.available" @change="onQtyChange(item)" />
          </template>
        </van-cell>
        <van-cell>
          <template #extra>
            <van-button size="small" type="danger" plain @click="form.items.splice(idx, 1)">删除</van-button>
          </template>
        </van-cell>
      </van-cell-group>

      <van-empty v-if="form.items.length === 0" description="请添加调拨商品" />

      <div style="display:flex;gap:8px;margin-top:16px">
        <van-button block @click="showCreate = false">取消</van-button>
        <van-button type="primary" block :loading="submitting" @click="handleCreate">提交调拨</van-button>
      </div>
    </div>

    <!-- 调拨详情 -->
    <div v-else-if="showDetail" style="padding:12px 16px">
      <div class="detail-header">
        <h3>{{ detail.code }}</h3>
        <van-tag :type="detail.status === 1 ? 'warning' : 'success'">{{ detail.status === 1 ? '调拨中' : '已完成' }}</van-tag>
      </div>
      <van-cell-group inset style="margin:8px 0">
        <van-cell title="调出仓库" :value="detail.from_warehouse_name" />
        <van-cell title="调入仓库" :value="detail.to_warehouse_name" />
        <van-cell title="创建时间" :value="detail.created_at?.substring(0, 16)" />
        <van-cell v-if="detail.confirmed_at" title="确认时间" :value="detail.confirmed_at?.substring(0, 16)" />
        <van-cell v-if="detail.remark" title="备注" :value="detail.remark" />
      </van-cell-group>

      <div style="font-weight:bold;margin:8px 0">调拨明细</div>
      <div v-for="item in detail.items" :key="item.product_id" class="item-card">
        <div style="font-weight:bold">{{ item.product_name }}</div>
        <div style="color:#666;font-size:13px;margin-top:4px">数量: {{ item.quantity }}</div>
      </div>

      <div style="display:flex;gap:8px;margin-top:12px">
        <van-button block @click="showDetail = false">返回</van-button>
        <van-button v-if="detail.status === 1" type="primary" block :loading="submitting" @click="handleConfirm">确认调拨</van-button>
      </div>
    </div>

    <!-- 调出仓库选择 -->
    <van-popup v-model:show="showFromPicker" position="bottom" round>
      <van-picker title="选择调出仓库" :columns="whColumns" @confirm="onFromConfirm" @cancel="showFromPicker = false" />
    </van-popup>
    <!-- 调入仓库选择 -->
    <van-popup v-model:show="showToPicker" position="bottom" round>
      <van-picker title="选择调入仓库" :columns="whColumns" @confirm="onToConfirm" @cancel="showToPicker = false" />
    </van-popup>

    <!-- 商品选择 -->
    <van-popup v-model:show="showProductPicker" position="bottom" round style="max-height:70%">
      <van-search v-model="productSearch" placeholder="搜索商品" />
      <van-list>
        <van-cell v-for="p in filteredProducts" :key="p.id" :title="p.name" :label="'库存: ' + (p.available || 0)" clickable @click="addProduct(p)" />
        <van-empty v-if="filteredProducts.length === 0" description="无商品" />
      </van-list>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getTransfers, createTransfer, getTransfer, confirmTransfer, cancelTransfer, getWarehouses, getProducts, getInventory } from '../api'

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
const showFromPicker = ref(false)
const showToPicker = ref(false)
const showProductPicker = ref(false)
const productSearch = ref('')

const form = ref({ from_warehouse_id: null, from_warehouse_name: '', to_warehouse_id: null, to_warehouse_name: '', remark: '', items: [] })
const detail = ref({})
const warehouses = ref([])
const products = ref([])

const whColumns = computed(() => warehouses.value.map(w => ({ text: w.name, value: w.id })))
const filteredProducts = computed(() => {
  if (!productSearch.value) return products.value.filter(p => p.available > 0).slice(0, 30)
  return products.value.filter(p => (p.name.includes(productSearch.value) || p.code?.includes(productSearch.value)) && p.available > 0).slice(0, 30)
})

const loadData = async (status) => {
  if (status === 1) {
    loading.value = true
    try {
      const res = await getTransfers({ status: 1, page: page1.value, page_size: 20 })
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
      const res = await getTransfers({ status: 2, page: page2.value, page_size: 20 })
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
  form.value = { from_warehouse_id: null, from_warehouse_name: '', to_warehouse_id: null, to_warehouse_name: '', remark: '', items: [] }
  showCreate.value = true
}

const onFromConfirm = async ({ selectedOptions }) => {
  form.value.from_warehouse_id = selectedOptions[0].value
  form.value.from_warehouse_name = selectedOptions[0].text
  form.value.items = []
  showFromPicker.value = false
  await loadProductStock()
}

const onToConfirm = ({ selectedOptions }) => {
  if (selectedOptions[0].value === form.value.from_warehouse_id) {
    showToast('调入仓库不能与调出仓库相同')
    return
  }
  form.value.to_warehouse_id = selectedOptions[0].value
  form.value.to_warehouse_name = selectedOptions[0].text
  showToPicker.value = false
}

const loadProductStock = async () => {
  if (!form.value.from_warehouse_id) return
  try {
    const res = await getInventory({ warehouse_id: form.value.from_warehouse_id, page_size: 500 })
    const inv = res.data || []
    products.value = inv.map(i => ({ ...i, available: i.quantity }))
  } catch {}
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
  if (item.quantity > item.available) {
    item.quantity = item.available
    showToast('超过可用库存')
  }
}

const handleCreate = async () => {
  if (!form.value.from_warehouse_id) return showToast('请选择调出仓库')
  if (!form.value.to_warehouse_id) return showToast('请选择调入仓库')
  const validItems = form.value.items.filter(i => i.quantity > 0 && i.quantity <= i.available)
  if (!validItems.length) return showToast('请添加有效的调拨商品')
  submitting.value = true
  try {
    await createTransfer({
      from_warehouse_id: form.value.from_warehouse_id,
      to_warehouse_id: form.value.to_warehouse_id,
      remark: form.value.remark,
      items: validItems.map(i => ({ product_id: i.product_id, quantity: i.quantity }))
    })
    showSuccessToast('调拨单已创建')
    showCreate.value = false
    page1.value = 1; loadData(1)
  } catch { showToast('创建失败') }
  submitting.value = false
}

const openDetail = async (t) => {
  try {
    const res = await getTransfer(t.id)
    detail.value = res.data
    showDetail.value = true
  } catch { showToast('加载失败') }
}

const handleConfirm = async () => {
  try {
    await showConfirmDialog({ title: '确认调拨', message: '确认后库存将从调出仓转移到调入仓' })
    await confirmTransfer(detail.value.id)
    showSuccessToast('调拨已确认')
    showDetail.value = false
    page1.value = 1; page2.value = 1; loadData(1); loadData(2)
  } catch {}
}

onMounted(async () => {
  const [whRes] = await Promise.all([getWarehouses()])
  warehouses.value = whRes.data || []
  loadData(1)
  loadData(2)
})
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.transfer-card {
  background: #fff; margin: 8px 16px; border-radius: 10px;
  padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.transfer-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.transfer-no { font-weight: bold; color: #333; font-size: 15px; }
.transfer-route { font-size: 13px; color: #1989fa; margin-bottom: 4px; }
.transfer-info { display: flex; gap: 12px; font-size: 12px; color: #999; }
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.item-card {
  background: #fff; border-radius: 8px; padding: 12px; margin-bottom: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
</style>
