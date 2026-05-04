<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>销售单管理</span>
          <el-button type="primary" @click="showDialog()">新开销售单</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="待处理" value="pending" />
            <el-option label="交账中" value="settling" />
            <el-option label="已交账" value="settled" />
            <el-option label="已作废" value="voided" />
            <el-option label="已锁定" value="locked" />
            <el-option label="已红冲" value="reversed" />
          </el-select>
        </el-form-item>
        <el-form-item label="客户">
          <el-select v-model="query.customer_id" clearable filterable placeholder="全部" style="width:160px">
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="query.date_range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="delivery_no" label="单号" width="150" />
        <el-table-column prop="customer_name" label="客户" width="120" />
        <el-table-column prop="total_amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="收款方式" width="200">
          <template #default="{ row }">
            <span v-if="row.cash_amount">现金¥{{ Number(row.cash_amount).toFixed(2) }} </span>
            <span v-if="row.wechat_amount">微信¥{{ Number(row.wechat_amount).toFixed(2) }} </span>
            <span v-if="row.alipay_amount">支付宝¥{{ Number(row.alipay_amount).toFixed(2) }} </span>
            <span v-if="row.credit_amount">赊账¥{{ Number(row.credit_amount).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">详情</el-button>
            <el-button link type="warning" v-if="row.status==='pending'" @click="handleVoid(row)">作废</el-button>
            <el-button link type="danger" v-if="row.status==='locked'||row.status==='settled'" @click="handleReverse(row)">红冲</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>

    <!-- 新开销售单弹窗 -->
    <el-dialog v-model="dialogVisible" title="新开销售单" width="900px" :close-on-click-modal="false">
      <el-form :model="form" label-width="80px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="客户" required>
              <el-select v-model="form.customer_id" filterable placeholder="选择客户" style="width:100%">
                <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="仓库" required>
              <el-select v-model="form.warehouse_id" filterable placeholder="选择仓库" style="width:100%">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="备注">
              <el-input v-model="form.remark" placeholder="备注" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider content-position="left">商品明细</el-divider>
        <el-table :data="form.items" border size="small">
          <el-table-column label="商品" min-width="200">
            <template #default="{ row, $index }">
              <el-select v-model="row.product_id" filterable placeholder="选择商品" style="width:100%" @change="onProductChange($index)">
                <el-option v-for="p in products" :key="p.id" :label="`${p.name}(${p.spec||''})`" :value="p.id" />
              </el-select>
            </template>
          </el-table-column>
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
          <el-table-column label="操作" width="60">
            <template #default="{ $index }">
              <el-button link type="danger" @click="form.items.splice($index, 1)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button style="margin-top:8px" @click="form.items.push({product_id:null,quantity:1,unit_price:0})">+ 添加商品</el-button>
        <el-divider content-position="left">收款方式</el-divider>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="现金">
              <el-input-number v-model="form.cash_amount" :min="0" :precision="2" size="small" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="微信">
              <el-input-number v-model="form.wechat_amount" :min="0" :precision="2" size="small" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="支付宝">
              <el-input-number v-model="form.alipay_amount" :min="0" :precision="2" size="small" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="赊账">
              <el-input-number v-model="form.credit_amount" :min="0" :precision="2" size="small" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <div style="text-align:right;font-size:16px;font-weight:bold">
          合计：¥{{ formTotal.toFixed(2) }}
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="销售单详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="单号">{{ detail.delivery_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusMap[detail.status]?.type">{{ statusMap[detail.status]?.label }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="客户">{{ detail.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="仓库">{{ detail.warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ Number(detail.total_amount||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detail.remark || '-' }}</el-descriptions-item>
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

    <!-- 作废弹窗 -->
    <el-dialog v-model="voidVisible" title="作废销售单" width="400px">
      <el-form label-width="80px">
        <el-form-item label="作废原因" required>
          <el-input v-model="voidReason" type="textarea" :rows="3" placeholder="请输入作废原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="voidVisible=false">取消</el-button>
        <el-button type="danger" @click="confirmVoid" :loading="saving">确认作废</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSalesDeliveries, createSalesDelivery, getSalesDelivery, voidSalesDelivery, reverseSalesDelivery, getCustomers, getWarehouses, getProducts } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, status: '', customer_id: '', date_range: [] })
const dialogVisible = ref(false)
const detailVisible = ref(false)
const voidVisible = ref(false)
const saving = ref(false)
const detail = ref({})
const voidReason = ref('')
const currentVoidId = ref(null)

const customers = ref([])
const warehouses = ref([])
const products = ref([])

const statusMap = {
  pending: { label: '待处理', type: 'info' },
  settling: { label: '交账中', type: 'warning' },
  settled: { label: '已交账', type: 'success' },
  voided: { label: '已作废', type: 'danger' },
  locked: { label: '已锁定', type: '' },
  reversed: { label: '已红冲', type: 'danger' }
}

const form = ref({
  customer_id: null, warehouse_id: null, remark: '',
  cash_amount: 0, wechat_amount: 0, alipay_amount: 0, credit_amount: 0,
  items: [{ product_id: null, quantity: 1, unit_price: 0 }]
})

const formTotal = computed(() => {
  return form.value.items.reduce((sum, item) => sum + (item.quantity || 0) * (item.unit_price || 0), 0)
})

const loadData = async () => {
  const params = { ...query.value }
  if (params.date_range?.length === 2) {
    params.start_date = params.date_range[0]
    params.end_date = params.date_range[1]
  }
  delete params.date_range
  const res = await getSalesDeliveries(params)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadDropdowns = async () => {
  const [c, w, p] = await Promise.all([getCustomers(), getWarehouses(), getProducts()])
  customers.value = c.data || []
  warehouses.value = w.data || []
  products.value = p.data || []
}

const showDialog = () => {
  form.value = {
    customer_id: null, warehouse_id: null, remark: '',
    cash_amount: 0, wechat_amount: 0, alipay_amount: 0, credit_amount: 0,
    items: [{ product_id: null, quantity: 1, unit_price: 0 }]
  }
  dialogVisible.value = true
}

const onProductChange = (index) => {
  const p = products.value.find(x => x.id === form.value.items[index].product_id)
  if (p) form.value.items[index].unit_price = p.retail_price || 0
}

const handleSave = async () => {
  if (!form.value.customer_id) return ElMessage.warning('请选择客户')
  if (!form.value.warehouse_id) return ElMessage.warning('请选择仓库')
  if (form.value.items.length === 0 || !form.value.items[0].product_id) return ElMessage.warning('请添加商品')
  saving.value = true
  try {
    await createSalesDelivery(form.value)
    ElMessage.success('销售单创建成功')
    dialogVisible.value = false
    loadData()
  } finally {
    saving.value = false
  }
}

const showDetail = async (row) => {
  const res = await getSalesDelivery(row.id)
  detail.value = res.data || res
  detailVisible.value = true
}

const handleVoid = (row) => {
  currentVoidId.value = row.id
  voidReason.value = ''
  voidVisible.value = true
}

const confirmVoid = async () => {
  if (!voidReason.value) return ElMessage.warning('请输入作废原因')
  saving.value = true
  try {
    await voidSalesDelivery(currentVoidId.value, { reason: voidReason.value })
    ElMessage.success('已作废')
    voidVisible.value = false
    loadData()
  } finally {
    saving.value = false
  }
}

const handleReverse = async (row) => {
  await ElMessageBox.confirm('确认红冲此销售单？', '红冲确认', { type: 'warning' })
  await reverseSalesDelivery(row.id)
  ElMessage.success('已红冲')
  loadData()
}

onMounted(() => { loadData(); loadDropdowns() })
</script>
