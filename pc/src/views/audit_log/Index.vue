<template>
  <div>
    <el-card>
      <template #header>
        <span>审计日志</span>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="操作类型">
          <el-select v-model="query.method" clearable placeholder="全部" style="width:100px">
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item label="实体类型">
          <el-select v-model="query.entity_type" clearable placeholder="全部" style="width:120px">
            <el-option v-for="t in entityTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="query.date_range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="created_at" label="时间" width="170" />
        <el-table-column prop="username" label="操作人" width="100" />
        <el-table-column prop="method" label="方法" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.method==='DELETE'?'danger':row.method==='PUT'?'warning':'success'" size="small">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路径" min-width="250" show-overflow-tooltip />
        <el-table-column prop="entity_type" label="实体类型" width="100" />
        <el-table-column prop="entity_id" label="实体ID" width="80" align="center" />
        <el-table-column prop="ip_address" label="IP" width="130" />
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" layout="total, prev, pager, next" style="margin-top:16px" @current-change="loadData" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getHttpAuditLogs } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, method: '', entity_type: '', date_range: [] })

const entityTypes = ['product', 'customer', 'supplier', 'purchase', 'sales', 'inventory', 'finance', 'expense']

const loadData = async () => {
  const params = { ...query.value }
  if (params.date_range?.length === 2) {
    params.start_date = params.date_range[0]
    params.end_date = params.date_range[1]
  }
  delete params.date_range
  const res = await getHttpAuditLogs(params)
  list.value = res.data || []
  total.value = res.total || 0
}

onMounted(() => { loadData() })
</script>
