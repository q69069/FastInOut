<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>退货单管理</span>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="草稿" :value="0" />
            <el-option label="已确认" :value="1" />
            <el-option label="仓管已确认" :value="2" />
            <el-option label="财务已确认" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="客户">
          <el-select v-model="query.customer_id" clearable filterable placeholder="全部" style="width:160px">
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="code" label="单号" width="150" />
        <el-table-column prop="customer_name" label="客户" width="120" />
        <el-table-column prop="total_amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_amount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label || '未知' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">详情</el-button>
            <el-button link type="success" v-if="row.status===0" @click="handleWarehouseConfirm(row)">仓管确认</el-button>
            <el-button link type="warning" v-if="row.status===2" @click="handleFinanceConfirm(row)">财务确认</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="退货单详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="单号">{{ detail.code }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusMap[detail.status]?.type">{{ statusMap[detail.status]?.label }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="客户">{{ detail.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ Number(detail.total_amount||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ detail.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="detail.items || []" border size="small" style="margin-top:16px">
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="quantity" label="数量" width="100" align="right" />
        <el-table-column prop="price" label="单价" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.price||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.amount||0).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getReturnDeliveries, getReturnDelivery, warehouseConfirmReturn, financeConfirmReturn, getCustomers } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, status: '', customer_id: '' })
const detailVisible = ref(false)
const detail = ref({})
const customers = ref([])

const statusMap = {
  0: { label: '草稿', type: 'info' },
  1: { label: '已确认', type: '' },
  2: { label: '仓管已确认', type: 'warning' },
  3: { label: '财务已确认', type: 'success' }
}

const loadData = async () => {
  const res = await getReturnDeliveries(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadCustomers = async () => {
  const res = await getCustomers()
  customers.value = res.data || []
}

const showDetail = async (row) => {
  const res = await getReturnDelivery(row.id)
  detail.value = res.data || res
  detailVisible.value = true
}

const handleWarehouseConfirm = async (row) => {
  await ElMessageBox.confirm('确认退货入库？将增加库存', '仓管确认', { type: 'warning' })
  await warehouseConfirmReturn(row.id)
  ElMessage.success('仓管确认成功，退货已入库')
  loadData()
}

const handleFinanceConfirm = async (row) => {
  await ElMessageBox.confirm('确认冲减客户应收？', '财务确认', { type: 'warning' })
  await financeConfirmReturn(row.id)
  ElMessage.success('财务确认成功，已冲减客户应收')
  loadData()
}

onMounted(() => { loadData(); loadCustomers() })
</script>
