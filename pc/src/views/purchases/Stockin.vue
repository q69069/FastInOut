<template>
  <div class="order-page">
    <!-- 顶部标题栏 -->
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">采购入库单</span>
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
          <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
          <el-button @click="handleAudit()" v-if="form.id">审核</el-button>
          <el-button @click="handlePrint" v-if="form.id">打印</el-button>
          <el-button @click="handleCopy" v-if="form.id">复制</el-button>
          <el-button @click="resetForm">新增</el-button>
          <el-button @click="handleClose">关闭</el-button>
        </div>
      </div>
    </el-card>

    <!-- 单据主内容 -->
    <el-card class="form-card">
      <!-- 表头区域 -->
      <div class="form-header">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="供应商" required class="form-label-bold">
              <el-select v-model="form.supplier_id" filterable placeholder="搜索供应商" style="width:100%">
                <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
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
            <el-form-item label="采购员" class="form-label-bold">
              <el-select v-model="form.purchaser_id" clearable filterable placeholder="选择采购员" style="width:100%">
                <el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="入库日期" class="form-label-bold">
              <el-date-picker v-model="form.stockin_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
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

      <!-- 商品明细 -->
      <div class="section-title">
        <span>入库明细</span>
      </div>
      <el-table :data="form.items" border size="small" class="items-table" show-summary :summary-method="getSummary">
        <el-table-column type="index" label="序号" width="50" align="center" />
        <el-table-column label="商品名称" min-width="220">
          <template #default="{ row, $index }">
            <el-select v-model="row.product_id" filterable placeholder="搜索商品" style="width:100%" @change="onProductChange($index)">
              <el-option v-for="p in products" :key="p.id" :label="`${p.name}${p.spec ? ' ['+p.spec+']' : ''}`" :value="p.id">
                <span>{{ p.name }}</span>
                <span v-if="p.spec" class="text-muted"> [{{ p.spec }}]</span>
                <span class="text-muted fr">¥{{ p.cost_price || p.retail_price }}</span>
              </el-option>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="条形码" width="120">
          <template #default="{ row }">{{ getProductBarcode(row.product_id) }}</template>
        </el-table-column>
        <el-table-column label="单位" width="110" align="center">
          <template #default="{ row, $index }">
            <el-select v-if="row._availableUnits?.length" v-model="row._unitLevel" size="small" style="width:100px" @change="v => onUnitChange($index, v)">
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
          <template #default="{ row }">{{ getAvailableStock(row) }}</template>
        </el-table-column>
        <el-table-column label="备注" width="100">
          <template #default="{ row }">
            <el-input v-model="row.remark" size="small" placeholder="备注" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ $index }">
            <el-button link type="primary" size="small" @click="copyRow($index)">复制</el-button>
            <el-button link type="danger" size="small" @click="form.items.splice($index, 1)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="add-row-bar">
        <el-button size="small" @click="addItem">+ 添加商品</el-button>
      </div>

      <!-- 金额汇总 -->
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
              <el-input-number v-model="form.discount_amount" :min="0" :precision="2" size="small" controls-position="right" style="width:120px" @change="calcNetAmount" />
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
              <label>入库金额：</label>
              <span class="amount text-danger">¥{{ netAmount.toFixed(2) }}</span>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 查询模式列表 -->
    <el-card class="list-card" v-if="mode === 'query'">
      <div class="section-title">入库记录</div>
      <el-form inline @submit.prevent="loadData" style="margin-bottom:12px">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" clearable placeholder="单据号/供应商" style="width:150px" @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="草稿" :value="0" />
            <el-option label="已入库" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="clearFilter">清空</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column type="index" width="50" align="center" />
        <el-table-column prop="code" label="单据号" width="150" />
        <el-table-column prop="supplier_name" label="供应商" />
        <el-table-column prop="warehouse_name" label="仓库" width="100" />
        <el-table-column prop="total_amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 2 ? 'success' : 'warning'">{{ statusMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="150" :formatter="fmtDate" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showDetail(row)">详情</el-button>
            <el-button link type="success" size="small" v-if="row.status === 0" @click="handleAudit(row)">审核</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total"
        layout="total, prev, pager, next" style="margin-top:16px;justify-content:flex-end" @current-change="loadData" />
    </el-card>

    <DocumentDetail v-model="detailVisible" title="入库单详情"
      :fields="detailFields" :items="detail.items || []" :item-columns="detailItemColumns" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPurchaseStockins, createPurchaseStockin, getPurchaseStockin, confirmPurchaseStockin, getSuppliers, getWarehouses, getEmployees } from '../../api'
import { useAuthStore } from '../../stores/auth'
import DocumentDetail from '../../components/DocumentDetail.vue'
import { useWarehouseProducts } from '../../utils/useWarehouseProducts'

const fmtDateVal = (v) => v ? String(v).replace("T", " ").slice(0, 16) : ""
const buildAvailableUnits = (p) => {
  if (!p) return []
  const baseId = p.base_unit_id || p.id
  const units = [{ unit_id: baseId, unit_level: 'small', unit_name: p.small_unit_name || p.unit || '基本单位', conv_rate: 1 }]
  if (p.medium_unit_name) units.push({ unit_id: baseId, unit_level: 'medium', unit_name: p.medium_unit_name, conv_rate: p.medium_conv_rate || 1 })
  if (p.large_unit_name) units.push({ unit_id: baseId, unit_level: 'large', unit_name: p.large_unit_name, conv_rate: p.large_conv_rate || 1 })
  return units
}
const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')
const statusMap = { 0: '草稿', 1: '已入库', 2: '已入库', 3: '已冲红' }

const mode = ref('create')
const saving = ref(false)
const suppliers = ref([])
const warehouses = ref([])
const form = ref({
  code: '',
  supplier_id: null,
  warehouse_id: null,
  purchaser_id: null,
  stockin_date: '',
  remark: '',
  discount_amount: 0,
  items: [
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 }
  ]
})
const { products, loadProducts } = useWarehouseProducts(() => form.value.warehouse_id)
const employees = ref([])
const list = ref([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref({})

const detailFields = computed(() => {
  const d = detail.value
  if (!d.code) return []
  return [
    { label: '单号', value: d.code },
    { label: '供应商', value: d.supplier_name },
    { label: '仓库', value: d.warehouse_name },
    { label: '状态', value: statusMap[d.status] || '-', type: 'tag', tagType: d.status === 2 ? 'success' : 'warning' },
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

const query = ref({ page: 1, page_size: 20, keyword: '', status: null })

const totalAmount = computed(() => {
  return form.value.items.reduce((s, item) => s + (item.quantity || 0) * (item.price || 0), 0)
})

const netAmount = computed(() => {
  return (totalAmount.value || 0) - (form.value.discount_amount || 0)
})

const getSummary = ({ columns, data }) => {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (col.property === 'amount') {
      sums[idx] = `¥${totalAmount.value.toFixed(2)}`
    }
  })
  return sums
}

const getProductBarcode = (productId) => {
  const p = products.value.find(x => x.id === productId)
  return p?.barcode || '-'
}

const getAvailableStock = (row) => {
  const p = products.value.find(x => x.id === row.product_id)
  const stock = p?.available_stock || p?.stock || 0
  const rate = row._unitConvRate || 1
  return rate > 1 ? (stock / rate).toFixed(2) : stock.toFixed(2)
}

const onProductChange = (index) => {
  const row = form.value.items[index]
  const p = products.value.find(x => x.id === row.product_id)
  if (p) {
    row.price = p.cost_price || p.retail_price || 0
    row._basePrice = row.price
    row._availableUnits = buildAvailableUnits(p)
    if (row._availableUnits.length > 0) {
      const defaultUnit = row._availableUnits.find(u => u.unit_level === p.default_unit_level) || row._availableUnits[0]
      row.unit_id = defaultUnit.unit_id
      row._unitLevel = defaultUnit.unit_level
      row._unitConvRate = defaultUnit.conv_rate
      row.price = parseFloat((row._basePrice * defaultUnit.conv_rate).toFixed(2))
    }
    calcRowAmount(row)
  }
}

const onUnitChange = (index, unitLevel) => {
  const row = form.value.items[index]
  const unit = row._availableUnits?.find(u => u.unit_level === unitLevel)
  if (unit && row._basePrice) {
    row._unitLevel = unit.unit_level
    row._unitConvRate = unit.conv_rate
    row.price = parseFloat((row._basePrice * unit.conv_rate).toFixed(2))
    row.price = parseFloat((row._basePrice * unit.conv_rate).toFixed(2))
  }
  calcRowAmount(row)
}

const calcRowAmount = (row) => {
  row.amount = (row.quantity || 0) * (row.price || 0)
}

const calcNetAmount = () => {}

const addItem = () => {
  form.value.items.push({ product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 })
}

const copyRow = (index) => {
  const item = { ...form.value.items[index] }
  form.value.items.splice(index + 1, 0, item)
}

const resetForm = () => {
  form.value = {
    code: '',
    supplier_id: null,
    warehouse_id: null,
    purchaser_id: null,
    stockin_date: '',
    remark: '',
    discount_amount: 0,
    items: [
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 }
  ]
  }
  mode.value = 'create'
}

const handleSave = async () => {
  if (!form.value.supplier_id) return ElMessage.warning('请选择供应商')
  if (!form.value.warehouse_id) return ElMessage.warning('请选择仓库')
  const validItems = form.value.items.filter(i => i.product_id && i.quantity > 0)
  if (validItems.length === 0) return ElMessage.warning('请添加商品')

  saving.value = true
  try {
    const data = {
      ...form.value,
      items: validItems.map(i => {
        return {
          product_id: i.product_id,
          quantity: i.quantity,
          price: i.price,
          amount: (i.quantity || 0) * (i.price || 0),
          remark: i.remark,
          unit_id: i.unit_id || null,
          unit_level: i._unitLevel || 'small',
          unit_conv_rate: i._unitConvRate || 1,
          unit_quantity: i.quantity
        }
      })
    }
    await createPurchaseStockin(data)
    ElMessage.success('保存成功')
    resetForm()
    loadData()
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleAudit = async (row) => {
  const id = row?.id || form.value?.id
  if (!id) return ElMessage.warning('请先保存单据')
  await ElMessageBox.confirm('确认审核该入库单？', '审核确认', { type: 'warning' })
  await confirmPurchaseStockin(id)
  ElMessage.success({ message: '审核成功', duration: 1500 })
  loadData()
}

const handlePrint = () => {
  ElMessage.info('打印功能开发中')
}

const handleCopy = () => {
  ElMessage.info('复制功能开发中')
}

const handleClose = () => {
  mode.value = 'query'
  loadData()
}

const clearFilter = () => {
  query.value = { page: 1, page_size: 20, keyword: '', status: null }
  loadData()
}

const loadData = async () => {
  const params = { ...query.value }
  if (!params.status) delete params.status
  if (!params.keyword) delete params.keyword
  const res = await getPurchaseStockins(params)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDetail = async (row) => {
  const res = await getPurchaseStockin(row.id)
  detail.value = res.data || res
  detailVisible.value = true
}

onMounted(async () => {
  const [s, w, e] = await Promise.all([
    getSuppliers({ page_size: 1000 }),
    getWarehouses({ page_size: 100 }),
    getEmployees({ page_size: 100 })
  ])
  suppliers.value = s.data?.list || s.data || []
  warehouses.value = w.data?.list || w.data || []
  employees.value = e.data?.list || e.data || []
  await loadProducts()
  loadData()
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
