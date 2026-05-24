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
          <el-input v-model="query.keyword" placeholder="搜索名称/编码/品牌/首字母" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="query.status" placeholder="状态" clearable style="width:100px" @change="loadData">
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="brand_name" label="品牌" width="100" />
        <el-table-column prop="spec" label="规格" width="120" />
        <el-table-column prop="small_unit_name" label="单位" width="80" />
        <el-table-column label="进价" width="100" align="right">
          <template #default="{ row }">{{ row.purchase_price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="售价" width="100" align="right">
          <template #default="{ row }">{{ row.retail_price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="stock_min" label="库存下限" width="100" />
        <el-table-column label="状态" width="70" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.status" :active-value="1" :inactive-value="0" @change="(val) => toggleStatus(row, val)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
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
      <el-form :model="form" label-width="100px">
        <el-form-item label="编码" required>
          <el-input v-model="form.code" @input="_codeEdited = true" />
        </el-form-item>
        <el-form-item label="名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="规格">
          <el-input v-model="form.spec" />
        </el-form-item>
        <el-form-item label="品牌" required>
          <el-select v-model="form.brand_id" filterable placeholder="选择品牌" style="width:100%">
            <el-option v-for="b in brands" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>

        <el-divider content-position="left">单位与价格</el-divider>

        <el-form-item label="小单位" required>
          <div style="display:flex;gap:8px;width:100%">
            <el-select v-model="form.small_unit_name" filterable allow-create placeholder="选择单位" style="width:100px">
              <el-option v-for="u in allUnits" :key="u.name" :label="u.name" :value="u.name" />
            </el-select>
            <span style="line-height:32px;color:#909399;font-size:12px;width:60px">进价</span>
            <el-input-number v-model="smallPurchasePrice" :min="0" :precision="2" size="small" controls-position="right" style="width:100px" @change="onSmallPurchaseChange" />
            <span style="line-height:32px;color:#909399;font-size:12px;width:60px">售价</span>
            <el-input-number v-model="smallRetailPrice" :min="0" :precision="2" size="small" controls-position="right" style="width:100px" @change="onSmallRetailChange" />
          </div>
        </el-form-item>

        <el-form-item label="中单位">
          <div style="display:flex;gap:8px;width:100%">
            <el-select v-model="form.medium_unit_name" filterable allow-create clearable placeholder="选择单位" style="width:100px">
              <el-option v-for="u in allUnits" :key="u.name" :label="u.name" :value="u.name" />
            </el-select>
            <span style="line-height:32px;font-size:12px;white-space:nowrap">1 =</span>
            <el-input-number v-model="form.medium_conv_rate" :min="0" :precision="0" size="small" controls-position="right" style="width:80px" />
            <span style="line-height:32px;color:#909399;font-size:12px;white-space:nowrap">{{ form.small_unit_name || '小单位' }}</span>
            <el-input-number v-model="mediumPurchasePrice" :min="0" :precision="2" size="small" controls-position="right" style="width:100px" @change="onMediumPurchaseChange" :disabled="!form.medium_conv_rate" />
            <el-input-number v-model="mediumRetailPrice" :min="0" :precision="2" size="small" controls-position="right" style="width:100px" @change="onMediumRetailChange" :disabled="!form.medium_conv_rate" />
          </div>
        </el-form-item>

        <el-form-item label="大单位">
          <div style="display:flex;gap:8px;width:100%">
            <el-select v-model="form.large_unit_name" filterable allow-create clearable placeholder="选择单位" style="width:100px">
              <el-option v-for="u in allUnits" :key="u.name" :label="u.name" :value="u.name" />
            </el-select>
            <span style="line-height:32px;font-size:12px;white-space:nowrap">1 =</span>
            <el-input-number v-model="form.large_conv_rate" :min="0" :precision="0" size="small" controls-position="right" style="width:80px" />
            <span style="line-height:32px;color:#909399;font-size:12px;white-space:nowrap">{{ form.small_unit_name || '小单位' }}</span>
            <el-input-number v-model="largePurchasePrice" :min="0" :precision="2" size="small" controls-position="right" style="width:100px" @change="onLargePurchaseChange" :disabled="!form.large_conv_rate" />
            <el-input-number v-model="largeRetailPrice" :min="0" :precision="2" size="small" controls-position="right" style="width:100px" @change="onLargeRetailChange" :disabled="!form.large_conv_rate" />
          </div>
        </el-form-item>

        <el-form-item label="默认单位">
          <el-radio-group v-model="form.default_unit_level">
            <el-radio value="small">{{ form.small_unit_name || '小单位' }}</el-radio>
            <el-radio value="medium" :disabled="!form.medium_unit_name">{{ form.medium_unit_name || '中单位' }}</el-radio>
            <el-radio value="large" :disabled="!form.large_unit_name">{{ form.large_unit_name || '大单位' }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-divider content-position="left">其他</el-divider>
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
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { pinyin } from 'pinyin-pro'
import { getProducts, createProduct, updateProduct, deleteProduct, getAllUnits, getBrands } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, keyword: '', status: null })
const dialogVisible = ref(false)
const form = ref({})
const allUnits = ref([])
const brands = ref([])

// 表单中三级价格（用于 UI 绑定，不存 DB）
const smallPurchasePrice = ref(0)
const smallRetailPrice = ref(0)
const mediumPurchasePrice = ref(0)
const mediumRetailPrice = ref(0)
const largePurchasePrice = ref(0)
const largeRetailPrice = ref(0)

let _recalc = false
const _codeEdited = ref(false)

// 名称变化时自动生成首字母编码
watch(() => form.value.name, (name) => {
  if (name && !form.value.id && !_codeEdited.value) {
    form.value.code = pinyin(name, { pattern: 'first', toneType: 'none' }).replace(/\s/g, '')
  }
})

const recalcPricesFromSmall = () => {
  if (_recalc) return
  _recalc = true
  const pp = smallPurchasePrice.value || 0
  const rp = smallRetailPrice.value || 0
  if (form.value.medium_conv_rate) {
    mediumPurchasePrice.value = parseFloat((pp * form.value.medium_conv_rate).toFixed(2))
    mediumRetailPrice.value = parseFloat((rp * form.value.medium_conv_rate).toFixed(2))
  }
  if (form.value.large_conv_rate) {
    largePurchasePrice.value = parseFloat((pp * form.value.large_conv_rate).toFixed(2))
    largeRetailPrice.value = parseFloat((rp * form.value.large_conv_rate).toFixed(2))
  }
  _recalc = false
}

const onSmallPurchaseChange = () => { form.value.purchase_price = smallPurchasePrice.value; recalcPricesFromSmall() }
const onSmallRetailChange = () => { form.value.retail_price = smallRetailPrice.value; recalcPricesFromSmall() }

const onMediumPurchaseChange = () => {
  if (_recalc || !form.value.medium_conv_rate) return
  _recalc = true
  form.value.purchase_price = parseFloat(((mediumPurchasePrice.value || 0) / form.value.medium_conv_rate).toFixed(4))
  smallPurchasePrice.value = form.value.purchase_price
  recalcPricesFromSmall()
  _recalc = false
}

const onMediumRetailChange = () => {
  if (_recalc || !form.value.medium_conv_rate) return
  _recalc = true
  form.value.retail_price = parseFloat(((mediumRetailPrice.value || 0) / form.value.medium_conv_rate).toFixed(4))
  smallRetailPrice.value = form.value.retail_price
  recalcPricesFromSmall()
  _recalc = false
}

const onLargePurchaseChange = () => {
  if (_recalc || !form.value.large_conv_rate) return
  _recalc = true
  form.value.purchase_price = parseFloat(((largePurchasePrice.value || 0) / form.value.large_conv_rate).toFixed(4))
  smallPurchasePrice.value = form.value.purchase_price
  recalcPricesFromSmall()
  _recalc = false
}

const onLargeRetailChange = () => {
  if (_recalc || !form.value.large_conv_rate) return
  _recalc = true
  form.value.retail_price = parseFloat(((largeRetailPrice.value || 0) / form.value.large_conv_rate).toFixed(4))
  smallRetailPrice.value = form.value.retail_price
  recalcPricesFromSmall()
  _recalc = false
}

// 中/大单位换算率变化时重新计算对应价格
watch(() => form.value.medium_conv_rate, (v) => {
  if (v) { mediumPurchasePrice.value = parseFloat(((form.value.purchase_price || 0) * v).toFixed(2)); mediumRetailPrice.value = parseFloat(((form.value.retail_price || 0) * v).toFixed(2)) }
})
watch(() => form.value.large_conv_rate, (v) => {
  if (v) { largePurchasePrice.value = parseFloat(((form.value.purchase_price || 0) * v).toFixed(2)); largeRetailPrice.value = parseFloat(((form.value.retail_price || 0) * v).toFixed(2)) }
})

const loadData = async () => {
  const res = await getProducts(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadUnits = async () => {
  const res = await getAllUnits()
  allUnits.value = res.data || []
}

const loadBrands = async () => {
  const res = await getBrands({ page_size: 1000 })
  brands.value = res.data?.list || res.data || []
}

const showDialog = (row) => {
  _codeEdited.value = false
  if (row) {
    form.value = { ...row }
  } else {
    form.value = { code: '', name: '', spec: '', brand_id: null, small_unit_name: '', medium_unit_name: '', medium_conv_rate: null, large_unit_name: '', large_conv_rate: null, default_unit_level: 'small', purchase_price: 0, retail_price: 0, barcode: '', stock_min: 0, stock_max: 0 }
  }
  smallPurchasePrice.value = form.value.purchase_price || 0
  smallRetailPrice.value = form.value.retail_price || 0
  if (form.value.medium_conv_rate) {
    mediumPurchasePrice.value = parseFloat(((form.value.purchase_price || 0) * form.value.medium_conv_rate).toFixed(2))
    mediumRetailPrice.value = parseFloat(((form.value.retail_price || 0) * form.value.medium_conv_rate).toFixed(2))
  } else {
    mediumPurchasePrice.value = 0; mediumRetailPrice.value = 0
  }
  if (form.value.large_conv_rate) {
    largePurchasePrice.value = parseFloat(((form.value.purchase_price || 0) * form.value.large_conv_rate).toFixed(2))
    largeRetailPrice.value = parseFloat(((form.value.retail_price || 0) * form.value.large_conv_rate).toFixed(2))
  } else {
    largePurchasePrice.value = 0; largeRetailPrice.value = 0
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.brand_id) return ElMessage.warning('请选择品牌')
  form.value.purchase_price = smallPurchasePrice.value
  form.value.retail_price = smallRetailPrice.value
  // 清理空单位
  if (!form.value.medium_unit_name) { form.value.medium_conv_rate = null }
  if (!form.value.large_unit_name) { form.value.large_conv_rate = null }

  if (form.value.id) {
    await updateProduct(form.value.id, form.value)
  } else {
    await createProduct(form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

const toggleStatus = async (row, val) => {
  await updateProduct(row.id, { status: val })
  row.status = val
  ElMessage.success(val ? '已启用' : '已停用')
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该商品？', '提示', { type: 'warning' })
  await deleteProduct(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => {
  loadData()
  loadUnits()
  loadBrands()
})
</script>
