<template>
  <div class="order-page">
    <el-card class="header-card" style="position:relative">
      <DocumentStamp :status="form.status" />
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">销售出库单</span>
        </div>
        <div class="header-meta">
          <div class="meta-row">
            <span class="meta-item">单据编号：<em class="text-primary">{{ form.code || '（自动生成）' }}</em></span>
            <span class="meta-item">制单：<em>{{ authStore.displayName }}</em></span>
            <span class="meta-item">日期：<em>{{ now }}</em></span>
            <span class="meta-item">审核：<em class="text-muted">{{ form.auditor_name || '待审核' }}</em></span>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleSave" :loading="saving" v-if="!form.id || form.status === 0">保存</el-button>
          <el-button type="success" @click="handleConfirm" v-if="form.id && form.status === 0">确认出库</el-button>
          <el-button @click="showReverseDialog = true" v-if="form.id && form.status > 0 && form.status !== 3" type="danger">冲红</el-button>
          <el-button @click="handlePrint" v-if="form.id">打印</el-button>
          <el-button @click="handleCopy" v-if="form.id">复制</el-button>
          <el-button @click="resetForm">新增</el-button>
          <el-button @click="handleClose">关闭</el-button>
        </div>
      </div>
    </el-card>
    <ReverseDialog v-model="showReverseDialog" @confirm="handleReverse" />

    <el-card class="form-card">
      <div class="form-header">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="客户" required class="form-label-bold">
              <el-select v-model="form.customer_id" filterable placeholder="搜索客户" style="width:100%">
                <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="仓库" required class="form-label-bold">
              <el-select v-model="form.warehouse_id" filterable placeholder="选择仓库" style="width:100%">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="业务员" class="form-label-bold">
              <el-select v-model="form.salesman_id" clearable filterable placeholder="选择业务员" style="width:100%">
                <el-option v-for="s in salesmen" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="出库日期" class="form-label-bold">
              <el-date-picker v-model="form.stockout_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="备注" class="form-label-bold">
              <el-input v-model="form.remark" placeholder="填写备注信息" />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <div class="section-title"><span>出库明细</span></div>
      <el-table :data="form.items" border size="small" class="items-table" show-summary :summary-method="getSummary">
        <el-table-column type="index" label="序号" width="50" align="center" />
        <el-table-column label="商品名称" min-width="220">
          <template #default="{ row, $index }">
            <el-select v-model="row.product_id" filterable placeholder="搜索商品" style="width:100%" @change="handleProductChange($index)">
              <el-option v-for="p in products" :key="p.id" :label="`${p.name}${p.spec ? ' ['+p.spec+']' : ''}`" :value="p.id">
                <span>{{ p.name }}</span>
                <span v-if="p.spec" class="text-muted"> [{{ p.spec }}]</span>
                <span class="text-muted fr">¥{{ p.retail_price }}</span>
              </el-option>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="条形码" width="120">
          <template #default="{ row }">{{ getProductBarcode(products, row.product_id) }}</template>
        </el-table-column>
        <el-table-column label="单位" width="110" align="center">
          <template #default="{ row, $index }">
            <el-select v-if="row._availableUnits?.length" v-model="row._unitLevel" size="small" style="width:100px" @change="v => handleUnitChange($index, v)">
              <el-option v-for="u in row._availableUnits" :key="u.unit_level" :label="u.unit_name" :value="u.unit_level" />
            </el-select>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="数量" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.quantity" :min="1" size="small" style="width:120px" @change="calcRowAmount(row)" />
          </template>
        </el-table-column>
        <el-table-column label="单价" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.price" :min="0" :precision="2" size="small" style="width:120px" @change="calcRowAmount(row)" />
          </template>
        </el-table-column>
        <el-table-column label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ (row.amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="可用库存" width="90" align="right">
          <template #default="{ row }">{{ getAvailableStock(products, row.product_id, row._unitConvRate) }}</template>
        </el-table-column>
        <el-table-column label="备注" width="100">
          <template #default="{ row }">
            <el-input v-model="row.remark" size="small" placeholder="备注" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ $index }">
            <el-button link type="primary" size="small" @click="copyRow(form.items, $index)">复制</el-button>
            <el-button link type="danger" size="small" @click="form.items.splice($index, 1)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="add-row-bar">
        <el-button size="small" @click="addItem">+ 添加商品</el-button>
      </div>

      <div class="amount-summary">
        <el-row :gutter="24">
          <el-col :span="6">
            <div class="summary-item">
              <label>商品金额：</label>
              <span class="amount">¥{{ totalAmount.toFixed(2) }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <label>优惠金额：</label>
              <el-input-number v-model="form.discount_amount" :min="0" :precision="2" size="small" controls-position="right" style="width:120px" />
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <label>优惠后金额：</label>
              <span class="amount text-primary">¥{{ netAmount.toFixed(2) }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <label>应收金额：</label>
              <span class="amount text-danger">¥{{ netAmount.toFixed(2) }}</span>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <el-card class="list-card" v-if="mode === 'query'">
      <div class="section-title">出库记录</div>
      <el-form inline @submit.prevent="loadList" style="margin-bottom:12px">
        <el-form-item label="关键词">
          <el-input v-model="listQuery.keyword" clearable placeholder="单据号/客户" style="width:150px" @keyup.enter="loadList" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="listQuery.status" clearable placeholder="全部" style="width:120px">
            <el-option label="草稿" :value="0" />
            <el-option label="已出库" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">查询</el-button>
          <el-button @click="clearListFilter">清空</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column type="index" width="50" align="center" />
        <el-table-column prop="code" label="单据号" width="150" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="warehouse_name" label="仓库" width="100" />
        <el-table-column prop="total_amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="150" :formatter="fmtDate" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showDetail(row)">详情</el-button>
            <el-button link type="success" size="small" v-if="row.status === 0" @click="handleConfirm(row)">确认出库</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="listQuery.page" v-model:page-size="listQuery.page_size" :total="listTotal"
        layout="total, prev, pager, next" style="margin-top:16px;justify-content:flex-end" @current-change="loadList" />
    </el-card>

    <DocumentDetail v-model="detailVisible" title="出库单详情"
      :fields="detailFields" :items="detail.items || []" :item-columns="detailItemColumns" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getSalesStockouts, createSalesStockout, getSalesStockout, updateSalesStockout,
  confirmSalesStockout, reverseSalesStockout, deleteSalesStockout,
  getCustomers, getWarehouses, getSalesmen
} from '../../api'
import { useAuthStore } from '../../stores/auth'
import DocumentStamp from '../../components/DocumentStamp.vue'
import ReverseDialog from '../../components/ReverseDialog.vue'
import DocumentDetail from '../../components/DocumentDetail.vue'
import { useWarehouseProducts } from '../../utils/useWarehouseProducts'
import {
  buildAvailableUnits, onProductChange as _onProductChange, onUnitChange as _onUnitChange,
  calcRowAmount, copyRow, createEmptyRows, fmtDate, fmtDateVal,
  getProductBarcode, getAvailableStock, stockStatusMap, makeSummaryMethod
} from '../../utils/document'

const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')
const showReverseDialog = ref(false)
const statusMap = stockStatusMap

const mode = ref('create')
const saving = ref(false)
const customers = ref([])
const warehouses = ref([])
const form = ref({
  code: '',
  customer_id: null,
  warehouse_id: null,
  salesman_id: null,
  stockout_date: '',
  remark: '',
  discount_amount: 0,
  status: null,
  items: createEmptyRows(5)
})
const { products, loadProducts } = useWarehouseProducts(() => form.value.warehouse_id)
const salesmen = ref([])
const list = ref([])
const listTotal = ref(0)
const detailVisible = ref(false)
const detail = ref({})

const listQuery = ref({ page: 1, page_size: 20, keyword: '', status: null })

const totalAmount = computed(() => form.value.items.reduce((s, i) => s + (i.quantity || 0) * (i.price || 0), 0))
const netAmount = computed(() => (totalAmount.value || 0) - (form.value.discount_amount || 0))
const getSummary = makeSummaryMethod()

const handleProductChange = (index) => {
  const row = form.value.items[index]
  const p = products.value.find(x => x.id === row.product_id)
  if (p) _onProductChange(row, p, 'retail_price')
}

const handleUnitChange = (index, unitLevel) => {
  _onUnitChange(form.value.items[index], unitLevel)
}

const addItem = () => {
  form.value.items.push(...createEmptyRows(1))
}

const resetForm = () => {
  form.value = {
    code: '', customer_id: null, warehouse_id: null, salesman_id: null,
    stockout_date: '', remark: '', discount_amount: 0, status: null,
    items: createEmptyRows(5)
  }
  mode.value = 'create'
}

const handleSave = async () => {
  if (!form.value.customer_id) return ElMessage.warning('请选择客户')
  if (!form.value.warehouse_id) return ElMessage.warning('请选择仓库')
  const validItems = form.value.items.filter(i => i.product_id && i.quantity > 0)
  if (!validItems.length) return ElMessage.warning('请添加商品')

  saving.value = true
  try {
    const data = {
      customer_id: form.value.customer_id,
      warehouse_id: form.value.warehouse_id,
      salesman_id: form.value.salesman_id,
      stockout_date: form.value.stockout_date,
      remark: form.value.remark,
      discount_amount: form.value.discount_amount || 0,
      items: validItems.map(i => ({
        product_id: i.product_id,
        quantity: i.quantity,
        price: i.price,
        amount: (i.quantity || 0) * (i.price || 0),
        remark: i.remark,
        unit_id: i.unit_id || null,
        unit_level: i._unitLevel || 'small',
        unit_conv_rate: i._unitConvRate || 1,
        unit_quantity: i.quantity
      }))
    }
    if (form.value.id) {
      await updateSalesStockout(form.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createSalesStockout(data)
      ElMessage.success('保存成功')
    }
    resetForm()
    loadList()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleConfirm = async (row) => {
  const id = row?.id || form.value?.id
  if (!id) return
  await ElMessageBox.confirm('确认出库？库存将减少！', '确认操作', { type: 'warning' })
  await confirmSalesStockout(id)
  ElMessage.success('出库确认成功')
  if (form.value.id === id) loadOrder(id)
  loadList()
}

const handleReverse = async (reason) => {
  if (!form.value.id) return
  await reverseSalesStockout(form.value.id, { reason })
  ElMessage.success('冲红成功')
  loadOrder(form.value.id)
  loadList()
}

const handlePrint = () => ElMessage.info('打印功能开发中')

const handleCopy = () => {
  const data = { ...form.value }
  delete data.id
  delete data.code
  delete data.status
  data.items = data.items.map(i => ({ ...i }))
  form.value = data
  mode.value = 'create'
  ElMessage.success('已复制，请修改后保存')
}

const handleClose = () => {
  mode.value = 'query'
  loadList()
}

const loadList = async () => {
  const params = { ...listQuery.value }
  if (!params.status && params.status !== 0) delete params.status
  if (!params.keyword) delete params.keyword
  const res = await getSalesStockouts(params)
  list.value = res.data || []
  listTotal.value = res.total || 0
}

const clearListFilter = () => {
  listQuery.value = { page: 1, page_size: 20, keyword: '', status: null }
  loadList()
}

const loadOrder = async (id) => {
  const res = await getSalesStockout(id)
  const d = res.data || res
  form.value = {
    ...d,
    items: (d.items || []).map(i => ({
      ...i,
      _availableUnits: buildAvailableUnits(i.product || {}),
      _basePrice: i.price || 0,
      _unitLevel: i.unit_level || 'small',
      _unitConvRate: i.unit_conv_rate || 1
    }))
  }
  if (!form.value.items.length) form.value.items = createEmptyRows(5)
  mode.value = 'edit'
}

const showDetail = async (row) => {
  const res = await getSalesStockout(row.id)
  detail.value = res.data || res
  detailVisible.value = true
}

const detailFields = computed(() => {
  const d = detail.value
  if (!d.code) return []
  return [
    { label: '单号', value: d.code },
    { label: '客户', value: d.customer_name },
    { label: '仓库', value: d.warehouse_name },
    { label: '状态', value: statusMap[d.status]?.label, type: 'tag', tagType: statusMap[d.status]?.type },
    { label: '创建时间', value: fmtDateVal(d.created_at) },
    { label: '备注', value: d.remark, span: 2 }
  ]
})

const detailItemColumns = [
  { prop: 'product_name', label: '商品', minWidth: 150 },
  { prop: 'quantity', label: '数量', width: 80, align: 'right' },
  { prop: 'price', label: '单价', width: 80, align: 'right', type: 'money' },
  { prop: 'amount', label: '金额', width: 100, align: 'right', type: 'money' }
]

onMounted(async () => {
  const [c, w, s] = await Promise.all([
    getCustomers({ page_size: 1000 }),
    getWarehouses({ page_size: 100 }),
    getSalesmen({ page_size: 100 })
  ])
  customers.value = c.data?.list || c.data || []
  warehouses.value = w.data?.list || w.data || []
  salesmen.value = s.data?.list || s.data || []
  await loadProducts()
  loadList()
})
</script>

<style scoped>
.order-page { padding: 12px; background: #f5f5f5; min-height: 100vh }
.header-card { margin-bottom: 12px }
.page-header { display: flex; align-items: center; gap: 16px; flex-wrap: wrap }
.page-title { display: flex; align-items: center; gap: 12px }
.title-text { font-size: 18px; font-weight: 600; color: #303133 }
.header-meta { flex: 1 }
.meta-row { display: flex; gap: 24px; color: #606266; font-size: 13px }
.meta-item em { font-style: normal }
.meta-item .text-primary { color: #409eff }
.meta-item .text-muted { color: #909399 }
.header-actions { display: flex; gap: 8px; flex-wrap: wrap }
.form-card { margin-bottom: 12px }
.form-header { margin-bottom: 16px; background: #fafafa; padding: 16px; border-radius: 4px }
.form-label-bold :deep(.el-form-item__label) { font-weight: 600; color: #303133 }
.section-title { font-size: 14px; font-weight: 600; color: #303133; margin: 16px 0 10px; display: flex; align-items: center; gap: 8px }
.items-table { margin-bottom: 8px }
.add-row-bar { padding: 8px 0; display: flex; align-items: center; gap: 8px }
.text-muted { color: #909399; font-size: 12px }
.fr { float: right }
.amount-summary { background: #f5f7fa; padding: 16px; border-radius: 4px; margin-top: 16px }
.summary-item { display: flex; align-items: center; gap: 8px; height: 32px }
.summary-item label { font-weight: 600; color: #606266; min-width: 80px }
.summary-item .amount { font-size: 16px; font-weight: 600 }
.text-primary { color: #409eff }
.text-danger { color: #f56c6c }
.list-card { margin-top: 12px }
</style>
