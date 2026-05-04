<template>
  <div>
    <el-card>
      <template #header>销售明细报表</template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="日期">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" />
        </el-form-item>
        <el-form-item label="维度">
          <el-select v-model="groupBy" style="width:120px">
            <el-option label="按商品" value="product" />
            <el-option label="按客户" value="customer" />
            <el-option label="按业务员" value="employee" />
            <el-option label="按日期" value="date" />
            <el-option label="按仓库" value="warehouse" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" @click="loadData">查询</el-button></el-form-item>
      </el-form>
      <el-table :data="data" border stripe show-summary :summary-method="getSummaries">
        <el-table-column prop="label" label="名称" min-width="200" />
        <el-table-column prop="quantity" label="数量" width="100" align="right" />
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ Number(row.amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="count" label="单数" width="80" align="center" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSalesDetailReport } from '../../api'

const dateRange = ref([])
const groupBy = ref('product')
const data = ref([])

const loadData = async () => {
  const params = { group_by: groupBy.value }
  if (dateRange.value?.length === 2) {
    params.start_date = dateRange.value[0]
    params.end_date = dateRange.value[1]
  }
  const res = await getSalesDetailReport(params)
  data.value = res.data || []
}

const getSummaries = ({ columns, data }) => {
  return columns.map((col, i) => {
    if (i === 0) return '合计'
    if (col.property === 'quantity') return data.reduce((s, r) => s + (r.quantity || 0), 0).toFixed(0)
    if (col.property === 'amount') return '¥' + data.reduce((s, r) => s + (r.amount || 0), 0).toFixed(2)
    if (col.property === 'count') return data.reduce((s, r) => s + (r.count || 0), 0)
    return ''
  })
}

onMounted(() => { loadData() })
</script>
