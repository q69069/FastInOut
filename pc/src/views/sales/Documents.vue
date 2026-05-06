<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>销售单据查看</span>
        </div>
      </template>
      <el-tabs v-model="activeTab" @tab-change="loadData">
        <el-tab-pane label="销售订单" name="order">
          <el-table :data="orderList" border stripe>
            <el-table-column prop="code" label="单号" width="150" />
            <el-table-column prop="customer_name" label="客户" />
            <el-table-column prop="warehouse_name" label="仓库" width="100" />
            <el-table-column prop="total_amount" label="金额" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusMap[row.status] || 'info'">{{ statusLabelMap[row.status] || '未知' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170" />
          </el-table>
          <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="orderTotal"
            layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadOrders" />
        </el-tab-pane>
        <el-tab-pane label="销售单" name="delivery">
          <el-table :data="deliveryList" border stripe>
            <el-table-column prop="delivery_no" label="单号" width="150" />
            <el-table-column prop="customer_name" label="客户" width="120" />
            <el-table-column prop="total_amount" label="金额" width="100" align="right">
              <template #default="{ row }">¥{{ Number(row.total_amount || 0).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="收款方式" width="180">
              <template #default="{ row }">
                <span v-if="row.cash_amount">现金{{ Number(row.cash_amount).toFixed(0) }} </span>
                <span v-if="row.wechat_amount">微信{{ Number(row.wechat_amount).toFixed(0) }} </span>
                <span v-if="row.alipay_amount">支付宝{{ Number(row.alipay_amount).toFixed(0) }} </span>
                <span v-if="row.credit_amount">赊账{{ Number(row.credit_amount).toFixed(0) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="deliveryStatusMap[row.status]?.type">{{ deliveryStatusMap[row.status]?.label || row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170" />
          </el-table>
          <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="deliveryTotal"
            layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadDeliveries" />
        </el-tab-pane>
        <el-tab-pane label="退货订单" name="returnOrder">
          <el-table :data="returnList" border stripe>
            <el-table-column prop="code" label="单号" width="150" />
            <el-table-column prop="customer_name" label="客户" />
            <el-table-column prop="total_amount" label="金额" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="returnStatusMap[row.status] || 'info'">{{ returnStatusLabelMap[row.status] || '未知' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170" />
          </el-table>
          <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="returnTotal"
            layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadReturns" />
        </el-tab-pane>
        <el-tab-pane label="退货单" name="returnDelivery">
          <el-table :data="returnDeliveryList" border stripe>
            <el-table-column prop="return_no" label="单号" width="150" />
            <el-table-column prop="customer_name" label="客户" />
            <el-table-column prop="total_amount" label="金额" width="100" align="right">
              <template #default="{ row }">¥{{ Number(row.total_amount || 0).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="returnDeliveryStatusMap[row.status]?.type">{{ returnDeliveryStatusMap[row.status]?.label || row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="170" />
          </el-table>
          <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="returnDeliveryTotal"
            layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadReturnDeliveries" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSalesOrders } from '../../api'
import { getSalesDeliveries } from '../../api'
import { getSalesReturns } from '../../api'
import { getReturnDeliveries } from '../../api'

const activeTab = ref('order')
const orderList = ref([])
const deliveryList = ref([])
const returnList = ref([])
const returnDeliveryList = ref([])
const orderTotal = ref(0)
const deliveryTotal = ref(0)
const returnTotal = ref(0)
const returnDeliveryTotal = ref(0)
const query = ref({ page: 1, page_size: 20 })

const statusMap = { 0: 'warning', 1: 'success', 3: 'info' }
const statusLabelMap = { 0: '待审核', 1: '已确认', 3: '已作废' }
const returnStatusMap = { 0: 'warning', 1: 'success', 2: 'info' }
const returnStatusLabelMap = { 0: '待审核', 1: '已确认', 2: '已作废' }
const deliveryStatusMap = {
  pending: { label: '待处理', type: 'warning' },
  settling: { label: '交账中', type: '' },
  settled: { label: '已交账', type: 'success' },
  voided: { label: '已作废', type: 'info' },
  locked: { label: '已锁定', type: 'warning' },
  reversed: { label: '已红冲', type: 'danger' },
}
const returnDeliveryStatusMap = {
  0: { label: '草稿', type: 'info' },
  1: { label: '已确认', type: 'success' },
  2: { label: '仓管已确认', type: '' },
  3: { label: '财务已确认', type: '' },
}

const loadOrders = async () => {
  try {
    const res = await getSalesOrders({ page: query.value.page, page_size: query.value.page_size })
    orderList.value = res.data.list || []
    orderTotal.value = res.data.total || 0
  } catch {}
}
const loadDeliveries = async () => {
  try {
    const res = await getSalesDeliveries({ page: query.value.page, page_size: query.value.page_size })
    deliveryList.value = res.data.list || []
    deliveryTotal.value = res.data.total || 0
  } catch {}
}
const loadReturns = async () => {
  try {
    const res = await getSalesReturns({ page: query.value.page, page_size: query.value.page_size })
    returnList.value = res.data.list || []
    returnTotal.value = res.data.total || 0
  } catch {}
}
const loadReturnDeliveries = async () => {
  try {
    const res = await getReturnDeliveries({ page: query.value.page, page_size: query.value.page_size })
    returnDeliveryList.value = res.data.list || []
    returnDeliveryTotal.value = res.data.total || 0
  } catch {}
}
const loadData = () => {
  query.value.page = 1
  if (activeTab.value === 'order') loadOrders()
  else if (activeTab.value === 'delivery') loadDeliveries()
  else if (activeTab.value === 'returnOrder') loadReturns()
  else if (activeTab.value === 'returnDelivery') loadReturnDeliveries()
}

onMounted(() => loadOrders())
</script>
