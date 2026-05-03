<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>销售订单</span>
          <el-button v-if="authStore.hasOperation('sales:create')" type="primary" @click="showDialog()">新增订单</el-button>
        </div>
      </template>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="单号" width="150" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="warehouse_name" label="仓库" width="100" />
        <el-table-column prop="total_amount" label="金额" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : row.status === 3 ? 'info' : 'warning'">
              {{ statusMap[row.status] || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="authStore.can('sales', 'edit') && row.status === 0" size="small" @click="showDialog(row)">编辑</el-button>
            <el-button v-if="authStore.hasOperation('sales:create') && row.status === 0" size="small" type="primary" @click="handleStockout(row)">生成出库</el-button>
            <el-button v-if="authStore.can('sales', 'delete') && row.status === 0" size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" title="新增销售订单" width="800px">
      <el-form :model="form" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户" required>
              <el-select v-model="form.customer_id" filterable placeholder="选择客户">
                <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="仓库" required>
              <el-select v-model="form.warehouse_id" filterable placeholder="选择仓库">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" />
        </el-form-item>
        <el-form-item label="商品明细">
          <el-button size="small" @click="addItem">添加商品</el-button>
          <el-table :data="form.items" border style="margin-top:8px">
            <el-table-column label="商品">
              <template #default="{ row }">
                <el-select v-model="row.product_id" filterable placeholder="选择商品">
                  <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="数量" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.quantity" :min="1" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="单价" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.price" :min="0" :precision="2" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row, $index }">
                <el-button size="small" type="danger" @click="form.items.splice($index, 1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSalesOrders, createSalesOrder, updateSalesOrder, deleteSalesOrder, orderToStockout, getProducts, getCustomers, getWarehouses } from '../../api'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const statusMap = { 0: '草稿', 1: '已确认', 2: '已出库', 3: '已关闭' }
const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20 })
const dialogVisible = ref(false)
const form = ref({})
const customers = ref([])
const warehouses = ref([])
const products = ref([])

const loadData = async () => {
  const res = await getSalesOrders(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadOptions = async () => {
  const [c, w, p] = await Promise.all([
    getCustomers({ page_size: 100 }),
    getWarehouses({ page_size: 100 }),
    getProducts({ page_size: 100 })
  ])
  customers.value = c.data || []
  warehouses.value = w.data || []
  products.value = p.data || []
}

const showDialog = (row) => {
  if (row) {
    form.value = { ...row, items: [] }
    loadOrderItems(row.id)
  } else {
    form.value = { customer_id: null, warehouse_id: null, remark: '', items: [] }
  }
  dialogVisible.value = true
}

const loadOrderItems = async (id) => {
  try {
    const res = await getSalesOrder(id)
    if (res.data && res.data.items) {
      form.value.items = res.data.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        price: item.price
      }))
    }
  } catch (e) {
    console.error('[SalesOrder] loadOrderItems error:', e)
  }
}

const addItem = () => {
  form.value.items.push({ product_id: null, quantity: 1, price: 0 })
}

const handleSave = async () => {
  if (!form.value.customer_id) return ElMessage.warning('请选择客户')
  if (!form.value.warehouse_id) return ElMessage.warning('请选择仓库')
  if (!form.value.items || form.value.items.length === 0) return ElMessage.warning('请添加商品')

  const data = {
    customer_id: form.value.customer_id,
    warehouse_id: form.value.warehouse_id,
    remark: form.value.remark,
    items: form.value.items.map(item => ({
      product_id: item.product_id,
      quantity: item.quantity,
      price: item.price,
      amount: (item.quantity || 0) * (item.price || 0)
    }))
  }

  if (form.value.id) {
    await updateSalesOrder(form.value.id, data)
    ElMessage.success('更新成功')
  } else {
    await createSalesOrder(data)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  loadData()
}

const handleStockout = async (row) => {
  await ElMessageBox.confirm('确定生成出库单？', '提示', { type: 'warning' })
  await orderToStockout(row.id)
  ElMessage.success('出库单已生成')
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该订单？', '提示', { type: 'warning' })
  await deleteSalesOrder(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => {
  loadData()
  loadOptions()
})
</script>
