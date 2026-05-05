<template>
  <div class="page">
    <van-nav-bar title="采购退货出库" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startCreate" />
      </template>
    </van-nav-bar>

    <van-tabs v-model:active="tab" sticky>
      <van-tab title="待确认">
        <van-pull-refresh v-model="loading" @refresh="loadList">
          <van-list :finished="finished" finished-text="没有更多了" @load="loadList">
            <div v-for="item in pendingList" :key="item.id" class="dlv-card" @click="openDetail(item)">
              <div class="dlv-header">
                <span class="dlv-no">{{ item.return_dlv_no }}</span>
                <van-tag type="warning">{{ item.status_text }}</van-tag>
              </div>
              <div class="dlv-body">
                <div class="info-row"><span>供应商</span><span>{{ item.supplier_name }}</span></div>
                <div class="info-row"><span>退货金额</span><span class="red">¥{{ (item.total_amount || 0).toFixed(2) }}</span></div>
                <div class="info-row"><span>创建时间</span><span>{{ item.created_at?.substring(0, 16) }}</span></div>
              </div>
              <div v-if="item.status === 'pending'" style="display:flex;gap:8px;margin-top:8px">
                <van-button type="primary" size="small" @click.stop="handleWarehouseConfirm(item)">仓管确认</van-button>
                <van-button type="danger" plain size="small" @click.stop="handleDelete(item)">删除</van-button>
              </div>
            </div>
            <van-empty v-if="pendingList.length === 0 && !loading" description="暂无待确认退货" />
          </van-list>
        </van-pull-refresh>
      </van-tab>

      <van-tab title="已完成">
        <van-pull-refresh v-model="loading2" @refresh="loadCompleted">
          <van-list :finished="finished2" finished-text="没有更多了" @load="loadCompleted">
            <div v-for="item in completedList" :key="item.id" class="dlv-card" @click="openDetail(item)">
              <div class="dlv-header">
                <span class="dlv-no">{{ item.return_dlv_no }}</span>
                <van-tag :type="item.status === 'settled' ? 'success' : 'primary'">{{ item.status_text }}</van-tag>
              </div>
              <div class="dlv-body">
                <div class="info-row"><span>供应商</span><span>{{ item.supplier_name }}</span></div>
                <div class="info-row"><span>退货金额</span><span class="red">¥{{ (item.total_amount || 0).toFixed(2) }}</span></div>
                <div class="info-row"><span>状态</span><span>{{ item.status_text }}</span></div>
              </div>
            </div>
            <van-empty v-if="completedList.length === 0 && !loading2" description="暂无已完成退货" />
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>

    <!-- 新建退货出库 -->
    <van-popup v-model:show="showCreate" position="bottom" round style="max-height:85%">
      <div style="padding:16px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">新建退货出库单</div>
        <van-cell-group inset>
          <van-cell title="供应商" is-link :value="selectedSupplierName || '请选择'" @click="showSupplierPicker = true" />
          <van-cell title="仓库" is-link :value="selectedWarehouseName || '请选择'" @click="showWhPicker = true" />
          <van-field v-model="form.remark" label="备注" placeholder="退货原因备注" rows="2" type="textarea" />
        </van-cell-group>

        <div class="items-section">
          <div style="display:flex;justify-content:space-between;align-items:center;margin:12px 0 8px">
            <span style="font-weight:bold">退货商品</span>
            <van-button size="small" type="primary" @click="showProductPicker = true">添加商品</van-button>
          </div>
          <div v-for="(item, idx) in form.items" :key="idx" class="item-row">
            <span class="item-name">{{ item.product_name }}</span>
            <span class="item-qty">{{ item.quantity }} × ¥{{ item.unit_price }}</span>
            <van-icon name="close" @click="form.items.splice(idx, 1)" />
          </div>
          <div v-if="form.items.length === 0" style="color:#999;text-align:center;padding:12px">请添加退货商品</div>
        </div>

        <div style="display:flex;gap:12px;margin-top:16px">
          <van-button block @click="showCreate = false">取消</van-button>
          <van-button type="danger" block :loading="submitting" @click="submitDlv">提交出库</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 供应商选择 -->
    <van-popup v-model:show="showSupplierPicker" position="bottom" round>
      <van-picker title="选择供应商" :columns="supplierColumns" @confirm="onSupplierConfirm" @cancel="showSupplierPicker = false" />
    </van-popup>

    <!-- 仓库选择 -->
    <van-popup v-model:show="showWhPicker" position="bottom" round>
      <van-picker title="选择仓库" :columns="whColumns" @confirm="onWhConfirm" @cancel="showWhPicker = false" />
    </van-popup>

    <!-- 商品选择 -->
    <van-popup v-model:show="showProductPicker" position="bottom" round style="max-height:70%">
      <div style="padding:16px">
        <div style="font-weight:bold;text-align:center;margin-bottom:12px">选择商品</div>
        <van-search v-model="productKeyword" placeholder="搜索商品" @search="loadProducts" style="margin-bottom:8px" />
        <van-list :finished="productFinished" @load="loadProducts">
          <div v-for="p in productList" :key="p.id" class="product-item" @click="addProduct(p)">
            <span>{{ p.name }}</span>
            <span class="green">¥{{ (p.price || 0).toFixed(2) }}</span>
          </div>
        </van-list>
      </div>
    </van-popup>

    <!-- 详情 -->
    <van-popup v-model:show="showDetail" position="bottom" round style="max-height:70%">
      <div style="padding:16px" v-if="detailItem">
        <h3>退货出库单详情</h3>
        <van-cell-group style="margin-top:12px">
          <van-cell title="单号" :value="detailItem.return_dlv_no" />
          <van-cell title="供应商" :value="detailItem.supplier_name" />
          <van-cell title="状态">
            <template #value><van-tag :type="getStatusType(detailItem.status)">{{ detailItem.status_text }}</van-tag></template>
          </van-cell>
          <van-cell title="总金额" :value="'¥' + (detailItem.total_amount || 0).toFixed(2)" />
          <van-cell title="备注" :value="detailItem.remark || '-'" />
        </van-cell-group>
        <div style="margin-top:12px">
          <div style="font-weight:bold;margin-bottom:8px">商品明细</div>
          <div v-for="item in detailItem.items" :key="item.id" class="item-row">
            <span>{{ item.product_name }}</span>
            <span>{{ item.quantity }} × ¥{{ item.unit_price }}</span>
          </div>
        </div>
        <div style="display:flex;gap:8px;margin-top:16px">
          <van-button v-if="detailItem.status === 'pending'" type="primary" block @click="handleWarehouseConfirm(detailItem)">仓管确认</van-button>
          <van-button v-if="detailItem.status === 'warehouse_confirmed'" type="success" block @click="handleFinanceConfirm(detailItem)">财务确认</van-button>
          <van-button block @click="showDetail = false">关闭</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getPurchaseReturnDlvs, createPurchaseReturnDlv, warehouseConfirmDlv, financeConfirmDlv, deletePurchaseReturnDlv, getSuppliers, getWarehouses, getProducts } from '../api'

const tab = ref(0)
const loading = ref(false)
const loading2 = ref(false)
const finished = ref(false)
const finished2 = ref(false)
const pendingList = ref([])
const completedList = ref([])
const showCreate = ref(false)
const showDetail = ref(false)
const showSupplierPicker = ref(false)
const showWhPicker = ref(false)
const showProductPicker = ref(false)
const submitting = ref(false)

const suppliers = ref([])
const warehouses = ref([])
const products = ref([])
const productList = ref([])
const productKeyword = ref('')
const productFinished = ref(false)

const selectedSupplierName = ref('')
const selectedWarehouseName = ref('')

const form = ref({ supplier_id: null, warehouse_id: null, remark: '', items: [] })

const supplierColumns = computed(() => suppliers.value.map(s => ({ text: s.name, value: s.id })))
const whColumns = computed(() => warehouses.value.map(w => ({ text: w.name, value: w.id })))

const getStatusType = (status) => ({ pending: 'warning', warehouse_confirmed: 'primary', finance_confirmed: 'success', settled: 'success' }[status] || 'default')

const loadList = async () => {
  loading.value = true
  try {
    const res = await getPurchaseReturnDlvs({ status: 'pending', page_size: 50 })
    pendingList.value = res.data || []
  } catch {}
  loading.value = false
  finished.value = true
}

const loadCompleted = async () => {
  loading2.value = true
  try {
    const res = await getPurchaseReturnDlvs({ page_size: 50 })
    const all = res.data || []
    completedList.value = all.filter(i => i.status !== 'pending')
  } catch {}
  loading2.value = false
  finished2.value = true
}

const loadSuppliers = async () => {
  const res = await getSuppliers({ page_size: 100 })
  suppliers.value = res.data || []
}

const loadWarehouses = async () => {
  const res = await getWarehouses()
  warehouses.value = res.data || []
}

const loadProducts = async () => {
  const res = await getProducts({ keyword: productKeyword.value, page_size: 50 })
  productList.value = res.data || []
  productFinished.value = true
}

const startCreate = () => {
  form.value = { supplier_id: null, warehouse_id: null, remark: '', items: [] }
  selectedSupplierName.value = ''
  selectedWarehouseName.value = ''
  showCreate.value = true
}

const onSupplierConfirm = ({ selectedOptions }) => {
  form.value.supplier_id = selectedOptions[0].value
  selectedSupplierName.value = selectedOptions[0].text
  showSupplierPicker.value = false
}

const onWhConfirm = ({ selectedOptions }) => {
  form.value.warehouse_id = selectedOptions[0].value
  selectedWarehouseName.value = selectedOptions[0].text
  showWhPicker.value = false
}

const addProduct = (p) => {
  const exists = form.value.items.find(i => i.product_id === p.id)
  if (exists) return showToast('已添加该商品')
  form.value.items.push({ product_id: p.id, product_name: p.name, quantity: 1, unit_price: p.price || 0, amount: p.price || 0 })
  showProductPicker.value = false
}

const submitDlv = async () => {
  if (!form.value.supplier_id) return showToast('请选择供应商')
  if (!form.value.warehouse_id) return showToast('请选择仓库')
  if (form.value.items.length === 0) return showToast('请添加退货商品')
  submitting.value = true
  try {
    const total_amount = form.value.items.reduce((s, i) => s + (i.quantity * i.unit_price), 0)
    await createPurchaseReturnDlv({
      supplier_id: form.value.supplier_id,
      warehouse_id: form.value.warehouse_id,
      remark: form.value.remark,
      items: form.value.items.map(i => ({
        product_id: i.product_id,
        quantity: i.quantity,
        unit_price: i.unit_price
      })),
      total_amount
    })
    showSuccessToast('退货出库单已创建')
    showCreate.value = false
    loadList()
  } catch { showToast('创建失败') }
  submitting.value = false
}

const openDetail = async (item) => {
  try {
    const res = await getPurchaseReturnDlv(item.id)
    detailItem.value = res.data
    showDetail.value = true
  } catch {}
}

const detailItem = ref(null)

const handleWarehouseConfirm = async (item) => {
  try {
    await showConfirmDialog({ title: '仓管确认', message: `确认退货出库单 ${item.return_dlv_no}？` })
    await warehouseConfirmDlv(item.id)
    showSuccessToast('仓管已确认')
    showDetail.value = false
    loadList()
    loadCompleted()
  } catch {}
}

const handleFinanceConfirm = async (item) => {
  try {
    await showConfirmDialog({ title: '财务确认', message: `确认财务冲账 ${item.return_dlv_no}？` })
    await financeConfirmDlv(item.id)
    showSuccessToast('财务已确认')
    showDetail.value = false
    loadCompleted()
  } catch {}
}

const handleDelete = async (item) => {
  try {
    await showConfirmDialog({ title: '删除', message: `确认删除退货出库单 ${item.return_dlv_no}？` })
    await deletePurchaseReturnDlv(item.id)
    showSuccessToast('已删除')
    loadList()
  } catch {}
}

onMounted(async () => {
  await Promise.all([loadSuppliers(), loadWarehouses()])
  loadList()
  loadCompleted()
})
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.dlv-card { background: #fff; margin: 8px 16px; border-radius: 10px; padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); cursor: pointer; }
.dlv-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.dlv-no { font-weight: bold; font-size: 14px; color: #333; }
.dlv-body { border-top: 1px solid #f5f5f5; padding-top: 6px; }
.info-row { display: flex; justify-content: space-between; padding: 2px 0; font-size: 13px; color: #666; }
.red { color: #ee0a24; }
.items-section { background: #f7f8fa; border-radius: 8px; padding: 8px 12px; margin-top: 8px; }
.item-row { display: flex; align-items: center; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f0f0f0; font-size: 13px; }
.item-name { flex: 1; color: #333; }
.item-qty { color: #666; margin-right: 8px; }
.product-item { display: flex; justify-content: space-between; padding: 12px; border-bottom: 1px solid #f5f5f5; cursor: pointer; }
.product-item:hover { background: #f7f8fa; }
.green { color: #07c160; font-weight: bold; }
</style>