<template>
  <div class="order-page">
    <!-- 顶部标题栏 -->
    <el-card class="header-card" style="position:relative">
      <DocumentStamp :status="form.status" />
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">装车调度</span>
        </div>
        <div class="header-meta">
          <div class="meta-row">
            <span class="meta-item">单据编号：<em class="text-primary">{{ form.load_no || '（自动生成）' }}</em></span>
            <span class="meta-item">制单：<em>{{ authStore.displayName }}</em></span>
            <span class="meta-item">日期：<em>{{ now }}</em></span>
            <span class="meta-item">审核：<em class="text-muted">{{ form.auditor_name || '待审核' }}</em></span>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleSave" :loading="saving" v-if="!form.id || form.status === '' || form.status === 'draft' || form.status === 'loaded'">保存</el-button>
          <el-button @click="handleAudit()" v-if="form.id && (form.status === '' || form.status === 'draft')">审核</el-button>
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
          <el-col :span="8">
            <el-form-item label="来源仓库" required class="form-label-bold">
              <el-select v-model="form.from_warehouse_id" filterable placeholder="选择仓库" style="width:100%">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="目标车仓" required class="form-label-bold">
              <el-select v-model="form.vehicle_warehouse_id" filterable placeholder="选择车仓" style="width:100%">
                <el-option v-for="w in vehicleWarehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="业务员" class="form-label-bold">
              <el-select v-model="form.employee_id" clearable filterable placeholder="选择业务员" style="width:100%">
                <el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="24">
            <el-form-item label="备注" class="form-label-bold">
              <el-input v-model="form.remark" placeholder="填写备注信息" />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 商品明细 -->
      <div class="section-title">
        <span>装车明细</span>
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
        <el-table-column label="装车数量" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.quantity" :min="1" size="small" style="width:120px" @change="calcRowAmount(row)" />
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

      <!-- 汇总 -->
      <div class="amount-summary">
        <el-row :gutter="24">
          <el-col :span="6">
            <div class="summary-item">
              <label>商品数量：</label>
              <span class="amount">{{ totalQuantity }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <label>商品金额：</label>
              <span class="amount">¥{{ totalAmount.toFixed(2) }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <label>单据状态：</label>
              <el-tag :type="statusTagType(form.status)">{{ statusMap[form.status] || '草稿' }}</el-tag>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 查询模式列表 -->
    <el-card class="list-card" v-if="mode === 'query'">
      <div class="section-title">装车记录</div>
      <el-form inline @submit.prevent="loadData" style="margin-bottom:12px">
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="草稿" value="draft" />
            <el-option label="已装车" value="loaded" />
            <el-option label="已退库" value="returned" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="clearFilter">清空</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column type="index" width="50" align="center" />
        <el-table-column prop="load_no" label="单据号" width="150" />
        <el-table-column prop="from_warehouse_name" label="来源仓库" />
        <el-table-column prop="vehicle_warehouse_name" label="目标车仓" />
        <el-table-column prop="employee_name" label="业务员" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="150" :formatter="fmtDate" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showDetail(row)">详情</el-button>
            <el-button link type="success" size="small" v-if="row.status === 'draft'" @click="handleAudit(row)">审核</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total"
        layout="total, prev, pager, next" style="margin-top:16px;justify-content:flex-end" @current-change="loadData" />
    </el-card>

    <!-- 详情弹窗（支持多开） -->
    <el-dialog v-for="d in openDetails" :key="d.id" v-model="d.visible" :title="`装车单详情 - ${d.data.load_no || ''}`" width="700px">
      <el-descriptions :column="2" border v-if="d.data">
        <el-descriptions-item label="单号">{{ d.data.load_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTagType(d.data.status)">{{ statusMap[d.data.status] }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="来源仓库">{{ d.data.from_warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="目标车仓">{{ d.data.vehicle_warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="业务员">{{ d.data.employee_name }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ fmtDateVal(d.data.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ d.data.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-table v-if="d.data.items?.length" :data="d.data.items" border size="small" style="margin-top:16px">
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="product_unit" label="单位" width="70" align="center" />
        <el-table-column prop="quantity" label="装车数量" width="100" align="right" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useWarehouseProducts } from '../../utils/useWarehouseProducts'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getVehicleLoads, createVehicleLoad, updateVehicleLoad, confirmVehicleLoad, returnVehicleLoad, getVehicleLoad, getWarehouses, getEmployees } from '../../api'
import { useAuthStore } from '../../stores/auth'
import DocumentStamp from '../../components/DocumentStamp.vue'

const fmtDateVal = (v) => v ? String(v).replace("T", " ").slice(0, 16) : ""
const route = useRoute()
const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')
const statusMap = { '': '草稿', draft: '草稿', loaded: '已装车', returned: '已退库' }

const mode = ref('create')
const saving = ref(false)
const warehouses = ref([])
const vehicleWarehouses = ref([])
const form = ref({
  id: null,
  load_no: '',
  from_warehouse_id: null,
  vehicle_warehouse_id: null,
  employee_id: null,
  remark: '',
  status: '',
  items: [
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 }
  ]
})
const { products, loadProducts } = useWarehouseProducts(() => form.value.from_warehouse_id)
const employees = ref([])
const list = ref([])
const total = ref(0)
const openDetails = ref([])

const query = ref({ page: 1, page_size: 20, status: '', keyword: '' })

const totalAmount = computed(() => {
  return form.value.items.reduce((s, item) => s + (item.quantity || 0) * (item.price || 0), 0)
})

const totalQuantity = computed(() => {
  return form.value.items.filter(i => i.product_id).reduce((s, item) => s + (item.quantity || 0), 0)
})

const statusTagType = (status) => ({ '': 'info', draft: 'warning', loaded: 'success', returned: 'danger' })[status] || 'info'

const getSummary = ({ columns, data }) => {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (col.property === 'amount') {
      sums[idx] = `¥${totalAmount.value.toFixed(2)}`
    }
    if (col.property === 'quantity') {
      sums[idx] = totalQuantity.value
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

const buildAvailableUnits = (p) => {
  if (!p) return []
  const baseId = p.base_unit_id || p.id
  const units = [{ unit_id: baseId, unit_level: 'small', unit_name: p.small_unit_name || p.unit || '基本单位', conv_rate: 1 }]
  if (p.medium_unit_name) units.push({ unit_id: baseId, unit_level: 'medium', unit_name: p.medium_unit_name, conv_rate: p.medium_conv_rate || 1 })
  if (p.large_unit_name) units.push({ unit_id: baseId, unit_level: 'large', unit_name: p.large_unit_name, conv_rate: p.large_conv_rate || 1 })
  return units
}

const onProductChange = async (index) => {
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
  }
  calcRowAmount(row)
}

const calcRowAmount = (row) => {
  row.amount = (row.quantity || 0) * (row.price || 0)
}

const addItem = () => {
  form.value.items.push({ product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 })
}

const copyRow = (index) => {
  const item = { ...form.value.items[index] }
  form.value.items.splice(index + 1, 0, item)
}

const resetForm = () => {
  form.value = {
    id: null,
    load_no: '',
    from_warehouse_id: null,
    vehicle_warehouse_id: null,
    employee_id: null,
    remark: '',
    status: '',
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
  if (!form.value.from_warehouse_id) return ElMessage.warning('请选择来源仓库')
  if (!form.value.vehicle_warehouse_id) return ElMessage.warning('请选择目标车仓')
  const validItems = form.value.items.filter(i => i.product_id && i.quantity > 0)
  if (validItems.length === 0) return ElMessage.warning('请添加装车商品')

  saving.value = true
  try {
    const data = {
      from_warehouse_id: form.value.from_warehouse_id,
      vehicle_warehouse_id: form.value.vehicle_warehouse_id,
      employee_id: form.value.employee_id,
      remark: form.value.remark,
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
    const res = form.value.id ? await updateVehicleLoad(form.value.id, data) : await createVehicleLoad(data)
    ElMessage.success('保存成功')
    if (res.data?.id) {
      form.value.id = res.data.id
      form.value.load_no = res.data.load_no
      form.value.status = 'draft'
    }
    loadData()
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleAudit = async (row) => {
  if (row) {
    await ElMessageBox.confirm('确认审核该装车单？', '审核确认', { type: 'warning' })
    await confirmVehicleLoad(row.id)
    ElMessage.success('审核成功')
    loadData()
    return
  }
  if (!form.value.id) return ElMessage.warning('请先保存单据')
  ElMessage.info('审核功能开发中')
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
  query.value = { page: 1, page_size: 20, status: '', keyword: '' }
  loadData()
}

const loadData = async () => {
  const params = { ...query.value }
  if (!params.status) delete params.status
  if (!params.keyword) delete params.keyword
  const res = await getVehicleLoads(params)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDetail = async (row) => {
  const res = await getVehicleLoad(row.id)
  const data = res.data || res
  openDetails.value.push({ id: data.id, visible: true, data })
}

onMounted(async () => {
  const [w, e] = await Promise.all([
    getWarehouses({ page_size: 100 }),
    getEmployees({ page_size: 100 })
  ])
  warehouses.value = w.data?.list || w.data || []
  vehicleWarehouses.value = warehouses.value
  employees.value = e.data?.list || e.data || []
  await loadProducts()

  const id = route.query.id
  if (id) {
    try {
      const res = await getVehicleLoad(id)
      const data = res.data || res
      if (data && data.id) {
        form.value = {
          ...data,
          items: (data.items || []).map(i => {
            const avail = buildAvailableUnits(products.value.find(x => x.id === i.product_id))
            const matched = avail.find(u => Math.abs(u.conv_rate - (i.unit_conv_rate || 1)) < 0.01) || avail[0] || {}
            return {
              product_id: i.product_id,
              quantity: i.unit_quantity || i.quantity || 1,
              price: i.price || 0,
              amount: i.amount || 0,
              remark: i.remark || '',
              unit_id: i.unit_id || null,
              _availableUnits: avail,
              _basePrice: i.price || 0,
              _unitLevel: matched.unit_level || 'small',
              _unitConvRate: i.unit_conv_rate || 1
            }
          })
        }
        while (form.value.items.length < 5) {
          form.value.items.push({ product_id: null, quantity: 1, price: 0, amount: 0, remark: '', unit_id: null, _availableUnits: [], _basePrice: 0 })
        }
      }
    } catch (e) { console.error('操作失败:', e) }
  } else {
    loadData()
  }
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
