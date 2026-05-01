<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>客户价格等级</span>
          <el-button type="primary" @click="showDialog()">新增价格协议</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="客户">
          <el-select v-model="query.customer_id" placeholder="全部客户" clearable filterable style="width:200px">
            <el-option v-for="c in customerList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="customer_name" label="客户名称" />
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="price" label="专属价格" width="120" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="showDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑价格协议' : '新增价格协议'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="客户" required>
          <el-select v-model="form.customer_id" placeholder="请选择客户" filterable style="width:100%">
            <el-option v-for="c in customerList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="商品" required>
          <el-select v-model="form.product_id" placeholder="请选择商品" filterable style="width:100%">
            <el-option v-for="p in productList" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="专属价格" required>
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
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
  getCustomerPrices, createCustomerPrice, updateCustomerPrice, deleteCustomerPrice,
  getCustomers, getProducts
} from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, customer_id: null })
const dialogVisible = ref(false)
const form = ref({})
const customerList = ref([])
const productList = ref([])

const loadCustomers = async () => {
  try {
    const res = await getCustomers({ page: 1, page_size: 9999 })
    customerList.value = res.data || []
  } catch (e) {}
}

const loadProducts = async () => {
  try {
    const res = await getProducts({ page: 1, page_size: 9999 })
    productList.value = res.data || []
  } catch (e) {}
}

const loadData = async () => {
  try {
    const params = { page: query.value.page, page_size: query.value.page_size }
    if (query.value.customer_id) {
      params.customer_id = query.value.customer_id
    }
    const res = await getCustomerPrices(params)
    list.value = res.data || []
    total.value = res.total || 0
  } catch (e) {}
}

const showDialog = (row) => {
  form.value = row
    ? { ...row }
    : { customer_id: null, product_id: null, price: 0, remark: '' }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.customer_id) {
    ElMessage.warning('请选择客户')
    return
  }
  if (!form.value.product_id) {
    ElMessage.warning('请选择商品')
    return
  }
  if (form.value.id) {
    await updateCustomerPrice(form.value.id, form.value)
  } else {
    await createCustomerPrice(form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该价格协议？', '提示', { type: 'warning' })
  await deleteCustomerPrice(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(async () => {
  try {
    await Promise.all([loadCustomers(), loadProducts(), loadData()])
  } catch (e) {}
})
</script>
