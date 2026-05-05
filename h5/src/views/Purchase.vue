<template>
  <div class="page">
    <van-nav-bar title="采购管理" left-arrow @click-left="$router.back()" />

    <!-- 采购单列表 -->
    <div v-if="!showCreate">
      <van-tabs v-model:active="tab" sticky>
        <van-tab title="采购订单">
          <van-button type="primary" block style="margin:8px 16px" @click="startCreate">新建采购订单</van-button>
          <van-pull-refresh v-model="refreshing" @refresh="loadOrders">
            <van-list :loading="loading" :finished="finished" finished-text="没有更多了" @load="loadOrders">
              <div v-for="o in orders" :key="o.id" class="order-card" @click="showOrderDetail(o)">
                <div class="order-header">
                  <span class="order-no">{{ o.code }}</span>
                  <van-tag :type="getOrderStatusType(o.status)">{{ getOrderStatusLabel(o.status) }}</van-tag>
                </div>
                <div class="order-info">
                  <span>{{ o.supplier_name }}</span>
                  <span>¥{{ (o.total_amount || 0).toFixed(2) }}</span>
                </div>
                <div class="order-info">
                  <span>{{ o.created_at?.substring(0, 16) }}</span>
                  <van-button v-if="o.status === 0" size="small" type="primary" plain @click.stop="toStockin(o)">生成入库</van-button>
                </div>
              </div>
              <van-empty v-if="orders.length === 0 && !loading" description="暂无采购订单" />
            </van-list>
          </van-pull-refresh>
        </van-tab>

        <van-tab title="入库单">
          <van-pull-refresh v-model="refreshing2" @refresh="loadStockins">
            <van-list :loading="loading2" :finished="finished2" finished-text="没有更多了" @load="loadStockins">
              <div v-for="s in stockins" :key="s.id" class="order-card" @click="showStockinDetail(s)">
                <div class="order-header">
                  <span class="order-no">{{ s.code }}</span>
                  <van-tag :type="getStockinStatusType(s.status)">{{ getStockinStatusLabel(s.status) }}</van-tag>
                </div>
                <div class="order-info">
                  <span>{{ s.supplier_name }}</span>
                  <span>¥{{ (s.total_amount || 0).toFixed(2) }}</span>
                </div>
                <div class="order-info">
                  <span>{{ s.created_at?.substring(0, 16) }}</span>
                  <van-button v-if="s.status === 0" size="small" type="success" plain @click.stop="confirmStockin(s)">确认入库</van-button>
                </div>
              </div>
              <van-empty v-if="stockins.length === 0 && !loading2" description="暂无入库单" />
            </van-list>
          </van-pull-refresh>
        </van-tab>

        <van-tab title="采购退货">
          <van-button type="warning" block style="margin:8px 16px" @click="startReturn">新建退货</van-button>
          <van-pull-refresh v-model="refreshing3" @refresh="loadReturns">
            <van-list :loading="loading3" :finished="finished3" finished-text="没有更多了" @load="loadReturns">
              <div v-for="r in returns" :key="r.id" class="order-card" @click="showReturnDetail(r)">
                <div class="order-header">
                  <span class="order-no">{{ r.code }}</span>
                  <van-tag :type="getReturnStatusType(r.status)">{{ getReturnStatusLabel(r.status) }}</van-tag>
                </div>
                <div class="order-info">
                  <span>{{ r.supplier_name }}</span>
                  <span>¥{{ (r.total_amount || 0).toFixed(2) }}</span>
                </div>
                <div class="order-info">
                  <span>{{ r.created_at?.substring(0, 16) }}</span>
                  <van-button v-if="r.status === 0" size="small" type="warning" plain @click.stop="confirmReturn(r)">确认退货</van-button>
                </div>
              </div>
              <van-empty v-if="returns.length === 0 && !loading3" description="暂无退货记录" />
            </van-list>
          </van-pull-refresh>
        </van-tab>
      </van-tabs>
    </div>

    <!-- 新建采购订单 -->
    <div v-else-if="showCreate" style="padding:12px 16px">
      <van-cell-group inset title="订单信息">
        <van-cell title="供应商" is-link :value="form.supplier_name || '请选择'" @click="showSupplierPicker = true" />
        <van-cell title="收货仓库" is-link :value="form.warehouse_name || '请选择'" @click="showWhPicker = true" />
        <van-cell title="备注">
          <template #extra>
            <van-field v-model="form.remark" placeholder="可选" style="width:200px" />
          </template>
        </van-cell>
      </van-cell-group>

      <div style="display:flex;justify-content:space-between;align-items:center;margin:12px 0 8px">
        <span style="font-weight:bold">商品明细</span>
        <van-button size="small" type="primary" @click="showProductPicker = true">添加商品</van-button>
      </div>

      <van-cell-group v-for="(item, idx) in form.items" :key="idx" style="margin-bottom:8px">
        <van-cell :title="item.product_name" :label="'单价: ¥' + (item.price || 0)" />
        <van-cell title="数量">
          <template #extra>
            <van-stepper v-model="item.quantity" min="1" />
          </template>
        </van-cell>
        <van-cell title="金额">
          <template #value>¥{{ ((item.quantity || 0) * (item.price || 0)).toFixed(2) }}</template>
        </van-cell>
        <van-cell>
          <template #extra>
            <van-button size="small" type="danger" plain @click="form.items.splice(idx, 1)">删除</van-button>
          </template>
        </van-cell>
      </van-cell-group>

      <div class="order-summary">
        <span>合计: </span>
        <span class="total-price">¥{{ totalAmount }}</span>
      </div>

      <div style="display:flex;gap:8px;margin-top:12px">
        <van-button block @click="showCreate = false">取消</van-button>
        <van-button type="primary" block :loading="submitting" @click="handleCreateOrder">提交订单</van-button>
      </div>
    </div>

    <!-- 新建退货 -->
    <div v-else-if="showReturnForm" style="padding:12px 16px">
      <van-cell-group inset title="退货信息">
        <van-cell title="供应商" is-link :value="returnForm.supplier_name || '请选择'" @click="showSupplierPicker2 = true" />
        <van-cell title="关联入库单" is-link :value="returnForm.stockin_code || '可选'" @click="showStockinPicker = true" />
        <van-cell title="备注">
          <template #extra>
            <van-field v-model="returnForm.remark" placeholder="可选" style="width:200px" />
          </template>
        </van-cell>
      </van-cell-group>

      <div style="display:flex;justify-content:space-between;align-items:center;margin:12px 0 8px">
        <span style="font-weight:bold">退货商品</span>
        <van-button size="small" type="warning" @click="showProductPicker2 = true">添加商品</van-button>
      </div>

      <van-cell-group v-for="(item, idx) in returnForm.items" :key="idx" style="margin-bottom:8px">
        <van-cell :title="item.product_name" :label="'单价: ¥' + (item.price || 0)" />
        <van-cell title="数量">
          <template #extra>
            <van-stepper v-model="item.quantity" min="1" />
          </template>
        </van-cell>
        <van-cell>
          <template #extra>
            <van-button size="small" type="danger" plain @click="returnForm.items.splice(idx, 1)">删除</van-button>
          </template>
        </van-cell>
      </van-cell-group>

      <div style="display:flex;gap:8px;margin-top:12px">
        <van-button block @click="showReturnForm = false">取消</van-button>
        <van-button type="warning" block :loading="submitting" @click="handleCreateReturn">提交退货</van-button>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <van-popup v-model:show="showDetailPopup" position="bottom" round style="max-height:70%">
      <div style="padding:16px" v-if="detail">
        <h3>{{ detail.code }}</h3>
        <van-cell-group style="margin-top:12px">
          <van-cell title="供应商" :value="detail.supplier_name" />
          <van-cell title="总金额" :value="'¥' + (detail.total_amount || 0).toFixed(2)" />
          <van-cell title="状态" :value="detail.status_text || detail.status" />
          <van-cell v-if="detail.created_at" title="创建时间" :value="detail.created_at?.substring(0, 16)" />
          <van-cell v-if="detail.confirmed_at" title="确认时间" :value="detail.confirmed_at?.substring(0, 16)" />
        </van-cell-group>
        <van-cell-group title="明细" v-if="detail.items" style="margin-top:12px">
          <van-cell v-for="item in detail.items" :key="item.id"
            :title="item.product_name"
            :label="'单价: ¥' + (item.price || 0)"
            :value="'x' + (item.quantity || item.count_num)" />
        </van-cell-group>
      </div>
    </van-popup>

    <!-- 选择器 -->
    <van-popup v-model:show="showSupplierPicker" position="bottom" round>
      <van-picker title="选择供应商" :columns="supplierColumns" @confirm="onSupplierConfirm" @cancel="showSupplierPicker = false" />
    </van-popup>
    <van-popup v-model:show="showSupplierPicker2" position="bottom" round>
      <van-picker title="选择供应商" :columns="supplierColumns" @confirm="onSupplierConfirm2" @cancel="showSupplierPicker2 = false" />
    </van-popup>
    <van-popup v-model:show="showWhPicker" position="bottom" round>
      <van-picker title="选择仓库" :columns="whColumns" @confirm="onWhConfirm" @cancel="showWhPicker = false" />
    </van-popup>
    <van-popup v-model:show="showStockinPicker" position="bottom" round>
      <van-picker title="选择入库单" :columns="stockinColumns" @confirm="onStockinConfirm" @cancel="showStockinPicker = false" />
    </van-popup>
    <van-popup v-model:show="showProductPicker" position="bottom" round style="max-height:70%">
      <van-search v-model="productSearch" placeholder="搜索商品" />
      <van-list>
        <van-cell v-for="p in filteredProducts" :key="p.id" :title="p.name" :label="'¥' + (p.purchase_price || 0)" clickable @click="addProduct(p)" />
        <van-empty v-if="filteredProducts.length === 0" description="无商品" />
      </van-list>
    </van-popup>
    <van-popup v-model:show="showProductPicker2" position="bottom" round style="max-height:70%">
      <van-search v-model="productSearch2" placeholder="搜索商品" />
      <van-list>
        <van-cell v-for="p in filteredProducts2" :key="p.id" :title="p.name" :label="'¥' + (p.purchase_price || 0)" clickable @click="addProduct2(p)" />
        <van-empty v-if="filteredProducts2.length === 0" description="无商品" />
      </van-list>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import {
  getPurchaseOrders, createPurchaseOrder, getPurchaseOrder,
  orderToStockin, getPurchaseStockins, getPurchaseStockin, confirmPurchaseStockin,
  getPurchaseReturns, createPurchaseReturn, getPurchaseReturn, confirmPurchaseReturn,
  getSuppliers, getWarehouses, getProducts
} from '../api'

const tab = ref(0)
const showCreate = ref(false)
const showReturnForm = ref(false)
const showDetailPopup = ref(false)
const submitting = ref(false)
const showSupplierPicker = ref(false)
const showSupplierPicker2 = ref(false)
const showWhPicker = ref(false)
const showStockinPicker = ref(false)
const showProductPicker = ref(false)
const showProductPicker2 = ref(false)
const productSearch = ref('')
const productSearch2 = ref('')

const orders = ref([])
const stockins = ref([])
const returns = ref([])
const detail = ref({})
const suppliers = ref([])
const warehouses = ref([])
const products = ref([])
const stockinsForReturn = ref([])
const page1 = ref(1), page2 = ref(1), page3 = ref(1)
const loading = ref(false), loading2 = ref(false), loading3 = ref(false)
const finished = ref(false), finished2 = ref(false), finished3 = ref(false)
const refreshing = ref(false), refreshing2 = ref(false), refreshing3 = ref(false)

const form = ref({ supplier_id: null, supplier_name: '', warehouse_id: null, warehouse_name: '', remark: '', items: [] })
const returnForm = ref({ supplier_id: null, supplier_name: '', stockin_id: null, stockin_code: '', warehouse_id: null, remark: '', items: [] })

const supplierColumns = computed(() => suppliers.value.map(s => ({ text: s.name, value: s.id })))
const whColumns = computed(() => warehouses.value.map(w => ({ text: w.name, value: w.id })))
const stockinColumns = computed(() => stockinsForReturn.value.map(s => ({ text: s.code + ' ¥' + (s.total_amount || 0).toFixed(0), value: s.id })))
const filteredProducts = computed(() => {
  if (!productSearch.value) return products.value.slice(0, 30)
  return products.value.filter(p => p.name.includes(productSearch.value) || p.code?.includes(productSearch.value)).slice(0, 30)
})
const filteredProducts2 = computed(() => {
  if (!productSearch2.value) return products.value.slice(0, 30)
  return products.value.filter(p => p.name.includes(productSearch2.value) || p.code?.includes(productSearch2.value)).slice(0, 30)
})
const totalAmount = computed(() => form.value.items.reduce((s, i) => s + (i.quantity || 0) * (i.price || 0), 0).toFixed(2))

const getOrderStatusType = (s) => ({ 0: 'warning', 1: 'primary', 2: 'success', 3: 'info' }[s] || 'default')
const getOrderStatusLabel = (s) => ({ 0: '待入库', 1: '部分入库', 2: '已完成', 3: '已关闭' }[s] || s)
const getStockinStatusType = (s) => ({ 0: 'warning', 1: 'success', 2: 'info' }[s] || 'default')
const getStockinStatusLabel = (s) => ({ 0: '待确认', 1: '已入库', 2: '已作废' }[s] || s)
const getReturnStatusType = (s) => ({ 0: 'warning', 1: 'success', 2: 'info' }[s] || 'default')
const getReturnStatusLabel = (s) => ({ 0: '待确认', 1: '已退货', 2: '已作废' }[s] || s)

const loadOrders = async () => {
  loading.value = true
  try {
    const res = await getPurchaseOrders({ page: page1.value, page_size: 20 })
    if (page1.value === 1) orders.value = res.data || []
    else orders.value.push(...(res.data || []))
    finished.value = (res.data || []).length < 20
    page1.value++
  } catch {}
  loading.value = false
  refreshing.value = false
}

const loadStockins = async () => {
  loading2.value = true
  try {
    const res = await getPurchaseStockins({ page: page2.value, page_size: 20 })
    if (page2.value === 1) stockins.value = res.data || []
    else stockins.value.push(...(res.data || []))
    finished2.value = (res.data || []).length < 20
    page2.value++
  } catch {}
  loading2.value = false
  refreshing2.value = false
}

const loadReturns = async () => {
  loading3.value = true
  try {
    const res = await getPurchaseReturns({ page: page3.value, page_size: 20 })
    if (page3.value === 1) returns.value = res.data || []
    else returns.value.push(...(res.data || []))
    finished3.value = (res.data || []).length < 20
    page3.value++
  } catch {}
  loading3.value = false
  refreshing3.value = false
}

const startCreate = () => {
  form.value = { supplier_id: null, supplier_name: '', warehouse_id: null, warehouse_name: '', remark: '', items: [] }
  showCreate.value = true
}

const startReturn = () => {
  returnForm.value = { supplier_id: null, supplier_name: '', stockin_id: null, stockin_code: '', warehouse_id: null, remark: '', items: [] }
  showReturnForm.value = true
}

const onSupplierConfirm = ({ selectedOptions }) => {
  const s = suppliers.value.find(x => x.id === selectedOptions[0].value)
  form.value.supplier_id = s?.id; form.value.supplier_name = s?.name
  showSupplierPicker.value = false
}

const onSupplierConfirm2 = ({ selectedOptions }) => {
  const s = suppliers.value.find(x => x.id === selectedOptions[0].value)
  returnForm.value.supplier_id = s?.id; returnForm.value.supplier_name = s?.name
  returnForm.value.stockin_id = null; returnForm.value.stockin_code = ''
  showSupplierPicker2.value = false
  loadStockinsForReturn()
}

const onWhConfirm = ({ selectedOptions }) => {
  const w = warehouses.value.find(x => x.id === selectedOptions[0].value)
  form.value.warehouse_id = w?.id; form.value.warehouse_name = w?.name
  showWhPicker.value = false
}

const onStockinConfirm = ({ selectedOptions }) => {
  const s = stockinsForReturn.value.find(x => x.id === selectedOptions[0].value)
  returnForm.value.stockin_id = s?.id; returnForm.value.stockin_code = s?.code
  returnForm.value.warehouse_id = s?.warehouse_id
  showStockinPicker.value = false
}

const loadStockinsForReturn = async () => {
  if (!returnForm.value.supplier_id) return
  const res = await getPurchaseStockins({ supplier_id: returnForm.value.supplier_id, status: 1, page_size: 200 })
  stockinsForReturn.value = res.data || []
}

const addProduct = (p) => {
  if (form.value.items.find(i => i.product_id === p.id)) { showToast('已添加'); return }
  form.value.items.push({ product_id: p.id, product_name: p.name, price: p.purchase_price || 0, quantity: 1 })
  showProductPicker.value = false
}

const addProduct2 = (p) => {
  if (returnForm.value.items.find(i => i.product_id === p.id)) { showToast('已添加'); return }
  returnForm.value.items.push({ product_id: p.id, product_name: p.name, price: p.purchase_price || 0, quantity: 1 })
  showProductPicker2.value = false
}

const handleCreateOrder = async () => {
  if (!form.value.supplier_id) return showToast('请选择供应商')
  if (!form.value.warehouse_id) return showToast('请选择仓库')
  if (!form.value.items.length) return showToast('请添加商品')
  submitting.value = true
  try {
    await createPurchaseOrder({
      supplier_id: form.value.supplier_id, warehouse_id: form.value.warehouse_id,
      remark: form.value.remark,
      items: form.value.items.map(i => ({ product_id: i.product_id, quantity: i.quantity, price: i.price, amount: i.quantity * i.price }))
    })
    showSuccessToast('订单已创建')
    showCreate.value = false
    page1.value = 1; loadOrders()
  } catch { showToast('创建失败') }
  submitting.value = false
}

const handleCreateReturn = async () => {
  if (!returnForm.value.supplier_id) return showToast('请选择供应商')
  if (!returnForm.value.items.length) return showToast('请添加退货商品')
  submitting.value = true
  try {
    await createPurchaseReturn({
      supplier_id: returnForm.value.supplier_id, stockin_id: returnForm.value.stockin_id,
      warehouse_id: returnForm.value.warehouse_id || warehouses.value[0]?.id,
      remark: returnForm.value.remark,
      items: returnForm.value.items.map(i => ({ product_id: i.product_id, quantity: i.quantity, price: i.price, amount: i.quantity * i.price }))
    })
    showSuccessToast('退货单已创建')
    showReturnForm.value = false
    page3.value = 1; loadReturns()
  } catch { showToast('创建失败') }
  submitting.value = false
}

const showOrderDetail = async (o) => {
  const res = await getPurchaseOrder(o.id)
  detail.value = res.data; showDetailPopup.value = true
}

const showStockinDetail = async (s) => {
  const res = await getPurchaseStockin(s.id)
  detail.value = res.data; showDetailPopup.value = true
}

const showReturnDetail = async (r) => {
  const res = await getPurchaseReturn(r.id)
  detail.value = res.data; showDetailPopup.value = true
}

const toStockin = async (o) => {
  try {
    await showConfirmDialog({ title: '生成入库', message: `是否为订单 ${o.code} 生成入库单？` })
    const res = await orderToStockin(o.id)
    showSuccessToast('入库单已生成')
    page2.value = 1; loadStockins()
  } catch {}
}

const confirmStockin = async (s) => {
  try {
    await showConfirmDialog({ title: '确认入库', message: '确认后将增加库存，是否继续？' })
    await confirmPurchaseStockin(s.id)
    showSuccessToast('入库确认成功')
    page2.value = 1; loadStockins()
  } catch {}
}

const confirmReturn = async (r) => {
  try {
    await showConfirmDialog({ title: '确认退货', message: '确认后将扣减库存，是否继续？' })
    await confirmPurchaseReturn(r.id)
    showSuccessToast('退货确认成功')
    page3.value = 1; loadReturns()
  } catch {}
}

onMounted(async () => {
  const [sRes, wRes, pRes] = await Promise.all([getSuppliers(), getWarehouses(), getProducts({ page_size: 100 })])
  suppliers.value = sRes.data || []
  warehouses.value = wRes.data || []
  products.value = pRes.data || []
  loadOrders(); loadStockins(); loadReturns()
})
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.order-card {
  background: #fff; margin: 8px 16px; border-radius: 10px;
  padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.order-no { font-weight: bold; color: #333; font-size: 15px; }
.order-info { display: flex; justify-content: space-between; font-size: 13px; color: #666; margin-top: 4px; }
.total-price { font-size: 20px; font-weight: bold; color: #ff6b35; }
.order-summary {
  display: flex; justify-content: flex-end; align-items: center;
  background: #fff; border-radius: 8px; padding: 12px; margin-top: 8px;
  font-size: 16px; color: #333;
}
</style>
