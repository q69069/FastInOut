<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>库存调拨</span>
          <el-button type="primary" @click="showDialog()">新增调拨</el-button>
        </div>
      </template>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="单号" width="150" />
        <el-table-column prop="from_warehouse_name" label="调出仓库" width="120" />
        <el-table-column prop="to_warehouse_name" label="调入仓库" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">
              {{ statusMap[row.status] || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <template v-if="row.status === 1">
              <el-button size="small" type="success" @click="handleConfirm(row)">确认</el-button>
              <el-button size="small" type="danger" @click="handleCancel(row)">取消</el-button>
            </template>
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

    <el-dialog v-model="dialogVisible" title="新增调拨单" width="900px">
      <el-form :model="form" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="调出仓库" required>
              <el-select v-model="form.from_warehouse_id" filterable placeholder="选择调出仓库">
                <el-option
                  v-for="w in warehouses"
                  :key="w.id"
                  :label="w.name"
                  :value="w.id"
                  :disabled="w.id === form.to_warehouse_id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="调入仓库" required>
              <el-select v-model="form.to_warehouse_id" filterable placeholder="选择调入仓库">
                <el-option
                  v-for="w in warehouses"
                  :key="w.id"
                  :label="w.name"
                  :value="w.id"
                  :disabled="w.id === form.from_warehouse_id"
                />
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
            <el-table-column label="操作" width="80">
              <template #default="{ $index }">
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
  getTransfers, createTransfer, confirmTransfer, cancelTransfer,
  getProducts, getWarehouses
} from '../../api'

const statusMap = { 1: '调拨中', 2: '已确认', 3: '已取消' }
const statusTagType = (status) => {
  const map = { 1: 'warning', 2: 'success', 3: 'info' }
  return map[status] || 'info'
}

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20 })
const dialogVisible = ref(false)
const form = ref({ from_warehouse_id: null, to_warehouse_id: null, remark: '', items: [] })
const warehouses = ref([])
const products = ref([])

const loadData = async () => {
  const res = await getTransfers(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadOptions = async () => {
  const [w, p] = await Promise.all([
    getWarehouses({ page_size: 100 }),
    getProducts({ page_size: 100 })
  ])
  warehouses.value = w.data || []
  products.value = p.data || []
}

const showDialog = () => {
  form.value = { from_warehouse_id: null, to_warehouse_id: null, remark: '', items: [] }
  dialogVisible.value = true
}

const addItem = () => {
  form.value.items.push({ product_id: null, quantity: 1 })
}

const handleSave = async () => {
  if (!form.value.from_warehouse_id || !form.value.to_warehouse_id) {
    ElMessage.warning('请选择调出仓库和调入仓库')
    return
  }
  if (form.value.from_warehouse_id === form.value.to_warehouse_id) {
    ElMessage.warning('调出仓库和调入仓库不能相同')
    return
  }
  if (!form.value.items.length) {
    ElMessage.warning('请至少添加一个商品')
    return
  }
  const invalidItem = form.value.items.find(item => !item.product_id || !item.quantity)
  if (invalidItem) {
    ElMessage.warning('请完善商品信息')
    return
  }
  await createTransfer(form.value)
  ElMessage.success('创建成功')
  dialogVisible.value = false
  loadData()
}

const handleConfirm = async (row) => {
  await ElMessageBox.confirm('确认该调拨单？', '提示', { type: 'warning' })
  await confirmTransfer(row.id)
  ElMessage.success('确认成功')
  loadData()
}

const handleCancel = async (row) => {
  await ElMessageBox.confirm('确认取消该调拨单？', '提示', { type: 'warning' })
  await cancelTransfer(row.id)
  ElMessage.success('已取消')
  loadData()
}

onMounted(() => {
  loadData()
  loadOptions()
})
</script>
