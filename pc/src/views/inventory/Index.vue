<template>
  <div class="order-page">
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">库存查询</span>
        </div>
        <div class="header-info">
          <span class="info-item">{{ now }}</span>
        </div>
        <div class="header-actions" />
      </div>
    </el-card>

    <!-- 查询模式 -->
    <el-card v-if="mode === 'query'" class="form-card">
      <el-form inline style="margin-bottom:12px">
        <el-form-item label="仓库">
          <el-select v-model="queryFilter.warehouse_id" clearable filterable placeholder="全部" style="width:150px">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="商品">
          <el-input v-model="queryFilter.keyword" clearable placeholder="商品名称/编码" style="width:160px" />
        </el-form-item>
        <el-form-item label="品牌">
          <el-select v-model="queryFilter.brand_id" clearable filterable placeholder="全部" style="width:140px">
            <el-option v-for="b in brands" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="queryFilter.category_id" clearable filterable placeholder="全部" style="width:140px">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="clearFilter">清空</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" border stripe show-summary :summary-method="getSummary">
        <el-table-column prop="warehouse_name" label="仓库" width="120" />
        <el-table-column prop="product_code" label="商品编码" width="120" />
        <el-table-column prop="product_name" label="商品名称" min-width="200" />
        <el-table-column prop="product_spec" label="规格" width="100" />
        <el-table-column prop="product_unit" label="单位" width="70" align="center" />
        <el-table-column prop="quantity" label="库存数量" width="100" align="right">
          <template #default="{ row }">{{ (row.quantity || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="cost_price" label="成本价" width="100" align="right">
          <template #default="{ row }">¥{{ (row.cost_price || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="retail_price" label="零售价" width="100" align="right">
          <template #default="{ row }">¥{{ (row.retail_price || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="total_value" label="库存金额" width="120" align="right">
          <template #default="{ row }">¥{{ (row.total_value || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="queryFilter.page"
        v-model:page-size="queryFilter.page_size"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top:16px;justify-content:flex-end"
        @current-change="loadData"
      />
    </el-card>


    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="库存详情" width="600px">
      <el-descriptions :column="2" border v-if="detail">
        <el-descriptions-item label="商品">{{ detail.product_name }}</el-descriptions-item>
        <el-descriptions-item label="仓库">{{ detail.warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="规格">{{ detail.product_spec || '-' }}</el-descriptions-item>
        <el-descriptions-item label="单位">{{ detail.product_unit }}</el-descriptions-item>
        <el-descriptions-item label="库存数量">{{ (detail.quantity || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="成本价">¥{{ (detail.cost_price || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="零售价">¥{{ (detail.retail_price || 0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="库存金额">¥{{ (detail.total_value || 0).toFixed(2) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getInventory, getWarehouses, getProducts } from '../../api'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const warehouses = ref([])
const products = ref([])
const list = ref([])
const total = ref(0)

const queryFilter = ref({ page: 1, page_size: 20, warehouse_id: '', keyword: '', brand_id: '', category_id: '' })

const detailVisible = ref(false)
const detail = ref({})

const loadData = async () => {
  const params = { ...queryFilter.value }
  if (!params.warehouse_id) delete params.warehouse_id
  if (!params.keyword) delete params.keyword
  if (!params.brand_id) delete params.brand_id
  if (!params.category_id) delete params.category_id
  const res = await getInventory(params)
  list.value = res.data || []
  total.value = res.total || 0
}

const clearFilter = () => {
  queryFilter.value = { page: 1, page_size: 20, warehouse_id: '', keyword: '', brand_id: '', category_id: '' }
  loadData()
}

const getSummary = ({ columns, data }) => {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (['quantity', 'total_value'].includes(col.property)) {
      const val = data.reduce((s, r) => s + (Number(r[col.property]) || 0), 0)
      sums[idx] = col.property === 'quantity' ? val.toFixed(2) : `¥${val.toFixed(2)}`
    }
  })
  return sums
}

const showDetail = (row) => {
  detail.value = row
  detailVisible.value = true
}

onMounted(async () => {
  const [w, p] = await Promise.all([
    getWarehouses({ page_size: 100 }),
    getProducts({ page_size: 1000 })
  ])
  warehouses.value = w.data?.list || w.data || []
  products.value = p.data?.list || p.data || []
  loadData()
})
</script>

<style scoped>
.order-page { padding: 16px; background: #f5f5f5; min-height: 100vh }
.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px }
.page-title { display: flex; align-items: center; gap: 12px }
.title-text { font-size: 18px; font-weight: 600; color: #303133 }
.header-info { display: flex; gap: 24px; color: #909399; font-size: 13px }
.header-actions { display: flex; gap: 8px }
.form-card { margin-top: 12px }
.section-title { font-size: 14px; font-weight: 600; color: #303133; margin: 16px 0 10px; padding-left: 8px; border-left: 3px solid #409eff }
.items-table { margin-bottom: 8px }
.add-btn { margin-top: 8px }
.total-row { text-align: right; font-size: 16px; font-weight: 600; color: #303133; padding: 12px 0; border-top: 1px solid #eee; margin-top: 12px }
.total-value { color: #f56c6c; margin-left: 8px }
.action-bar { display: flex; justify-content: flex-end; gap: 12px; padding: 16px 0 8px; border-top: 1px solid #f0f0f0; margin-top: 16px }
</style>