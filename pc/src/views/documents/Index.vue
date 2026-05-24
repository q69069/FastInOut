<template>
  <div class="order-page">
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">单据查询</span>
        </div>
        <div class="header-info">
          <span class="info-item">{{ now }}</span>
        </div>
      </div>
    </el-card>

    <el-card class="form-card">
      <el-form inline style="margin-bottom:12px">
        <el-form-item label="单据类型">
          <el-select v-model="filter.type" clearable placeholder="全部类型" style="width:140px" @change="loadData">
            <el-option label="采购订单" value="purchase_order" />
            <el-option label="采购单" value="purchase_receipt" />
            <el-option label="入库单" value="purchase_stockin" />
            <el-option label="采购退货订单" value="purchase_return_order" />
            <el-option label="采购退货" value="purchase_return_dlv" />
            <el-option label="销售订单" value="sales_order" />
            <el-option label="销售单" value="sales_delivery" />
            <el-option label="出库单" value="sales_stockout" />
            <el-option label="退货订单" value="sales_return_order" />
            <el-option label="退货单" value="return_delivery" />
            <el-option label="库存调拨" value="transfer" />
            <el-option label="盘点单" value="stocktaking" />
            <el-option label="装车单" value="vehicle_load" />
            <el-option label="报损单" value="damage_report" />
            <el-option label="交账单" value="settlement" />
          </el-select>
        </el-form-item>
        <el-form-item label="单号">
          <el-input v-model="filter.keyword" clearable placeholder="单号/客户/供应商" style="width:160px" @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="时间">
          <el-date-picker v-model="filter.date_range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" @change="loadData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="clearFilter">清空</el-button>
          <el-button type="success" @click="handleExport">导出Excel</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" border stripe v-loading="loading" :row-class-name="tableRowClassName">
        <el-table-column label="单据类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="typeTagType(row.type)" size="small">{{ typeName(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="单号" width="160">
          <template #default="{ row }">{{ row[getCodeKey(row.type)] || row.code || '-' }}</template>
        </el-table-column>
        <el-table-column :label="partyLabel" min-width="140">
          <template #default="{ row }">{{ row[getPartyKey(row.type)] || row.party_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="warehouse_name" label="仓库" width="110" />
        <el-table-column prop="total_amount" label="金额" width="110" align="right">
          <template #default="{ row }">
            <span v-if="row.total_amount != null">¥{{ Number(row.total_amount || 0).toFixed(2) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row)" size="small">{{ statusText(row) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" :formatter="fmtDate" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showDetail(row)">详情</el-button>
            <el-button v-if="canFulfill(row)" link type="success" size="small" @click="handleFulfill(row)">{{ fulfillLabel(row.type) }}</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top:16px;justify-content:flex-end"
        @current-change="loadData"
      />
    </el-card>

    <DocumentDetail v-model="detailVisible" :title="`${typeName(currentRow?.type)}详情`"
      :fields="detailFields" :items="detail.items || []" :item-columns="detailItemColumns" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getPurchaseOrders, getPurchaseReceipts, getPurchaseReturns, getPurchaseReturnDlvs,
  getSalesOrders, getSalesDeliveries, getSalesReturns, getReturnDeliveries,
  getTransfers, getStocktaking, getVehicleLoads, getDamageReports, getSettlements,
  getPurchaseOrder, getPurchaseReceipt, getPurchaseReturn, getPurchaseReturnDlv,
  getSalesOrder, getSalesDelivery, getSalesReturn, getReturnDelivery,
  getTransfer, getStocktakingDetail, getVehicleLoad, getDamageReport, getSettlement,
  quickConfirmPurchaseOrder, quickConfirmSalesOrder, fulfillSalesReturn, fulfillPurchaseReturn,
  getSalesStockouts, getSalesStockout, getPurchaseStockins, getPurchaseStockin,
  exportDocuments
} from '../../api'
import { ElMessageBox } from 'element-plus'
import DocumentDetail from '../../components/DocumentDetail.vue'

const fmtDateVal = (v) => v ? String(v).replace("T", " ").slice(0, 16) : ""
const fmtDate = (_r, _c, v) => v ? String(v).replace('T', ' ').slice(0, 16) : ''
const now = new Date().toLocaleString('zh-CN')

const loading = ref(false)
const list = ref([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref({})
const currentRow = ref({})

const query = ref({ page: 1, page_size: 20 })
const filter = ref({ type: '', keyword: '', date_range: [] })

const typeMap = {
  purchase_order: '采购订单',
  purchase_receipt: '采购单',
  purchase_stockin: '入库单',
  purchase_return_order: '采购退货订单',
  purchase_return_dlv: '采购退货',
  sales_order: '销售订单',
  sales_delivery: '销售单',
  sales_stockout: '出库单',
  sales_return_order: '退货订单',
  return_delivery: '退货单',
  transfer: '库存调拨',
  stocktaking: '盘点单',
  vehicle_load: '装车单',
  damage_report: '报损单',
  settlement: '交账单'
}

const typeTagType = (type) => ({
  purchase_order: 'primary', purchase_receipt: 'success', purchase_stockin: 'success', purchase_return_order: 'warning', purchase_return_dlv: 'warning',
  sales_order: 'primary', sales_delivery: 'success', sales_stockout: 'success', sales_return_order: 'warning', return_delivery: 'warning',
  transfer: 'info', stocktaking: 'warning', vehicle_load: 'info', damage_report: 'danger', settlement: 'primary'
})[type] || 'info'

const typeName = (type) => typeMap[type] || type

const getCodeKey = (type) => apiMap[type]?.codeKey || 'code'
const getPartyKey = (type) => apiMap[type]?.partyKey || 'party_name'

const partyLabel = computed(() => {
  const map = {
    purchase_order: '供应商', purchase_receipt: '供应商', purchase_stockin: '供应商', purchase_return_order: '供应商', purchase_return_dlv: '供应商',
    sales_order: '客户', sales_delivery: '客户', sales_stockout: '客户', sales_return_order: '客户', return_delivery: '客户',
    transfer: '调拨', stocktaking: '盘点', vehicle_load: '装车', damage_report: '报损', settlement: '业务员'
  }
  return map[filter.value.type] || '客户/供应商'
})

const statusText = (row) => {
  const { type, status } = row
  const s = Number(status)
  if (type === 'purchase_order') {
    return { 0: '草稿', 1: '已确认', 2: '已入库', 3: '已冲红' }[s] || status
  }
  if (type === 'purchase_receipt') {
    return { pending: '草稿', confirmed: '已入库', cancelled: '已取消', reversed: '已冲红' }[status] || status
  }
  if (type === 'purchase_stockin') {
    return { 0: '草稿', 1: '已入库', 2: '已入库', 3: '已冲红' }[s] || status
  }
  if (type === 'purchase_return_order') {
    return { 0: '草稿', 1: '已确认', 2: '已出库', 3: '已冲红' }[s] || status
  }
  if (type === 'purchase_return_dlv') {
    return { pending: '草稿', warehouse_confirmed: '已出库', finance_confirmed: '已结算', settled: '已结算', reversed: '已冲红' }[status] || status
  }
  if (type === 'sales_order') {
    return { 0: '草稿', 1: '已确认', 2: '已出库', 3: '已冲红' }[s] || status
  }
  if (type === 'sales_delivery') {
    return { pending: '草稿', confirmed: '已出库', settled: '已结算', voided: '已作废', reversed: '已冲红' }[status] || status
  }
  if (type === 'sales_stockout') {
    return { 0: '草稿', 1: '已出库', 2: '已出库', 3: '已冲红' }[s] || status
  }
  if (type === 'sales_return_order') {
    return { 0: '草稿', 1: '已确认', 2: '已入库', 3: '已冲红' }[s] || status
  }
  if (type === 'return_delivery') {
    return { 0: '草稿', 1: '已入库', 2: '已入库', 3: '已结算' }[s] || status
  }
  if (type === 'transfer') {
    return { 0: '草稿', 1: '调拨中', 2: '已确认', 3: '已取消' }[s] || status
  }
  if (type === 'stocktaking') {
    return { 1: '盘点中', 2: '已审核', 3: '已调整', 4: '已作废' }[s] || status
  }
  if (type === 'vehicle_load') {
    return { draft: '草稿', loaded: '已装车', returned: '已退库' }[status] || status
  }
  if (type === 'damage_report') {
    return { pending: '草稿', adjusted: '已调整' }[status] || status
  }
  if (type === 'settlement') {
    return { pending: '草稿', audited: '已通过', rejected: '已驳回' }[status] || status
  }
  return status
}

const statusTagType = (row) => {
  const { type, status } = row
  const s = Number(status)
  if (type === 'purchase_order' || type === 'sales_order') {
    return { 0: 'info', 1: 'warning', 2: 'success', 3: 'danger' }[s] || 'info'
  }
  if (type === 'purchase_return_order' || type === 'sales_return_order') {
    return { 0: 'info', 1: 'warning', 2: 'success', 3: 'danger' }[s] || 'info'
  }
  if (type === 'sales_stockout' || type === 'purchase_stockin') {
    return { 0: 'info', 1: 'warning', 2: 'success', 3: 'danger' }[s] || 'info'
  }
  if (type === 'transfer') {
    return { 1: 'warning', 2: 'success', 3: 'info' }[s] || 'info'
  }
  if (type === 'stocktaking') {
    return { 1: 'info', 2: 'success', 3: 'warning', 4: 'danger' }[s] || 'info'
  }
  if (type === 'vehicle_load') {
    return { draft: 'info', loaded: 'success', returned: 'danger' }[status] || 'info'
  }
  const ss = String(status)
  return { pending: 'warning', approved: 'success', confirmed: 'success', audited: 'success', adjusted: 'success', warehouse_confirmed: 'success', finance_confirmed: 'success', settled: 'success', rejected: 'danger', cancelled: 'info', voided: 'info', reversed: 'info' }[ss] || 'info'
}

const detailFields = computed(() => {
  const d = detail.value
  const t = currentRow.value?.type
  const codeKey = getCodeKey(t)
  const partyKey = getPartyKey(t)
  const code = d[codeKey] || d.code
  if (!code) return []
  const fields = [
    { label: '单号', value: code },
    { label: partyLabel.value, value: d[partyKey] || d.party_name || d.supplier_name || d.customer_name || '-' },
    { label: '仓库', value: d.warehouse_name || d.from_warehouse_name || d.to_warehouse_name || '-' }
  ]
  if (d.total_amount != null) fields.push({ label: '金额', value: Number(d.total_amount).toFixed(2), type: 'money' })
  fields.push(
    { label: '状态', value: statusText({ type: t, status: d.status }), type: 'tag', tagType: statusTagType({ type: t, status: d.status }) },
    { label: '创建时间', value: fmtDateVal(d.created_at) },
    { label: '备注', value: d.remark, span: 2 }
  )
  return fields
})

const detailItemColumns = [
  { prop: 'product_name', label: '商品', minWidth: 150 },
  { prop: 'quantity', label: '数量', width: 80, align: 'right' },
  { prop: 'unit_price', label: '单价', width: 80, align: 'right', type: 'money' },
  { prop: 'amount', label: '金额', width: 100, align: 'right', type: 'money' }
]

const tableRowClassName = ({ row }) => {
  if (row.type === 'damage_report' || row.type === 'stocktaking') return 'warning-row'
  return ''
}

const canFulfill = (row) => {
  const orderTypes = ['purchase_order', 'sales_order', 'purchase_return_order', 'sales_return_order']
  return orderTypes.includes(row.type) && Number(row.status) === 1
}

const fulfillLabel = (type) => {
  return { purchase_order: '确认到货', sales_order: '确认发货', purchase_return_order: '确认退货', sales_return_order: '确认退货' }[type] || '确认'
}

const handleFulfill = async (row) => {
  const label = fulfillLabel(row.type)
  try {
    await ElMessageBox.confirm(`确定要${label}吗？`, '确认操作', { type: 'warning' })
  } catch { return }
  loading.value = true
  try {
    const apiMap = {
      purchase_order: quickConfirmPurchaseOrder,
      sales_order: quickConfirmSalesOrder,
      purchase_return_order: fulfillPurchaseReturn,
      sales_return_order: fulfillSalesReturn
    }
    const fn = apiMap[row.type]
    if (!fn) return
    await fn(row.id)
    ElMessage.success(`${label}成功`)
    loadData()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || `${label}失败`)
  } finally {
    loading.value = false
  }
}

const handleExport = async () => {
  try {
    const params = {}
    if (filter.value.type) params.type = filter.value.type
    if (filter.value.date_range?.length === 2) {
      params.start_date = filter.value.date_range[0]
      params.end_date = filter.value.date_range[1]
    }
    if (filter.value.keyword) params.keyword = filter.value.keyword
    const res = await exportDocuments(params)
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `单据导出_${new Date().toISOString().slice(0,10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

const apiMap = {
  purchase_order: { list: getPurchaseOrders, detail: getPurchaseOrder, codeKey: 'code', partyKey: 'supplier_name' },
  purchase_receipt: { list: getPurchaseReceipts, detail: getPurchaseReceipt, codeKey: 'receipt_no', partyKey: 'supplier_name' },
  purchase_stockin: { list: getPurchaseStockins, detail: getPurchaseStockin, codeKey: 'code', partyKey: 'supplier_name' },
  purchase_return_order: { list: getPurchaseReturns, detail: getPurchaseReturn, codeKey: 'code', partyKey: 'supplier_name' },
  purchase_return_dlv: { list: getPurchaseReturnDlvs, detail: getPurchaseReturnDlv, codeKey: 'return_dlv_no', partyKey: 'supplier_name' },
  sales_order: { list: getSalesOrders, detail: getSalesOrder, codeKey: 'code', partyKey: 'customer_name' },
  sales_delivery: { list: getSalesDeliveries, detail: getSalesDelivery, codeKey: 'delivery_no', partyKey: 'customer_name' },
  sales_stockout: { list: getSalesStockouts, detail: getSalesStockout, codeKey: 'code', partyKey: 'customer_name' },
  sales_return_order: { list: getSalesReturns, detail: getSalesReturn, codeKey: 'code', partyKey: 'customer_name' },
  return_delivery: { list: getReturnDeliveries, detail: getReturnDelivery, codeKey: 'code', partyKey: 'customer_name' },
  transfer: { list: getTransfers, detail: getTransfer, codeKey: 'code', partyKey: 'from_warehouse_name' },
  stocktaking: { list: getStocktaking, detail: getStocktakingDetail, codeKey: 'code', partyKey: 'warehouse_name' },
  vehicle_load: { list: getVehicleLoads, detail: getVehicleLoad, codeKey: 'load_no', partyKey: 'from_warehouse_name' },
  damage_report: { list: getDamageReports, detail: getDamageReport, codeKey: 'code', partyKey: 'warehouse_name' },
  settlement: { list: getSettlements, detail: getSettlement, codeKey: 'settlement_no', partyKey: 'employee_name' }
}

const loadData = async () => {
  if (!filter.value.type) {
    loadAllDocuments()
    return
  }
  loading.value = true
  try {
    const params = { ...query.value }
    if (filter.value.keyword) params.keyword = filter.value.keyword
    if (filter.value.date_range?.length === 2) {
      params.start_date = filter.value.date_range[0]
      params.end_date = filter.value.date_range[1]
    }
    const api = apiMap[filter.value.type]
    if (!api) return
    const res = await api.list(params)
    list.value = (res.data || []).map(item => ({ ...item, type: filter.value.type }))
    total.value = res.total || list.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadAllDocuments = async () => {
  loading.value = true
  try {
    const types = Object.keys(apiMap)
    const params = { ...query.value, page_size: 20 }
    if (filter.value.keyword) params.keyword = filter.value.keyword
    if (filter.value.date_range?.length === 2) {
      params.start_date = filter.value.date_range[0]
      params.end_date = filter.value.date_range[1]
    }
    const results = await Promise.allSettled(
      types.map(type => apiMap[type].list({ ...params, page: 1 }))
    )
    const allItems = []
    results.forEach((result, idx) => {
      if (result.status === 'fulfilled') {
        const type = types[idx]
        const items = (result.value.data || []).map(item => ({ ...item, type }))
        allItems.push(...items)
      }
    })
    allItems.sort((a, b) => {
      const ta = a.created_at || ''
      const tb = b.created_at || ''
      return tb.localeCompare(ta)
    })
    list.value = allItems.slice(0, query.value.page_size)
    total.value = allItems.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const clearFilter = () => {
  filter.value = { type: '', keyword: '', date_range: [] }
  query.value = { page: 1, page_size: 20 }
  loadData()
}

const showDetail = async (row) => {
  currentRow.value = row
  try {
    const api = apiMap[row.type]
    if (!api) return
    const res = await api.detail(row.id)
    detail.value = res.data || res
    detailVisible.value = true
  } catch (e) {
    ElMessage.error('加载详情失败')
  }
}

onMounted(() => { loadData() })
</script>

<style scoped>
.order-page { padding: 16px; background: #f5f5f5; min-height: 100vh }
.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px }
.page-title { display: flex; align-items: center; gap: 12px }
.title-text { font-size: 18px; font-weight: 600; color: #303133 }
.header-info { display: flex; gap: 24px; color: #909399; font-size: 13px }
.form-card { margin-top: 12px }
:deep(.warning-row) { background-color: #fdf6ec }
</style>
