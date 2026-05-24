<template>
  <div class="order-page">
    <!-- 顶部：标题栏 -->
    <el-card class="header-card" style="position:relative">
      <DocumentStamp :status="form.status" :confirmed-statuses="[2]" />
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">盘点管理</span>
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
          <el-button type="primary" @click="handleSave" :loading="saving" v-if="!form.id || form.status === 0 || form.status === 1">保存</el-button>
          <el-button @click="handleAudit()" v-if="form.id && form.status === 1">审核</el-button>
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
            <el-form-item label="仓库" required class="form-label-bold">
              <el-select v-model="form.warehouse_id" filterable placeholder="选择仓库" style="width:100%">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="备注" class="form-label-bold">
              <el-input v-model="form.remark" placeholder="填写备注信息" />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 商品明细 -->
      <div class="section-title">
        <span>盘点明细</span>
      </div>
      <el-table :data="form.items" border size="small" class="items-table" show-summary :summary-method="getSummary">
        <el-table-column type="index" label="序号" width="50" align="center" />
        <el-table-column label="商品名称" min-width="220">
          <template #default="{ row, $index }">
            <el-select v-model="row.product_id" filterable placeholder="搜索商品" style="width:100%" @change="onProductChange($index)">
              <el-option v-for="p in products" :key="p.id" :label="`${p.name}${p.spec ? ' ['+p.spec+']' : ''}`" :value="p.id">
                <span>{{ p.name }}</span>
                <span v-if="p.spec" class="text-muted"> [{{ p.spec }}]</span>
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
        <el-table-column label="系统数量" width="100" align="right">
          <template #default="{ row }">{{ getSystemQty(row.product_id) }}</template>
        </el-table-column>
        <el-table-column label="实际数量" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.actual_qty" :min="0" size="small" style="width:120px" />
          </template>
        </el-table-column>
        <el-table-column label="差异" width="80" align="right">
          <template #default="{ row }">
            <span :class="getDiffQty(row) > 0 ? 'text-success' : getDiffQty(row) < 0 ? 'text-danger' : ''">
              {{ getDiffQty(row) }}
            </span>
          </template>
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
              <label>盘点商品数：</label>
              <span class="amount">{{ totalCount }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <label>盘盈数量：</label>
              <span class="amount text-success">{{ totalProfit }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <label>盘亏数量：</label>
              <span class="amount text-danger">{{ totalLoss }}</span>
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
      <div class="section-title">盘点记录</div>
      <el-form inline @submit.prevent="loadData" style="margin-bottom:12px">
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="盘点中" value="1" />
            <el-option label="已审核" value="2" />
            <el-option label="已调整" value="3" />
            <el-option label="已作废" value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="query.warehouse_id" clearable placeholder="全部" style="width:150px">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
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
        <el-table-column prop="warehouse_name" label="仓库" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="150" :formatter="fmtDate" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showDetail(row)">详情</el-button>
            <el-button link type="success" size="small" v-if="row.status === 1" @click="handleAudit(row)">审核</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total"
        layout="total, prev, pager, next" style="margin-top:16px;justify-content:flex-end" @current-change="loadData" />
    </el-card>

    <!-- 详情弹窗（支持多开） -->
    <el-dialog v-for="d in openDetails" :key="d.id" v-model="d.visible" :title="`盘点单详情 - ${d.data.code || ''}`" width="700px">
      <el-descriptions :column="2" border v-if="d.data">
        <el-descriptions-item label="单号">{{ d.data.code }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusMap[d.data.status]?.type">{{ statusMap[d.data.status]?.label }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="仓库">{{ d.data.warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ d.data.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="d.data.items || []" border size="small" style="margin-top:16px">
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="product_code" label="编码" width="120" />
        <el-table-column prop="system_qty" label="系统数量" width="100" align="right" />
        <el-table-column prop="actual_qty" label="实际数量" width="100" align="right" />
        <el-table-column prop="diff_qty" label="差异" width="80" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.diff_qty > 0 ? '#67c23a' : row.diff_qty < 0 ? '#f56c6c' : '' }">{{ row.diff_qty }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="diff_type" label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.diff_type==='盘盈'?'success':row.diff_type==='盘亏'?'danger':'info'" size="small">{{ row.diff_type }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useWarehouseProducts } from '../../utils/useWarehouseProducts'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getStocktaking, createStocktaking, updateStocktaking, getStocktakingDetail, auditStocktaking, adjustStocktaking, voidStocktaking, getWarehouses, getInventory } from '../../api'
import { useAuthStore } from '../../stores/auth'
import DocumentStamp from '../../components/DocumentStamp.vue'

const fmtDate = (_r, _c, v) => v ? String(v).replace("T", " ").slice(0, 16) : ""
const route = useRoute()
const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const statusMap = { 0: '草稿', 1: '盘点中', 2: '已审核', 3: '已调整', 4: '已作废' }

const mode = ref('create')
const saving = ref(false)
const warehouses = ref([])
const form = ref({
  id: null,
  code: '',
  warehouse_id: null,
  remark: '',
  status: 0,
  items: [
    { product_id: null, actual_qty: 0, remark: '', unit_id: null, _availableUnits: [] },
    { product_id: null, actual_qty: 0, remark: '', unit_id: null, _availableUnits: [] },
    { product_id: null, actual_qty: 0, remark: '', unit_id: null, _availableUnits: [] },
    { product_id: null, actual_qty: 0, remark: '', unit_id: null, _availableUnits: [] },
    { product_id: null, actual_qty: 0, remark: '', unit_id: null, _availableUnits: [] }
  ]
})
const { products, loadProducts } = useWarehouseProducts(() => form.value.warehouse_id)
const inventoryMap = ref({})
const list = ref([])
const total = ref(0)

const query = ref({ page: 1, page_size: 20, status: '', warehouse_id: '' })
const openDetails = ref([])

const statusTagType = (status) => ({ 0: 'info', 1: 'warning', 2: 'success', 3: '', 4: 'danger' })[status] || 'info'

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

const onProductChange = (index) => {
  const row = form.value.items[index]
  if (!row.product_id) return
  const p = products.value.find(x => x.id === row.product_id)
  row._availableUnits = buildAvailableUnits(p)
  if (row._availableUnits.length > 0) {
    const defaultUnit = row._availableUnits.find(u => u.unit_level === p.default_unit_level) || row._availableUnits[0]
    row.unit_id = defaultUnit.unit_id
    row._unitLevel = defaultUnit.unit_level
    row._unitConvRate = defaultUnit.conv_rate
  }
}

const onUnitChange = () => {}

const getSystemQty = (productId) => {
  const inv = inventoryMap.value[productId]
  return inv?.quantity ?? '-'
}

const getDiffQty = (row) => {
  if (!row.product_id) return 0
  const sys = inventoryMap.value[row.product_id]?.quantity || 0
  return (row.actual_qty || 0) - sys
}

const totalCount = computed(() => form.value.items.filter(i => i.product_id).length)

const totalProfit = computed(() => {
  return form.value.items.filter(i => i.product_id && getDiffQty(i) > 0).reduce((s, i) => s + getDiffQty(i), 0)
})

const totalLoss = computed(() => {
  return form.value.items.filter(i => i.product_id && getDiffQty(i) < 0).reduce((s, i) => s + Math.abs(getDiffQty(i)), 0)
})

const getSummary = ({ columns, data }) => {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (col.property === 'actual_qty') {
      sums[idx] = form.value.items.reduce((s, i) => s + (i.actual_qty || 0), 0)
    }
  })
  return sums
}

const addItem = () => {
  form.value.items.push({ product_id: null, actual_qty: 0, remark: '', unit_id: null, _availableUnits: [] })
}

const copyRow = (index) => {
  const item = { ...form.value.items[index] }
  form.value.items.splice(index + 1, 0, item)
}

const resetForm = () => {
  form.value = {
    id: null,
    code: '',
    warehouse_id: null,
    remark: '',
    status: 0,
    items: [
      { product_id: null, actual_qty: 0, remark: '', unit_id: null, _availableUnits: [] },
      { product_id: null, actual_qty: 0, remark: '', unit_id: null, _availableUnits: [] },
      { product_id: null, actual_qty: 0, remark: '', unit_id: null, _availableUnits: [] },
      { product_id: null, actual_qty: 0, remark: '', unit_id: null, _availableUnits: [] },
      { product_id: null, actual_qty: 0, remark: '', unit_id: null, _availableUnits: [] }
    ]
  }
  mode.value = 'create'
}

const loadData = async () => {
  const params = { ...query.value }
  if (!params.status) delete params.status
  if (!params.warehouse_id) delete params.warehouse_id
  const res = await getStocktaking(params)
  list.value = res.data || []
  total.value = res.total || 0
}

const handleSave = async () => {
  if (!form.value.warehouse_id) return ElMessage.warning('请选择仓库')
  if (!form.value.items.some(i => i.product_id)) return ElMessage.warning('请添加盘点商品')

  saving.value = true
  try {
    const data = {
      warehouse_id: form.value.warehouse_id,
      remark: form.value.remark,
      items: form.value.items.filter(i => i.product_id).map(i => {
        return {
          product_id: i.product_id,
          actual_qty: i.actual_qty || 0,
          unit_id: i.unit_id || null,
          unit_level: i._unitLevel || 'small',
          unit_conv_rate: i._unitConvRate || 1,
          unit_quantity: i.actual_qty || 0
        }
      })
    }
    const res = form.value.id ? await updateStocktaking(form.value.id, data) : await createStocktaking(data)
    ElMessage.success('保存成功')
    if (res.data?.id) {
      form.value.id = res.data.id
      form.value.code = res.data.code
      form.value.status = res.data.status
    }
    loadData()
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const showDetail = async (row) => {
  const res = await getStocktakingDetail(row.id)
  const data = res.data || res
  data.warehouse_name = row.warehouse_name
  openDetails.value.push({ id: data.id, visible: true, data })
}

const handleAudit = async (row) => {
  await ElMessageBox.confirm('确认审核此盘点单？差异率超过5%将标记需复核', '审核确认', { type: 'warning' })
  await auditStocktaking(row.id)
  ElMessage.success('审核完成')
  loadData()
}

const handleAdjust = async (row) => {
  await ElMessageBox.confirm('确认按实际库存调整系统库存？此操作不可逆', '调整确认', { type: 'warning' })
  await adjustStocktaking(row.id)
  ElMessage.success('库存已调整')
  loadData()
}

const handleVoid = async (row) => {
  await ElMessageBox.confirm('确认作废此盘点单？', '作废确认', { type: 'warning' })
  await voidStocktaking(row.id)
  ElMessage.success('已作废')
  loadData()
}

const handleClose = () => {
  mode.value = 'query'
  loadData()
}

const clearFilter = () => {
  query.value = { page: 1, page_size: 20, status: '', warehouse_id: '' }
  loadData()
}

const handlePrint = () => {
  ElMessage.info('打印功能开发中')
}

const handleCopy = () => {
  ElMessage.info('复制功能开发中')
}

onMounted(async () => {
  const [w] = await Promise.all([getWarehouses({ page_size: 100 })])
  warehouses.value = w.data?.list || w.data || []
  await loadProducts()

  const id = route.query.id
  if (id) {
    try {
      const res = await getStocktakingDetail(id)
      const data = res.data || res
      if (data && data.id) {
        form.value = {
          ...data,
          items: (data.items || []).map(i => {
            const avail = buildAvailableUnits(products.value.find(x => x.id === i.product_id))
            const matched = avail.find(u => Math.abs(u.conv_rate - (i.unit_conv_rate || 1)) < 0.01) || avail[0] || {}
            return {
              product_id: i.product_id,
              actual_qty: i.unit_quantity || i.actual_qty || 0,
              remark: i.remark || '',
              unit_id: i.unit_id || null,
              _availableUnits: avail,
              _unitLevel: matched.unit_level || 'small',
              _unitConvRate: i.unit_conv_rate || 1
            }
          })
        }
        while (form.value.items.length < 5) {
          form.value.items.push({ product_id: null, actual_qty: 0, remark: '', unit_id: null, _availableUnits: [] })
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
.text-success { color: #67c23a }
.text-danger { color: #f56c6c }
.list-card { margin-top: 12px }
</style>
