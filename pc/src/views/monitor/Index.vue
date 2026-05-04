<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>异常交易监控</span>
          <el-button type="primary" @click="loadData">刷新</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="检测天数">
          <el-input-number v-model="params.days" :min="1" :max="90" style="width:120px" />
        </el-form-item>
        <el-form-item label="偏差阈值">
          <el-input-number v-model="params.threshold" :min="0.1" :max="1" :step="0.05" :precision="2" style="width:120px" />
        </el-form-item>
        <el-form-item><el-button type="primary" @click="loadData">检测</el-button></el-form-item>
      </el-form>

      <el-alert :title="`发现 ${anomalies.length} 条异常`" :type="anomalies.length ? 'warning' : 'success'" show-icon style="margin-bottom:16px" />

      <el-table :data="anomalies" border stripe>
        <el-table-column label="严重度" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.severity==='high'?'danger':'warning'" size="small">{{ row.severity==='high'?'高':'中' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            {{ typeMap[row.type] || row.type }}
          </template>
        </el-table-column>
        <el-table-column prop="desc" label="描述" min-width="250" />
        <el-table-column prop="detail" label="详情" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="170" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAnomalies } from '../../api'

const params = ref({ days: 7, threshold: 0.3 })
const anomalies = ref([])

const typeMap = {
  void_reopen: '作废复开',
  price_deviation: '单价异常',
  high_credit: '赊账过高',
  multi_return: '多次退货'
}

const loadData = async () => {
  const res = await getAnomalies(params.value)
  anomalies.value = res.data?.items || []
}

onMounted(() => { loadData() })
</script>
