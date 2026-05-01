<template>
  <div>
    <el-form inline style="margin-bottom:16px">
      <el-form-item label="操作人">
        <el-input v-model="query.operator" placeholder="操作人" clearable style="width:150px" @keyup.enter="loadData" />
      </el-form-item>
      <el-form-item label="操作类型">
        <el-select v-model="query.action" placeholder="全部" clearable style="width:120px" @change="loadData">
          <el-option label="新增" value="新增" />
          <el-option label="修改" value="修改" />
          <el-option label="删除" value="删除" />
          <el-option label="审核" value="审核" />
          <el-option label="登录" value="登录" />
          <el-option label="导入" value="导入" />
        </el-select>
      </el-form-item>
      <el-form-item label="关键词">
        <el-input v-model="query.keyword" placeholder="操作对象" clearable style="width:180px" @keyup.enter="loadData" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="loadData">查询</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="list" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="operator" label="操作人" width="100" />
      <el-table-column prop="action" label="操作类型" width="90">
        <template #default="{ row }">
          <el-tag :type="actionType(row.action)" size="small">{{ row.action }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="target" label="操作对象" min-width="200" />
      <el-table-column prop="detail" label="详情" min-width="250" show-overflow-tooltip />
      <el-table-column prop="ip" label="IP" width="130" />
      <el-table-column prop="created_at" label="时间" width="170" />
    </el-table>

    <el-pagination
      v-model:current-page="query.page"
      v-model:page-size="query.page_size"
      :total="total"
      :page-sizes="[20,50,100]"
      layout="total, sizes, prev, pager, next"
      style="margin-top:16px;justify-content:flex-end"
      @current-change="loadData"
      @size-change="loadData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOperationLogs } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, operator: '', action: '', keyword: '' })

const actionType = (action) => {
  const map = { '新增': 'success', '修改': 'warning', '删除': 'danger', '审核': '', '登录': 'info', '导入': '' }
  return map[action] || ''
}

const loadData = async () => {
  const res = await getOperationLogs(query.value)
  list.value = res.data || []
  total.value = res.total || 0
}

onMounted(() => loadData())
</script>
