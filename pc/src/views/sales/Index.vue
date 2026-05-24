<template>
  <div class="order-page">
    <!-- 顶部标题栏 -->
    <el-card class="header-card" style="position:relative">
      <DocumentStamp :status="form.status" />
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">销售订单</span>
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
          <el-button type="primary" @click="handleSave" :loading="saving" v-if="!form.id || form.status === 0 || form.status === 'pending'">保存</el-button>
          <el-button @click="handleAudit()" v-if="form.id && (form.status === 0 || form.status === 'pending')">审核</el-button>
          <el-button type="success" @click="handleQuickConfirm" v-if="form.id && form.status === 1">确认发货</el-button>
          <el-button @click="showReverseDialog = true" v-if="form.id && form.status !== 0 && form.status !== 'pending' && form.status !== 3 && form.status !== 'reversed'" type="danger">冲红</el-button>
          <el-button @click="handlePrint" v-if="form.id">打印</el-button>
          <el-button @click="handleCopy" v-if="form.id">复制</el-button>
          <el-button @click="handleNew">新增</el-button>
          <el-button @click="handleClose">关闭</el-button>
        </div>
      </div>
    </el-card>
    <ReverseDialog v-model="showReverseDialog" @confirm="handleReverse" />

    <!-- 单据主内容 -->
    <el-card class="form-card">
      <!-- 表头区域 -->
      <div class="form-header">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="客户" required class="form-label-bold">
              <el-select v-model="form.customer_id" filterable placeholder="搜索客户" style="width:100%" @change="onCustomerChange">
                <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id">
                  <span>{{ c.name }}</span>
                  <span class="text-muted fr"> {{ c.customer_level_name }}</span>
                </el-option>
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
            <el-form-item label="仓库" required class="form-label-bold">
              <el-select v-model="form.warehouse_id" filterable placeholder="选择仓库" style="width:100%">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="送货员" class="form-label-bold">
              <el-select v-model="form.deliverer_id" clearable filterable placeholder="选择送货员" style="width:100%">
                <el-option v-for="d in deliverers" :key="d.id" :label="d.name" :value="d.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="交易日期" class="form-label-bold">
              <el-date-picker v-model="form.trade_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="付款方式" class="form-label-bold">
              <el-select v-model="form.payment_method" style="width:100%">
                <el-option label="现结" value="cash" />
                <el-option label="月结" value="monthly" />
                <el-option label="预付" value="prepay" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="价格体系" class="form-label-bold">
              <el-select v-model="form.price_type" style="width:100%">
                <el-option label="标准售价" value="standard" />
                <el-option label="客户级别价" value="level" />
                <el-option label="最低售价" value="min" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="按最小单位销售" class="form-label-bold">
              <el-checkbox v-model="form.sell_by_min_unit" />
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
        <span>商品明细</span>
        <span class="text-muted">（双击行内数量或单价可直接编辑）</span>
      </div>
      <el-table :data="form.items" border size="small" class="items-table" show-summary :summary-method="getSummary">
        <el-table-column type="index" label="序号" width="50" align="center" />
        <el-table-column label="商品名称" min-width="220">
          <template #default="{ row, $index }">
            <el-select v-model="row.product_id" filterable placeholder="搜索商品" style="width:100%" @change="onProductChange($index)" @focus="focusProduct($index)">
              <el-option v-for="p in filterProducts($index)" :key="p.id" :label="`${p.name}${p.spec ? ' ['+p.spec+']' : ''}`" :value="p.id">
                <span>{{ p.name }}</span>
                <span v-if="p.spec" class="text-muted"> [{{ p.spec }}]</span>
                <span class="text-muted fr">¥{{ p.retail_price }}</span>
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
        <el-table-column label="生产日期" width="120">
          <template #default="{ row }">
            <el-date-picker v-model="row.production_date" type="date" value-format="YYYY-MM-DD" size="small" style="width:110px" />
          </template>
        </el-table-column>
        <el-table-column label="数量" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.quantity" :min="1" size="small" style="width:120px" @change="calcRowAmount(row)" />
          </template>
        </el-table-column>
        <el-table-column label="价格" width="130">
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
        <el-table-column label="占用库存" width="90" align="right">
          <template #default="{ row }">{{ getOccupiedStock(row.product_id) }}</template>
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
        <span class="text-muted ml-8">快捷键：Tab 跳下一格，Enter 新增一行</span>
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
              <label>待支付金额：</label>
              <span class="amount text-danger">¥{{ netAmount.toFixed(2) }}</span>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
defineOptions({ name: 'Sales' })
import { ref, computed, onMounted, onActivated, watch, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSalesOrders, createSalesOrder, updateSalesOrder, deleteSalesOrder, orderToStockout, getSalesOrder, auditSalesOrder, reverseSalesOrder, quickConfirmSalesOrder, getCustomers, getWarehouses, getSalesmen, getEmployees } from '../../api'
import { useAuthStore } from '../../stores/auth'
import { useWarehouseProducts } from '../../utils/useWarehouseProducts'
import DocumentStamp from '../../components/DocumentStamp.vue'
import ReverseDialog from '../../components/ReverseDialog.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const updateCurrentTabPath = inject('updateCurrentTabPath', null)
const closeCurrentTab = inject('closeCurrentTab', null)
const now = new Date().toLocaleString('zh-CN')
const showReverseDialog = ref(false)

const mode = ref('create')
const saving = ref(false)
const customers = ref([])
const warehouses = ref([])
const form = ref({
  code: '',
  customer_id: null,
  salesman_id: null,
  warehouse_id: null,
  deliverer_id: null,
  trade_date: new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '-'),
  payment_method: 'cash',
  price_type: 'standard',
  sell_by_min_unit: false,
  remark: '',
  discount_amount: 0,
  items: [
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' },
    { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' }
  ]
})
const { products, loadProducts } = useWarehouseProducts(() => form.value.warehouse_id)
const salesmen = ref([])
const deliverers = ref([])
const employees = ref([])

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

const filterProducts = (index) => {
  return products.value
}

const getProductBarcode = (productId) => {
  const p = products.value.find(x => x.id === productId)
  return p?.barcode || '-'
}

const buildAvailableUnits = (p) => {
  if (!p) return []
  const baseId = p.base_unit_id || p.id
  const units = [{ unit_id: baseId, unit_level: 'small', unit_name: p.small_unit_name || p.unit || '基本单位', conv_rate: 1 }]
  if (p.medium_unit_name) units.push({ unit_id: baseId, unit_level: 'medium', unit_name: p.medium_unit_name, conv_rate: p.medium_conv_rate || 1 })
  if (p.large_unit_name) units.push({ unit_id: baseId, unit_level: 'large', unit_name: p.large_unit_name, conv_rate: p.large_conv_rate || 1 })
  return units
}

const getAvailableStock = (row) => {
  const p = products.value.find(x => x.id === row.product_id)
  const stock = p?.available_stock || p?.stock || 0
  const rate = row._unitConvRate || 1
  return rate > 1 ? (stock / rate).toFixed(2) : stock.toFixed(2)
}

const getOccupiedStock = (productId) => {
  const p = products.value.find(x => x.id === productId)
  return (p?.occupied_stock || 0).toFixed(2)
}

const focusProduct = (index) => {}

const onCustomerChange = (customerId) => {
  const c = customers.value.find(x => x.id === customerId)
  if (c) form.value.salesman_id = c.salesman_id || null
}

const onProductChange = (index) => {
  const row = form.value.items[index]
  const p = products.value.find(x => x.id === row.product_id)
  if (p) {
    row._basePrice = p.retail_price || 0
    row.price = row._basePrice
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

const calcNetAmount = () => {}

const addItem = () => {
  form.value.items.push({ product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' })
}

const copyRow = (index) => {
  const item = { ...form.value.items[index] }
  form.value.items.splice(index + 1, 0, item)
}

const resetForm = () => {
  form.value = {
    code: '',
    customer_id: null,
    salesman_id: null,
    warehouse_id: null,
    deliverer_id: null,
    trade_date: new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '-'),
    payment_method: 'cash',
    price_type: 'standard',
    sell_by_min_unit: false,
    remark: '',
    discount_amount: 0,
    items: [
      { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' },
      { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' },
      { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' },
      { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' },
      { product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' }
    ]
  }
}

const handleSave = async () => {
  if (!form.value.customer_id) return ElMessage.warning('请选择客户')
  if (!form.value.warehouse_id) return ElMessage.warning('请选择仓库')
  const validItems = form.value.items.filter(i => i.product_id && i.quantity > 0)
  if (validItems.length === 0) return ElMessage.warning('请添加商品')

  saving.value = true
  try {
    const data = {
      customer_id: form.value.customer_id,
      salesman_id: form.value.salesman_id,
      warehouse_id: form.value.warehouse_id,
      deliverer_id: form.value.deliverer_id,
      trade_date: form.value.trade_date,
      payment_method: form.value.payment_method,
      price_type: form.value.price_type,
      sell_by_min_unit: form.value.sell_by_min_unit,
      remark: form.value.remark,
      discount_amount: form.value.discount_amount || 0,
      items: validItems.map(i => ({
        product_id: i.product_id,
        quantity: i.quantity,
        price: i.price,
        amount: (i.quantity || 0) * (i.price || 0),
        remark: i.remark,
        production_date: i.production_date || null,
        batch_id: i.batch_id || null,
        unit_id: i.unit_id,
        unit_level: i._unitLevel || 'small',
        unit_conv_rate: i._unitConvRate || 1,
        unit_quantity: i.quantity
      }))
    }
    if (form.value.id) {
      await updateSalesOrder(form.value.id, data)
      ElMessage.success('更新成功')
    } else {
      const res = await createSalesOrder(data)
      form.value.id = res.data?.id
      form.value.code = res.data?.code || res.data?.order_no || form.value.code || '（已保存）'
      form.value.status = res.data?.status ?? 0
      ElMessage.success('保存成功')
      if (updateCurrentTabPath && res.data?.id) {
        updateCurrentTabPath(`/sales?id=${res.data.id}`, `销售订单 ${form.value.code}`)
      }
    }
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleAudit = async () => {
  if (!form.value.id) return ElMessage.warning('请先保存单据')
  await ElMessageBox.confirm('确认审核该订单？审核后将无法修改', '审核确认', { type: 'warning' })
  await auditSalesOrder(form.value.id)
  // 立即更新状态
  form.value.status = 1
  form.value.auditor_name = authStore.displayName
  ElMessage.success({ message: '审核成功', duration: 1500 })
}

const handleQuickConfirm = async () => {
  if (!form.value.id) return
  await ElMessageBox.confirm('确认发货？将自动出库并更新库存', '发货确认', { type: 'warning' })
  try {
    await quickConfirmSalesOrder(form.value.id)
    form.value.status = 2
    ElMessage.success('发货确认成功，库存已更新')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '发货确认失败')
  }
}

const handlePrint = () => {
  if (!form.value.id) return ElMessage.warning('请先保存单据')
  window.open(`/api/print/sales-order/${form.value.id}`, '_blank')
}

const handleCopy = () => {
  if (!form.value.id) return ElMessage.warning('请先保存单据再复制')
  const ts = Date.now()
  // 存储当前表单数据用于复制
  try {
    const copyData = JSON.stringify(form.value)
    sessionStorage.setItem('copyFormData_' + ts, copyData)
    console.log('复制数据已存储:', ts, '数据大小:', copyData.length)
  } catch (e) {
    console.error('存储复制数据失败:', e)
  }
  router.push({ path: '/sales', query: { id: 'copy-' + ts } })
}

const handleNew = () => {
  router.push({ path: '/sales', query: { id: 'new-' + Date.now() } })
}

const handleReverse = async (reason) => {
  if (!form.value.id) return ElMessage.warning('请先保存单据')
  try {
    await reverseSalesOrder(form.value.id, { reason })
    form.value.status = 3
    form.value.reverse_reason = reason
    ElMessage.success('冲红成功')
  } catch (e) {
    ElMessage.error(e.message || '冲红失败')
  }
}

const handleClose = () => {
  if (closeCurrentTab) {
    closeCurrentTab()
  } else {
    resetForm()
  }
}

// 加载已有单据
const loadOrder = async (id) => {
  if (!id || String(id).startsWith('new')) {
    resetForm()
    return
  }
  // 复制模式：从sessionStorage恢复数据
  if (String(id).startsWith('copy-')) {
    const ts = id.replace('copy-', '')
    console.log('复制模式加载, ts:', ts)
    const saved = sessionStorage.getItem('copyFormData_' + ts)
    console.log('找到缓存数据:', !!saved, saved ? '长度:' + saved.length : '')
    if (saved) {
      try {
        const data = JSON.parse(saved)
        form.value = {
          ...data,
          id: null,
          code: '',
          status: 0,
          auditor_name: '',
          auditor_id: null,
          confirmed_at: null,
          audit_time: null,
          items: (data.items || []).map(i => {
            const p = products.value.find(x => x.id === i.product_id)
            const avail = buildAvailableUnits(p)
            const matched = avail.find(u => Math.abs(u.conv_rate - (i.unit_conv_rate || 1)) < 0.01) || avail[0] || {}
            return {
              product_id: i.product_id,
              quantity: i.quantity,
              price: i.price,
              amount: 0,
              remark: i.remark || '',
              production_date: i.production_date || '',
              batch_id: null,
              unit_id: i.unit_id,
              _basePrice: p?.retail_price || 0,
              _availableUnits: avail,
              _unitLevel: matched.unit_level || 'small',
              _unitConvRate: i.unit_conv_rate || 1
            }
          })
        }
        while (form.value.items.length < 5) {
          form.value.items.push({ product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' })
        }
        return
      } catch (e) {
        console.error('恢复复制数据失败:', e)
      }
    }
    resetForm()
    return
  }
  try {
    const res = await getSalesOrder(id)
    const data = res.data || res
    if (data && data.id) {
      form.value = {
        ...data,
        auditor_name: data.auditor_name || '',
        items: (data.items || []).map(i => {
          const p = products.value.find(x => x.id === i.product_id)
          const avail = buildAvailableUnits(p)
          const matched = avail.find(u => Math.abs(u.conv_rate - (i.unit_conv_rate || 1)) < 0.01) || avail[0] || {}
          return {
            product_id: i.product_id,
            quantity: i.quantity,
            price: i.price,
            amount: i.amount,
            remark: i.remark || '',
            production_date: i.production_date || '',
            batch_id: i.batch_id || null,
            unit_id: i.unit_id,
            _basePrice: p?.retail_price || 0,
            _availableUnits: avail,
            _unitLevel: matched.unit_level || 'small',
            _unitConvRate: i.unit_conv_rate || 1
          }
        })
      }
      while (form.value.items.length < 5) {
        form.value.items.push({ product_id: null, quantity: 1, price: 0, amount: 0, remark: '', production_date: '' })
      }
    }
  } catch (e) { console.error('加载订单失败:', e) }
}

// 切换标签时重新加载数据
watch(() => route.query.id, (newId) => {
  if (route.path === '/sales') loadOrder(newId)
})

onMounted(async () => {
  const [c, w, s, e] = await Promise.all([
    getCustomers({ page_size: 1000 }),
    getWarehouses({ page_size: 100 }),
    getSalesmen({ page_size: 100 }),
    getEmployees({ page_size: 100 })
  ])
  customers.value = c.data?.list || c.data || []
  warehouses.value = w.data?.list || w.data || []
  salesmen.value = s.data?.list || s.data || []
  await loadProducts()
  employees.value = e.data?.list || e.data || []
  deliverers.value = employees.value.filter(x => x.position === 'delivery')

  loadOrder(route.query.id)
})

// keep-alive 切换回来时重新加载数据
onActivated(async () => {
  if (route.query.id) {
    loadOrder(route.query.id)
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
.section-title .text-muted { font-weight: normal; font-size: 12px; color: #909399 }
.items-table { margin-bottom: 8px }
.items-table :deep(.el-input-number) { width: 90px }
.add-row-bar { padding: 8px 0; display: flex; align-items: center; gap: 8px }
.ml-8 { margin-left: 8px }
.text-muted { color: #909399; font-size: 12px }
.fr { float: right }
.amount-summary { background: #f5f7fa; padding: 16px; border-radius: 4px; margin-top: 16px }
.summary-item { display: flex; align-items: center; gap: 8px; height: 32px }
.summary-item label { font-weight: 600; color: #606266; min-width: 80px }
.summary-item .amount { font-size: 16px; font-weight: 600 }
.text-primary { color: #409eff }
.text-danger { color: #f56c6c }
</style>