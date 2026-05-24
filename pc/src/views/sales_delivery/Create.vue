<template>
  <div class="delivery-page">
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <el-button text @click="$router.back()"><el-icon><ArrowLeft /></el-icon> 返回</el-button>
          <span class="title-text">销售单</span>
        </div>
        <div class="header-info">
          <span class="info-item">制单人：{{ authStore.displayName }}</span>
          <span class="info-item">{{ now }}</span>
        </div>
      </div>
    </el-card>

    <el-card class="form-card">
      <el-form :model="form" label-width="90px">
        <!-- 基本信息区 -->
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="客户" required>
              <el-select v-model="form.customer_id" filterable placeholder="搜索客户" style="width:100%">
                <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" @click="$nextTick(() => loadCustomerPrice(c.id))" />
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
            <el-form-item label="交易日期">
              <el-date-picker v-model="form.delivery_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="业务员">
              <el-select v-model="form.salesman_id" clearable filterable placeholder="选择业务员" style="width:100%">
                <el-option v-for="s in salesmen" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="送货员">
              <el-select v-model="form.deliverer" clearable filterable placeholder="选择送货员" style="width:100%">
                <el-option v-for="s in salesmen" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="备注">
              <el-input v-model="form.remark" placeholder="备注信息" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <!-- 商品明细 -->
      <div class="section-title">商品明细</div>
      <el-table :data="form.items" border size="small" class="items-table">
        <el-table-column type="index" label="序号" width="50" align="center" />
        <el-table-column label="商品" min-width="200">
          <template #default="{ row, $index }">
            <el-select v-model="row.product_id" filterable placeholder="搜索商品" style="width:100%" @change="onProductChange($index)">
              <el-option v-for="p in products" :key="p.id" :label="`${p.name}${p.spec ? '('+p.spec+')' : ''}`" :value="p.id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="单位" width="110" align="center">
          <template #default="{ row, $index }">
            <el-select v-if="row._availableUnits?.length" v-model="row._unitLevel" size="small" style="width:100px" @change="v => onUnitChange($index, v)">
              <el-option v-for="u in row._availableUnits" :key="u.unit_level" :label="u.unit_name" :value="u.unit_level" />
            </el-select>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="数量" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.quantity" :min="0.01" :precision="2" size="small" style="width:100%" />
          </template>
        </el-table-column>
        <el-table-column label="单价" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.unit_price" :min="0" :precision="2" size="small" style="width:100%" />
          </template>
        </el-table-column>
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ ((row.quantity || 0) * (row.unit_price || 0)).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="可用库存" width="100" align="right">
          <template #default="{ row }">{{ getStock(row) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="60">
          <template #default="{ $index }">
            <el-button link type="danger" @click="form.items.splice($index, 1)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button class="add-btn" @click="form.items.push({product_id:null,quantity:1,unit_price:0})">+ 添加商品</el-button>

      <!-- 财务结算 -->
      <div class="section-title">收款方式</div>
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
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item label="优惠金额">
            <el-input-number v-model="form.discount_amount" :min="0" :precision="2" size="small" style="width:100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 合计 -->
      <div class="total-row">
        <span class="total-label">合计：</span>
        <span class="total-value">¥{{ totalAmount.toFixed(2) }}</span>
      </div>

      <!-- 操作按钮 -->
      <div class="action-bar">
        <el-button @click="$router.back()">关闭</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getCustomers, getWarehouses, getSalesmen, createSalesDelivery } from '../../api'
import { useAuthStore } from '../../stores/auth'
import { useWarehouseProducts } from '../../utils/useWarehouseProducts'

const router = useRouter()
const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })

const saving = ref(false)
const customers = ref([])
const warehouses = ref([])
const form = ref({
  customer_id: null,
  warehouse_id: null,
  delivery_date: new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '-'),
  salesman_id: null,
  deliverer: null,
  remark: '',
  discount_amount: 0,
  cash_amount: 0,
  wechat_amount: 0,
  alipay_amount: 0,
  credit_amount: 0,
  items: [{ product_id: null, quantity: 1, unit_price: 0 }]
})
const { products, loadProducts } = useWarehouseProducts(() => form.value.warehouse_id)
const salesmen = ref([])

const totalAmount = computed(() => {
  return form.value.items.reduce((s, item) => s + (item.quantity || 0) * (item.unit_price || 0), 0)
})

const buildAvailableUnits = (p) => {
  if (!p) return []
  const baseId = p.base_unit_id || p.id
  const units = [{ unit_id: baseId, unit_level: 'small', unit_name: p.small_unit_name || p.unit || '基本单位', conv_rate: 1 }]
  if (p.medium_unit_name) units.push({ unit_id: baseId, unit_level: 'medium', unit_name: p.medium_unit_name, conv_rate: p.medium_conv_rate || 1 })
  if (p.large_unit_name) units.push({ unit_id: baseId, unit_level: 'large', unit_name: p.large_unit_name, conv_rate: p.large_conv_rate || 1 })
  return units
}

const getStock = (row) => {
  const p = products.value.find(x => x.id === row.product_id)
  const stock = p?.available_stock || p?.stock || 0
  const rate = row._unitConvRate || 1
  return rate > 1 ? (stock / rate).toFixed(2) : stock.toFixed(2)
}

const onProductChange = (index) => {
  const row = form.value.items[index]
  const p = products.value.find(x => x.id === row.product_id)
  if (p) {
    row._basePrice = p.retail_price || 0
    row.unit_price = row._basePrice
    row._availableUnits = buildAvailableUnits(p)
    if (row._availableUnits.length > 0) {
      const defaultUnit = row._availableUnits.find(u => u.unit_level === p.default_unit_level) || row._availableUnits[0]
      row.unit_id = defaultUnit.unit_id
      row._unitLevel = defaultUnit.unit_level
      row._unitConvRate = defaultUnit.conv_rate
      row.unit_price = parseFloat((row._basePrice * defaultUnit.conv_rate).toFixed(2))
    }
  }
}

const onUnitChange = (index, unitLevel) => {
  const row = form.value.items[index]
  const unit = row._availableUnits?.find(u => u.unit_level === unitLevel)
  if (unit && row._basePrice) {
    row._unitLevel = unit.unit_level
    row._unitConvRate = unit.conv_rate
    row.unit_price = parseFloat((row._basePrice * unit.conv_rate).toFixed(2))
  }
}

const loadCustomerPrice = (customerId) => {
  // 可根据客户等级获取对应价格体系
}

const handleSave = async () => {
  if (!form.value.customer_id) return ElMessage.warning('请选择客户')
  if (!form.value.warehouse_id) return ElMessage.warning('请选择仓库')
  if (!form.value.items.length || !form.value.items[0].product_id) return ElMessage.warning('请添加商品')

  saving.value = true
  try {
    const data = { ...form.value }
    data.items = data.items.filter(i => i.product_id).map(i => ({
      product_id: i.product_id,
      quantity: i.quantity,
      unit_price: i.unit_price,
      amount: (i.quantity || 0) * (i.unit_price || 0),
      unit_id: i.unit_id,
      unit_level: i._unitLevel || 'small',
      unit_conv_rate: i._unitConvRate || 1,
      unit_quantity: i.quantity
    }))
    await createSalesDelivery(data)
    ElMessage.success('保存成功')
    router.push('/sales-deliveries')
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const [c, w, s] = await Promise.all([
    getCustomers({ page_size: 1000 }),
    getWarehouses({ page_size: 100 }),
    getSalesmen({ page_size: 100 })
  ])
  customers.value = c.data?.list || c.data || []
  warehouses.value = w.data?.list || w.data || []
  salesmen.value = s.data?.list || s.data || []
  await loadProducts()
})
</script>

<style scoped>
.delivery-page { padding: 16px; background: #f5f5f5; min-height: 100vh }
.page-header { display: flex; justify-content: space-between; align-items: center }
.page-title { display: flex; align-items: center; gap: 12px }
.title-text { font-size: 18px; font-weight: 600; color: #303133 }
.header-info { display: flex; gap: 24px; color: #909399; font-size: 13px }
.info-item { display: flex; align-items: center; gap: 4px }
.form-card { margin-top: 12px }
.section-title { font-size: 14px; font-weight: 600; color: #303133; margin: 16px 0 10px; padding-left: 8px; border-left: 3px solid #409eff }
.items-table { margin-bottom: 8px }
.add-btn { margin-top: 8px }
.total-row { text-align: right; font-size: 18px; font-weight: 600; color: #303133; padding: 12px 0; border-top: 1px solid #eee; margin-top: 12px }
.total-label { color: #606266 }
.total-value { color: #f56c6c; margin-left: 8px }
.action-bar { display: flex; justify-content: flex-end; gap: 12px; padding: 16px 0 8px; border-top: 1px solid #f0f0f0; margin-top: 16px }
</style>
