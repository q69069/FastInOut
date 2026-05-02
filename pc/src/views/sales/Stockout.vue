<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>销售出库单</span>
          <el-button type="primary" @click="showDialog()">新增出库</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="搜索单号" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="query.status" clearable placeholder="状态" style="width:100px">
            <el-option label="草稿" :value="0" />
            <el-option label="已出库" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="单号" width="150" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="warehouse_name" label="仓库" width="100" />
        <el-table-column prop="total_amount" label="金额" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 2 ? 'success' : 'warning'">
              {{ statusMap[row.status] || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 0" size="small" @click="showDialog(row)">编辑</el-button>
            <el-button v-if="row.status === 0" size="small" type="success" @click="handleConfirm(row)">确认出库</el-button>
            <el-button v-if="row.status === 0" size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑出库单' : '新增出库单'" width="800px">
      <el-form :model="form" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户" required>
              <el-select v-model="form.customer_id" filterable placeholder="选择客户" style="width:100%">
                <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="仓库" required>
              <el-select v-model="form.warehouse_id" filterable placeholder="选择仓库" style="width:100%">
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
                <el-select v-model="row.product_id" filterable placeholder="选择商品" style="width:100%">
                  <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="数量" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.quantity" :min="1" size="small" style="width:100%" />
              </template>
            </el-table-column>
            <el-table-column label="单价" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.price" :min="0" :precision="2" size="small" style="width:100%" />
              </template>
            </el-table-column>
            <el-table-column label="金额" width="100">
              <template #default="{ row }">
                {{ ((row.quantity || 0) * (row.price || 0)).toFixed(2) }}
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
import {
  getSalesStockouts, createSalesStockout, updateSalesStockout, deleteSalesStockout, confirmSalesStockout,
  getProducts, getCustomers, getWarehouses
} from '../../api'

const statusMap = { 0: '草稿', 1: '已确认', 2: '已出库', 3: '已关闭' }
const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, keyword: '', status: null })
const dialogVisible = ref(false)
const form = ref({})
const customers = ref([])
const warehouses = ref([])
const products = ref([])

const loadData = async () => {
  const params = { ...query.value }
  if (!params.status) delete params.status
  if (!params.keyword) delete params.keyword
  const res = await getSalesStockouts(params)
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
    const res = await getSalesStockout(id)
    if (res.data && res.data.items) {
      form.value.items = res.data.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        price: item.price
      }))
    }
  } catch (e) {
    console.error('[Stockout] loadOrderItems error:', e)
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
    await updateSalesStockout(form.value.id, data)
    ElMessage.success('更新成功')
  } else {
    await createSalesStockout(data)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  loadData()
}

const handleConfirm = async (row) => {
  await ElMessageBox.confirm('确认出库？库存将减少！', '提示', { type: 'warning' })
  await confirmSalesStockout(row.id)
  ElMessage.success('出库确认成功')
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该出库单？', '提示', { type: 'warning' })
  await deleteSalesStockout(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => {
  loadData()
  loadOptions()
})
</script>
