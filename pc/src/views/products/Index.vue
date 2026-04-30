<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>商品管理</span>
          <el-button type="primary" @click="showDialog()">新增商品</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="搜索商品名称/编码" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="spec" label="规格" width="120" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="purchase_price" label="进价" width="100" />
        <el-table-column prop="sale_price" label="售价" width="100" />
        <el-table-column prop="stock_min" label="库存下限" width="100" />
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
    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑商品' : '新增商品'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="编码" required>
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="规格">
          <el-input v-model="form.spec" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="form.unit" />
        </el-form-item>
        <el-form-item label="进价">
          <el-input-number v-model="form.purchase_price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="售价">
          <el-input-number v-model="form.sale_price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="条码">
          <el-input v-model="form.barcode" />
        </el-form-item>
        <el-form-item label="库存下限">
          <el-input-number v-model="form.stock_min" :min="0" />
        </el-form-item>
        <el-form-item label="库存上限">
          <el-input-number v-model="form.stock_max" :min="0" />
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
import { getProducts, createProduct, updateProduct, deleteProduct } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, keyword: '' })
const dialogVisible = ref(false)
const form = ref({})

const loadData = async () => {
  const res = await getProducts(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDialog = (row) => {
  form.value = row ? { ...row } : { code: '', name: '', spec: '', unit: '个', purchase_price: 0, sale_price: 0, barcode: '', stock_min: 0, stock_max: 0 }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (form.value.id) {
    await updateProduct(form.value.id, form.value)
  } else {
    await createProduct(form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该商品？', '提示', { type: 'warning' })
  await deleteProduct(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
