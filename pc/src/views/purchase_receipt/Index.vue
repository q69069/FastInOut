<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>采购入库单</span>
          <el-button type="primary" @click="showDialog()">新建入库单</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="待确认" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已红冲" value="reversed" />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商">
          <el-select v-model="query.supplier_id" clearable filterable placeholder="全部" style="width:160px">
            <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="receipt_no" label="单号" width="150" />
        <el-table-column prop="supplier_name" label="供应商" width="120" />
        <el-table-column prop="warehouse_name" label="仓库" width="100" />
        <el-table-column prop="total_amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status==='confirmed'?'success':row.status==='reversed'?'danger':'info'">
              {{ row.status==='confirmed'?'已确认':row.status==='reversed'?'已红冲':'待确认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">详情</el-button>
            <el-button link type="success" v-if="row.status==='pending'" @click="handleConfirm(row)">确认入库</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>

    <!-- 新建入库单弹窗 -->
    <el-dialog v-model="dialogVisible" title="新建采购入库单" width="800px" :close-on-click-modal="false">
      <el-form :model="form" label-width="80px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="采购订单" required>
              <el-select v-model="form.purchase_order_id" filterable placeholder="选择采购订单" style="width:100%" @change="onOrderChange">
                <el-option v-for="o in orders" :key="o.id" :label="`${o.code} - ${o.supplier_name||''}`" :value="o.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="供应商">
              <el-input :model-value="selectedOrder?.supplier_name" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="仓库" required>
              <el-select v-model="form.warehouse_id" filterable placeholder="选择仓库" style="width:100%">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider content-position="left">入库明细</el-divider>
        <el-table :data="form.items" border size="small">
          <el-table-column prop="product_name" label="商品" min-width="180" />
          <el-table-column label="数量" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="0.01" :precision="2" size="small" style="width:100%" />
            </template>
          </el-table-column>
          <el-table-column label="单价" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.unit_price" :min="0" :precision="2" size="small" style="width:100%" />
            </template>
          </el-table-column>
          <el-table-column label="金额" width="100" align="right">
            <template #default="{ row }">¥{{ (row.quantity * row.unit_price).toFixed(2) }}</template>
          </el-table-column>
        </el-table>
        <el-form-item label="备注" style="margin-top:12px">
          <el-input v-model="form.remark" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="入库单详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="单号">{{ detail.receipt_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="detail.status==='confirmed'?'success':'info'">{{ detail.status==='confirmed'?'已确认':'待确认' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="供应商">{{ detail.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="仓库">{{ detail.warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ Number(detail.total_amount||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="detail.items || []" border size="small" style="margin-top:16px">
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="quantity" label="数量" width="100" align="right" />
        <el-table-column prop="unit_price" label="单价" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.unit_price||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.amount||0).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPurchaseReceipts, createPurchaseReceipt, getPurchaseReceipt, confirmPurchaseReceipt, getPurchaseOrders, getSuppliers, getWarehouses } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, status: '', supplier_id: '' })
const dialogVisible = ref(false)
const detailVisible = ref(false)
const saving = ref(false)
const detail = ref({})

const suppliers = ref([])
const warehouses = ref([])
const orders = ref([])
const selectedOrder = ref(null)

const form = ref({ purchase_order_id: null, warehouse_id: null, remark: '', items: [] })

const loadData = async () => {
  const res = await getPurchaseReceipts(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadDropdowns = async () => {
  const [s, w, o] = await Promise.all([getSuppliers(), getWarehouses(), getPurchaseOrders({ status: 1 })])
  suppliers.value = s.data || []
  warehouses.value = w.data || []
  orders.value = o.data || []
}

const showDialog = () => {
  form.value = { purchase_order_id: null, warehouse_id: null, remark: '', items: [] }
  selectedOrder.value = null
  dialogVisible.value = true
}

const onOrderChange = () => {
  const order = orders.value.find(o => o.id === form.value.purchase_order_id)
  selectedOrder.value = order
  if (order) {
    form.value.supplier_id = order.supplier_id
    form.value.items = (order.items || []).map(item => ({
      product_id: item.product_id,
      product_name: item.product_name || `商品${item.product_id}`,
      order_item_id: item.id,
      quantity: item.quantity - (item.received_qty || 0),
      unit_price: item.price || 0
    }))
  }
}

const handleSave = async () => {
  if (!form.value.purchase_order_id) return ElMessage.warning('请选择采购订单')
  if (!form.value.warehouse_id) return ElMessage.warning('请选择仓库')
  saving.value = true
  try {
    await createPurchaseReceipt(form.value)
    ElMessage.success('入库单创建成功')
    dialogVisible.value = false
    loadData()
  } finally {
    saving.value = false
  }
}

const showDetail = async (row) => {
  const res = await getPurchaseReceipt(row.id)
  detail.value = res.data || res
  detailVisible.value = true
}

const handleConfirm = async (row) => {
  await ElMessageBox.confirm('确认入库？将增加库存并更新供应商应付', '确认入库', { type: 'warning' })
  await confirmPurchaseReceipt(row.id)
  ElMessage.success('已确认入库')
  loadData()
}

onMounted(() => { loadData(); loadDropdowns() })
</script>
