<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>采购退货出库单</span>
          <el-button type="primary" @click="showCreateDialog">新建退货出库单</el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <el-form :inline="true" style="margin-bottom:16px">
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:140px" @change="loadData">
            <el-option label="待仓管确认" value="pending" />
            <el-option label="仓管已确认" value="warehouse_confirmed" />
            <el-option label="财务已确认" value="finance_confirmed" />
            <el-option label="已结算" value="settled" />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商">
          <el-select v-model="query.supplier_id" clearable filterable placeholder="全部" style="width:180px" @change="loadData">
            <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="单号">
          <el-input v-model="query.keyword" placeholder="搜索单号" clearable style="width:180px" @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>

      <!-- 列表 -->
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="return_dlv_no" label="出库单号" width="160" />
        <el-table-column prop="supplier_name" label="供应商" min-width="150" />
        <el-table-column prop="total_amount" label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ (row.total_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="status_text" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="showDetail(row)">详情</el-button>
            <el-button v-if="row.status === 'pending'" size="small" type="success" @click="handleWarehouseConfirm(row)">仓管确认</el-button>
            <el-button v-if="row.status === 'warehouse_confirmed'" size="small" type="primary" @click="handleFinanceConfirm(row)">财务确认</el-button>
            <el-button v-if="row.status === 'pending'" size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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

    <!-- 新建对话框 -->
    <el-dialog v-model="createVisible" title="新建采购退货出库单" width="900px" destroy-on-close>
      <el-form :model="form" label-width="90px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="供应商" required>
              <el-select v-model="form.supplier_id" filterable placeholder="选择供应商" style="width:100%">
                <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="出库仓库" required>
              <el-select v-model="form.warehouse_id" filterable placeholder="选择仓库" style="width:100%">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="关联退货单">
              <el-select v-model="form.purchase_return_id" clearable filterable placeholder="可选" style="width:100%">
                <el-option v-for="r in purchaseReturns" :key="r.id" :label="r.code" :value="r.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" placeholder="备注信息" />
        </el-form-item>

        <el-form-item label="退货商品">
          <el-button size="small" type="primary" @click="addItem">添加商品</el-button>
          <el-table :data="form.items" border style="margin-top:8px" show-summary :summary-method="calcSummary">
            <el-table-column label="商品" min-width="200">
              <template #default="{ row }">
                <el-select v-model="row.product_id" filterable placeholder="选择商品" style="width:100%">
                  <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="数量" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.quantity" :min="0.01" :precision="2" size="small" controls-position="right" />
              </template>
            </el-table-column>
            <el-table-column label="单价" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.unit_price" :min="0" :precision="2" size="small" controls-position="right" />
              </template>
            </el-table-column>
            <el-table-column label="金额" width="120" align="right">
              <template #default="{ row }">¥{{ ((row.quantity || 0) * (row.unit_price || 0)).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center">
              <template #default="{ $index }">
                <el-button size="small" type="danger" text @click="form.items.splice($index, 1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">提交</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="退货出库单详情" width="800px">
      <el-descriptions :column="2" border v-if="detail">
        <el-descriptions-item label="出库单号">{{ detail.return_dlv_no }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ detail.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="金额">¥{{ (detail.total_amount || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(detail.status)">{{ detail.status_text }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="仓管确认时间">{{ detail.wh_confirmed_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="财务确认时间">{{ detail.fin_confirmed_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ detail.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="detail?.items || []" border style="margin-top:16px">
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="quantity" label="数量" width="100" align="right" />
        <el-table-column prop="unit_price" label="单价" width="100" align="right">
          <template #default="{ row }">¥{{ (row.unit_price || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ (row.amount || 0).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getPurchaseReturnDeliveries, createPurchaseReturnDelivery, getPurchaseReturnDelivery,
  warehouseConfirmPurchaseReturnDlv, financeConfirmPurchaseReturnDlv, deletePurchaseReturnDelivery,
  getProducts, getSuppliers, getWarehouses, getPurchaseReturns
} from '../../api'

const loading = ref(false)
const submitting = ref(false)
const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, status: '', supplier_id: null, keyword: '' })

const suppliers = ref([])
const warehouses = ref([])
const products = ref([])
const purchaseReturns = ref([])

const createVisible = ref(false)
const form = ref({ supplier_id: null, warehouse_id: null, purchase_return_id: null, remark: '', items: [] })

const detailVisible = ref(false)
const detail = ref(null)

const statusType = (status) => {
  const map = { pending: 'warning', warehouse_confirmed: 'primary', finance_confirmed: 'success', settled: 'info' }
  return map[status] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getPurchaseReturnDeliveries(query.value)
    list.value = res.data || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  const [s, w, p, r] = await Promise.all([
    getSuppliers({ page_size: 200 }),
    getWarehouses({ page_size: 200 }),
    getProducts({ page_size: 500 }),
    getPurchaseReturns({ page_size: 200, status: 0 })
  ])
  suppliers.value = s.data || []
  warehouses.value = w.data || []
  products.value = p.data || []
  purchaseReturns.value = r.data || []
}

const showCreateDialog = () => {
  form.value = { supplier_id: null, warehouse_id: null, purchase_return_id: null, remark: '', items: [] }
  createVisible.value = true
}

const addItem = () => {
  form.value.items.push({ product_id: null, quantity: 1, unit_price: 0 })
}

const calcSummary = ({ columns, data }) => {
  const sums = []
  columns.forEach((col, index) => {
    if (index === 0) { sums[index] = '合计'; return }
    if (index === columns.length - 1) { sums[index] = ''; return }
    const values = data.map(item => {
      if (index === 3) return (item.quantity || 0) * (item.unit_price || 0)
      return Number(item[col.property])
    })
    if (index === 3) {
      sums[index] = '¥' + values.reduce((a, b) => a + b, 0).toFixed(2)
    } else {
      sums[index] = ''
    }
  })
  return sums
}

const handleCreate = async () => {
  if (!form.value.supplier_id) return ElMessage.warning('请选择供应商')
  if (!form.value.warehouse_id) return ElMessage.warning('请选择出库仓库')
  if (!form.value.items.length) return ElMessage.warning('请添加退货商品')

  for (const item of form.value.items) {
    if (!item.product_id) return ElMessage.warning('请选择商品')
    if (!item.quantity || item.quantity <= 0) return ElMessage.warning('数量必须大于0')
  }

  submitting.value = true
  try {
    const data = {
      ...form.value,
      total_amount: form.value.items.reduce((sum, item) => sum + (item.quantity || 0) * (item.unit_price || 0), 0),
      items: form.value.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit_price: item.unit_price,
        amount: (item.quantity || 0) * (item.unit_price || 0)
      }))
    }
    await createPurchaseReturnDelivery(data)
    ElMessage.success('创建成功')
    createVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

const showDetail = async (row) => {
  const res = await getPurchaseReturnDelivery(row.id)
  detail.value = res.data
  detailVisible.value = true
}

const handleWarehouseConfirm = async (row) => {
  await ElMessageBox.confirm('确认退货出库？将扣减对应仓库库存！', '仓管确认', { type: 'warning' })
  await warehouseConfirmPurchaseReturnDlv(row.id)
  ElMessage.success('仓管确认成功，已扣减库存')
  loadData()
}

const handleFinanceConfirm = async (row) => {
  await ElMessageBox.confirm('确认冲账？将冲减供应商应付！', '财务确认', { type: 'warning' })
  await financeConfirmPurchaseReturnDlv(row.id)
  ElMessage.success('财务确认成功，已冲减供应商应付')
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该退货出库单？', '删除确认', { type: 'warning' })
  await deletePurchaseReturnDelivery(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => {
  loadData()
  loadOptions()
})
</script>
