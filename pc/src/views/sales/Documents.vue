<!-- DEPRECATED: 功能已合并到 sales/All.vue，此文件未被路由引用，可安全删除 -->
<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>查看销售单据</span>
          <div style="display:flex;gap:8px">
            <el-button type="success" @click="$router.push('/sales-deliveries')">+ 新增</el-button>
            <el-button>批量操作</el-button>
            <el-button>导出</el-button>
          </div>
        </div>
      </template>
      <!-- 筛选表单 -->
      <el-form inline style="margin-bottom:12px" @submit.prevent="loadData">
        <el-form-item label="业务员">
          <el-select v-model="query.salesman_id" clearable filterable placeholder="全部" style="width:130px">
            <el-option v-for="s in salesmen" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="query.warehouse_id" clearable filterable placeholder="全部" style="width:130px">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="单据号">
          <el-input v-model="query.delivery_no" clearable placeholder="单据号" style="width:140px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="待处理" value="pending" />
            <el-option label="交账中" value="settling" />
            <el-option label="已交账" value="settled" />
            <el-option label="已作废" value="voided" />
            <el-option label="已锁定" value="locked" />
            <el-option label="已红冲" value="reversed" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间">
          <el-date-picker v-model="query.date_range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" />
        </el-form-item>
        <el-form-item label="客户">
          <el-select v-model="query.customer_id" clearable filterable placeholder="全部" style="width:150px">
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="clearFilter">清空</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="list" border stripe @selection-change="onSelectChange" show-summary :summary-method="getSummary">
        <el-table-column type="selection" width="40" />
        <el-table-column prop="delivery_no" label="编号" width="150">
          <template #default="{ row }">
            <span :style="{color: row.has_return ? '#67C23A' : ''}">{{ row.delivery_no }}</span>
            <el-tag v-if="row.has_return" size="small" type="success">含退</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="交易时间" width="150" formatter="formatDate" />
        <el-table-column prop="salesman_name" label="业务员" width="100" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="warehouse_name" label="仓库" width="100" />
        <el-table-column prop="total_amount" label="应收金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.total_amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="discount_amount" label="优惠金额" width="80" align="right">
          <template #default="{ row }">¥{{ Number(row.discount_amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="收款账户" width="200">
          <template #default="{ row }">
            <span v-if="row.cash_amount">现金{{ Number(row.cash_amount).toFixed(0) }} </span>
            <span v-if="row.bank_amount">银行{{ Number(row.bank_amount).toFixed(0) }} </span>
            <span v-if="row.wechat_amount">微信{{ Number(row.wechat_amount).toFixed(0) }} </span>
            <span v-if="row.alipay_amount">支付宝{{ Number(row.alipay_amount).toFixed(0) }} </span>
            <span v-if="row.pre_amount">预收款{{ Number(row.pre_amount).toFixed(0) }} </span>
          </template>
        </el-table-column>
        <el-table-column prop="credit_amount" label="欠款金额" width="100" align="right">
          <template #default="{ row }">¥{{ Number(row.credit_amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="approved_at" label="审核时间" width="150" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total"
        layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="销售单详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="单号">{{ detail.delivery_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusMap[detail.status]?.type">{{ statusMap[detail.status]?.label }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="客户">{{ detail.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="仓库">{{ detail.warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ Number(detail.total_amount||0).toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ fmtDateVal(detail.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detail.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="detail.items || []" border size="small" style="margin-top:16px">
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="quantity" label="数量" width="80" align="right" />
        <el-table-column prop="unit_price" label="单价" width="80" align="right" />
        <el-table-column prop="amount" label="金额" width="100" align="right" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSalesDeliveries } from '../../api'
import { getCustomers } from '../../api'
import { getWarehouses } from '../../api'
import { ElMessage } from 'element-plus'

const fmtDateVal = (v) => v ? String(v).replace("T", " ").slice(0, 16) : ""
const list = ref([])
const customers = ref([])
const warehouses = ref([])
const salesmen = ref([])
const total = ref(0)
const detailVisible = ref(false)
const detail = ref({})
const selected = ref([])
const query = ref({ page: 1, page_size: 20, date_range: [] })

const statusMap = {
  pending: { label: '待处理', type: 'warning' },
  settling: { label: '交账中', type: 'primary' },
  settled: { label: '已交账', type: 'success' },
  voided: { label: '已作废', type: 'info' },
  locked: { label: '已锁定', type: 'warning' },
  reversed: { label: '已红冲', type: 'danger' },
}

const loadData = async () => {
  const params = { page: query.value.page, page_size: query.value.page_size }
  if (query.value.customer_id) params.customer_id = query.value.customer_id
  if (query.value.warehouse_id) params.warehouse_id = query.value.warehouse_id
  if (query.value.salesman_id) params.salesman_id = query.value.salesman_id
  if (query.value.status) params.status = query.value.status
  if (query.value.delivery_no) params.delivery_no = query.value.delivery_no
  if (query.value.date_range && query.value.date_range.length === 2) {
    params.start_date = query.value.date_range[0]
    params.end_date = query.value.date_range[1]
  }
  try {
    const res = await getSalesDeliveries(params)
    list.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (e) { console.error('操作失败:', e) }
}

const clearFilter = () => {
  query.value = { page: 1, page_size: 20, date_range: [] }
  loadData()
}

const onSelectChange = (rows) => { selected.value = rows }

const getSummary = ({ columns, data }) => {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (['total_amount','discount_amount','cash_amount','bank_amount','wechat_amount','alipay_amount','pre_amount','credit_amount'].includes(col.property)) {
      const val = data.reduce((s, r) => s + Number(r[col.property] || 0), 0)
      sums[idx] = `¥${val.toFixed(2)}`
    }
  })
  return sums
}

const showDetail = (row) => {
  detail.value = row
  detailVisible.value = true
}

const loadCustomers = async () => {
  try {
    const res = await getCustomers({ page: 1, page_size: 1000 })
    customers.value = res.data.list || []
  } catch (e) { console.error('操作失败:', e) }
}
const loadWarehouses = async () => {
  try {
    const res = await getWarehouses({ page: 1, page_size: 1000 })
    warehouses.value = res.data.list || []
  } catch (e) { console.error('操作失败:', e) }
}

onMounted(() => {
  loadData()
  loadCustomers()
  loadWarehouses()
})
</script>
