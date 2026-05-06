<template>
  <div class="return-page">
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <el-button text @click="$router.back()"><el-icon><ArrowLeft /></el-icon> 返回</el-button>
          <span class="title-text">退货订单</span>
        </div>
        <div class="header-info">
          <span class="info-item">制单人：{{ authStore.displayName }}</span>
          <span class="info-item">{{ now }}</span>
        </div>
      </div>
    </el-card>

    <el-card class="form-card">
      <el-form :model="form" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="客户" required>
              <el-select v-model="form.customer_id" filterable placeholder="搜索客户" style="width:100%">
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
              <el-input v-model="form.remark" placeholder="备注信息" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

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
        <el-table-column label="单位" width="80" align="center">
          <template #default="{ row }">{{ getUnit(row.product_id) }}</template>
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
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ ((row.quantity || 0) * (row.price || 0)).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="60">
          <template #default="{ $index }">
            <el-button link type="danger" @click="form.items.splice($index, 1)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button class="add-btn" @click="form.items.push({product_id:null,quantity:1,price:0})">+ 添加商品</el-button>

      <div class="total-row">
        <span class="total-label">合计：</span>
        <span class="total-value">¥{{ totalAmount.toFixed(2) }}</span>
      </div>

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
import { getCustomers, getWarehouses, getProducts, createSalesReturn } from '../../api'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const now = new Date().toLocaleString('zh-CN')

const saving = ref(false)
const customers = ref([])
const warehouses = ref([])
const products = ref([])

const form = ref({
  customer_id: null,
  warehouse_id: null,
  remark: '',
  items: [{ product_id: null, quantity: 1, price: 0 }]
})

const totalAmount = computed(() => {
  return form.value.items.reduce((s, item) => s + (item.quantity || 0) * (item.price || 0), 0)
})

const getUnit = (productId) => {
  const p = products.value.find(x => x.id === productId)
  return p?.unit || '-'
}

const onProductChange = (index) => {
  const p = products.value.find(x => x.id === form.value.items[index].product_id)
  if (p) form.value.items[index].price = p.retail_price || 0
}

const handleSave = async () => {
  if (!form.value.customer_id) return ElMessage.warning('请选择客户')
  if (!form.value.warehouse_id) return ElMessage.warning('请选择仓库')
  if (!form.value.items.length || !form.value.items[0].product_id) return ElMessage.warning('请添加商品')

  saving.value = true
  try {
    const data = {
      customer_id: form.value.customer_id,
      warehouse_id: form.value.warehouse_id,
      remark: form.value.remark,
      items: form.value.items.filter(i => i.product_id).map(i => ({
        product_id: i.product_id,
        quantity: i.quantity,
        price: i.price,
        amount: (i.quantity || 0) * (i.price || 0)
      }))
    }
    await createSalesReturn(data)
    ElMessage.success('保存成功')
    router.push('/sales-returns')
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const [c, w, p] = await Promise.all([
    getCustomers({ page_size: 1000 }),
    getWarehouses({ page_size: 100 }),
    getProducts({ page_size: 1000 })
  ])
  customers.value = c.data?.list || c.data || []
  warehouses.value = w.data?.list || w.data || []
  products.value = p.data?.list || p.data || []
})
</script>

<style scoped>
.return-page { padding: 16px; background: #f5f5f5; min-height: 100vh }
.page-header { display: flex; justify-content: space-between; align-items: center }
.page-title { display: flex; align-items: center; gap: 12px }
.title-text { font-size: 18px; font-weight: 600; color: #303133 }
.header-info { display: flex; gap: 24px; color: #909399; font-size: 13px }
.form-card { margin-top: 12px }
.section-title { font-size: 14px; font-weight: 600; color: #303133; margin: 16px 0 10px; padding-left: 8px; border-left: 3px solid #409eff }
.items-table { margin-bottom: 8px }
.add-btn { margin-top: 8px }
.total-row { text-align: right; font-size: 18px; font-weight: 600; color: #303133; padding: 12px 0; border-top: 1px solid #eee; margin-top: 12px }
.total-value { color: #f56c6c; margin-left: 8px }
.action-bar { display: flex; justify-content: flex-end; gap: 12px; padding: 16px 0 8px; border-top: 1px solid #f0f0f0; margin-top: 16px }
</style>
