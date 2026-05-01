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
        <el-table-column prop="unit" label="基本单位" width="100" />
        <el-table-column prop="purchase_price" label="进价" width="100" />
        <el-table-column prop="retail_price" label="零售价" width="100" />
        <el-table-column prop="stock_min" label="库存下限" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="showDialog(row)">编辑</el-button>
            <el-button size="small" @click="showUnitConfig(row)">单位换算</el-button>
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
        <el-form-item label="基本单位" required>
          <el-select v-model="form.unit" filterable allow-create placeholder="选择或输入单位" style="width:100%">
            <el-option v-for="u in allUnits" :key="u.id" :label="`${u.name} (${u.symbol || ''})`" :value="u.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="进价">
          <el-input-number v-model="form.purchase_price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="零售价">
          <el-input-number v-model="form.retail_price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="会员价">
          <el-input-number v-model="form.member_price" :min="0" :precision="2" />
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

    <!-- 单位换算配置弹窗 -->
    <el-dialog v-model="unitConfigVisible" title="单位换算配置" width="700px">
      <div style="margin-bottom:16px">
        <strong>商品：</strong>{{ currentProduct?.name }}
        <strong>基本单位：</strong>{{ currentProduct?.unit }}
      </div>
      <div style="margin-bottom:16px">
        <el-button type="primary" size="small" @click="showAddConversion">添加换算关系</el-button>
      </div>
      <el-table :data="productConversions" border stripe>
        <el-table-column prop="from_unit_name" label="源单位" />
        <el-table-column prop="to_unit_name" label="目标单位" />
        <el-table-column prop="ratio" label="换算比例" />
        <el-table-column prop="level" label="层级" width="80" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="handleDeleteConversion(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 添加换算表单 -->
      <el-card v-if="showAddConvForm" style="margin-top:16px">
        <el-form :model="newConversion" label-width="80px" inline>
          <el-form-item label="源单位" required>
            <el-select v-model="newConversion.from_unit_id" placeholder="选择单位" style="width:120px">
              <el-option v-for="u in allUnits" :key="u.id" :label="u.name" :value="u.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="=">
            <span style="font-size:18px">=</span>
          </el-form-item>
          <el-form-item label="比例" required>
            <el-input-number v-model="newConversion.ratio" :min="0.001" :precision="3" style="width:120px" />
          </el-form-item>
          <el-form-item label="目标单位" required>
            <el-select v-model="newConversion.to_unit_id" placeholder="选择单位" style="width:120px">
              <el-option v-for="u in allUnits" :key="u.id" :label="u.name" :value="u.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="层级">
            <el-input-number v-model="newConversion.level" :min="1" :max="10" style="width:80px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="small" @click="handleAddConversion">确定</el-button>
            <el-button size="small" @click="showAddConvForm = false">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getProducts, createProduct, updateProduct, deleteProduct,
  getAllUnits, getProductUnitConfig, createUnitConversion, deleteUnitConversion
} from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, keyword: '' })
const dialogVisible = ref(false)
const form = ref({})

// 单位相关
const allUnits = ref([])
const unitConfigVisible = ref(false)
const currentProduct = ref(null)
const productConversions = ref([])
const showAddConvForm = ref(false)
const newConversion = ref({ from_unit_id: null, to_unit_id: null, ratio: 1, level: 1 })

const loadData = async () => {
  const res = await getProducts(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadUnits = async () => {
  const res = await getAllUnits()
  allUnits.value = res.data || []
}

const showDialog = (row) => {
  form.value = row ? { ...row } : { code: '', name: '', spec: '', unit: '', purchase_price: 0, retail_price: 0, member_price: 0, barcode: '', stock_min: 0, stock_max: 0 }
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

// 单位换算配置
const showUnitConfig = async (row) => {
  currentProduct.value = row
  unitConfigVisible.value = true
  showAddConvForm.value = false
  await loadProductConversions(row.id)
}

const loadProductConversions = async (productId) => {
  const res = await getProductUnitConfig(productId)
  productConversions.value = res.data?.conversions || []
}

const showAddConversion = () => {
  newConversion.value = { product_id: currentProduct.value.id, from_unit_id: null, to_unit_id: null, ratio: 1, level: 1 }
  showAddConvForm.value = true
}

const handleAddConversion = async () => {
  if (!newConversion.value.from_unit_id || !newConversion.value.to_unit_id) {
    ElMessage.warning('请选择源单位和目标单位')
    return
  }
  await createUnitConversion(newConversion.value)
  ElMessage.success('添加成功')
  showAddConvForm.value = false
  await loadProductConversions(currentProduct.value.id)
}

const handleDeleteConversion = async (row) => {
  await ElMessageBox.confirm('确定删除该换算关系？', '提示', { type: 'warning' })
  await deleteUnitConversion(row.id)
  ElMessage.success('删除成功')
  await loadProductConversions(currentProduct.value.id)
}

onMounted(() => {
  loadData()
  loadUnits()
})
</script>
