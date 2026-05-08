<template>
  <div class="order-page">
    <!-- 顶部标题栏 -->
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">报损单</span>
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
          <el-button @click="handleAudit" v-if="form.id">审核</el-button>
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
        <span>报损明细</span>
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
        <el-table-column label="单位" width="80" align="center">
          <template #default="{ row }">{{ getUnit(row.product_id) }}</template>
        </el-table-column>
        <el-table-column label="单位换算" width="100" align="center">
          <template #default="{ row }">{{ getUnitConvert(row.product_id) }}</template>
        </el-table-column>
        <el-table-column label="数量" width="100">
          <template #default="{ row }">
            <el-input-number v-model="row.quantity" :min="1" size="small" style="width:90px" @change="calcRowAmount(row)" />
          </template>
        </el-table-column>
        <el-table-column label="单位成本" width="100">
          <template #default="{ row }">
            <el-input-number v-model="row.unit_cost" :min="0" :precision="2" size="small" style="width:90px" @change="calcRowAmount(row)" />
          </template>
        </el-table-column>
        <el-table-column label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ (row.amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="可用库存" width="90" align="right">
          <template #default="{ row }">{{ getAvailableStock(row.product_id) }}</template>
        </el-table-column>
        <el-table-column label="原因" width="120">
          <template #default="{ row }">
            <el-input v-model="row.reason" size="small" placeholder="原因" />
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
              <label>报损数量：</label>
              <span class="amount">{{ totalQuantity }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <label>报损金额：</label>
              <span class="amount text-danger">¥{{ totalAmount.toFixed(2) }}</span>
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
      <div class="section-title">报损记录</div>
      <el-form inline @submit.prevent="loadData" style="margin-bottom:12px">
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="待审核" value="pending" />
            <el-option label="已调整" value="adjusted" />
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
        <el-table-column prop="total_amount" label="总金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="150" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showDetail(row)">详情</el-button>
            <el-button link type="success" size="small" v-if="row.status === 'pending'" @click="handleAudit(row)">审核</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total"
        layout="total, prev, pager, next" style="margin-top:16px;justify-content:flex-end" @current-change="loadData" />
    </el-card>

    <!-- 详情弹窗（支持多开） -->
    <el-dialog v-for="d in openDetails" :key="d.id" v-model="d.visible" :title="`报损单详情 - ${d.data.code || ''}`" width="700px">
      <el-descriptions :column="2" border v-if="d.data">
        <el-descriptions-item label="单号">{{ d.data.code }}</el-descriptions-item>
        <el-descriptions-item label="仓库">{{ d.data.warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ (d.data.total_amount || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTagType(d.data.status)">{{ statusMap[d.data.status] }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ d.data.created_at }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ d.data.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-table v-if="d.data.items?.length" :data="d.data.items" border size="small" style="margin-top:16px">
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="quantity" label="数量" width="80" align="right" />
        <el-table-column prop="unit_cost" label="单位成本" width="80" align="right">
          <template #default="{ row }">¥{{ (row.unit_cost || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="80" align="right">
          <template #default="{ row }">¥{{ (row.amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDamageReports, createDamageReport, getDamageReport, auditDamageReport, getWarehouses, getProducts } from '../../api'
import { useAuthStore } from '../../stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')
const statusMap = { '': '草稿', pending: '待审核', adjusted: '已调整' }

const mode = ref('create')
const saving = ref(false)
const warehouses = ref([])
const products = ref([])
const list = ref([])
const total = ref(0)
const openDetails = ref([])

const query = ref({ page: 1, page_size: 20, status: '' })

const form = ref({
  code: '',
  warehouse_id: null,
  remark: '',
  status: '',
  items: [
    { product_id: null, quantity: 1, unit_cost: 0, amount: 0, reason: '' },
    { product_id: null, quantity: 1, unit_cost: 0, amount: 0, reason: '' },
    { product_id: null, quantity: 1, unit_cost: 0, amount: 0, reason: '' },
    { product_id: null, quantity: 1, unit_cost: 0, amount: 0, reason: '' },
    { product_id: null, quantity: 1, unit_cost: 0, amount: 0, reason: '' }
  ]
})

const totalAmount = computed(() => {
  return form.value.items.reduce((s, item) => s + (item.quantity || 0) * (item.unit_cost || 0), 0)
})

const totalQuantity = computed(() => {
  return form.value.items.filter(i => i.product_id).reduce((s, item) => s + (item.quantity || 0), 0)
})

const statusTagType = (status) => ({ '': 'info', pending: 'warning', adjusted: 'success' })[status] || 'info'

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

const getUnit = (productId) => {
  const p = products.value.find(x => x.id === productId)
  return p?.unit || '-'
}

const getUnitConvert = (productId) => {
  const p = products.value.find(x => x.id === productId)
  return p?.unit_convert || '-'
}

const getAvailableStock = (productId) => {
  const p = products.value.find(x => x.id === productId)
  return (p?.available_stock || p?.stock || 0).toFixed(2)
}

const onProductChange = (index) => {
  const p = products.value.find(x => x.id === form.value.items[index].product_id)
  if (p) {
    form.value.items[index].unit_cost = p.cost_price || p.retail_price || 0
    calcRowAmount(form.value.items[index])
  }
}

const calcRowAmount = (row) => {
  row.amount = (row.quantity || 0) * (row.unit_cost || 0)
}

const addItem = () => {
  form.value.items.push({ product_id: null, quantity: 1, unit_cost: 0, amount: 0, reason: '' })
}

const copyRow = (index) => {
  const item = { ...form.value.items[index] }
  form.value.items.splice(index + 1, 0, item)
}

const resetForm = () => {
  form.value = {
    code: '',
    warehouse_id: null,
    remark: '',
    status: '',
    items: [
      { product_id: null, quantity: 1, unit_cost: 0, amount: 0, reason: '' },
      { product_id: null, quantity: 1, unit_cost: 0, amount: 0, reason: '' },
      { product_id: null, quantity: 1, unit_cost: 0, amount: 0, reason: '' },
      { product_id: null, quantity: 1, unit_cost: 0, amount: 0, reason: '' },
      { product_id: null, quantity: 1, unit_cost: 0, amount: 0, reason: '' }
    ]
  }
  mode.value = 'create'
}

const handleSave = async () => {
  if (!form.value.warehouse_id) return ElMessage.warning('请选择仓库')
  const validItems = form.value.items.filter(i => i.product_id && i.quantity > 0)
  if (validItems.length === 0) return ElMessage.warning('请添加报损商品')

  saving.value = true
  try {
    const data = {
      warehouse_id: form.value.warehouse_id,
      remark: form.value.remark,
      items: validItems.map(i => ({
        product_id: i.product_id,
        quantity: i.quantity,
        unit_cost: i.unit_cost,
        amount: (i.quantity || 0) * (i.unit_cost || 0),
        reason: i.reason
      }))
    }
    const res = await createDamageReport(data)
    ElMessage.success('保存成功')
    if (res.data?.id) {
      form.value.id = res.data.id
      form.value.code = res.data.code
      form.value.status = 'pending'
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
    await ElMessageBox.confirm('确认审核该报损单？', '审核确认', { type: 'warning' })
    await auditDamageReport(row.id)
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
  query.value = { page: 1, page_size: 20, status: '' }
  loadData()
}

const loadData = async () => {
  const params = { ...query.value }
  if (!params.status) delete params.status
  const res = await getDamageReports(params)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDetail = async (row) => {
  const res = await getDamageReport(row.id)
  const data = res.data || res
  openDetails.value.push({ id: data.id, visible: true, data })
}

onMounted(async () => {
  const [w, p] = await Promise.all([getWarehouses({ page_size: 100 }), getProducts({ page_size: 5000 })])
  warehouses.value = w.data?.list || w.data || []
  products.value = p.data?.list || p.data || []

  const id = route.query.id
  if (id) {
    try {
      const res = await getDamageReport(id)
      const data = res.data || res
      if (data && data.id) {
        form.value = {
          ...data,
          items: (data.items || []).map(i => ({
            product_id: i.product_id,
            quantity: i.quantity || 1,
            unit_cost: i.unit_cost || 0,
            amount: i.amount || 0,
            reason: i.reason || ''
          }))
        }
        while (form.value.items.length < 5) {
          form.value.items.push({ product_id: null, quantity: 1, unit_cost: 0, amount: 0, reason: '' })
        }
      }
    } catch {}
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