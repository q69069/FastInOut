<template>
  <div class="order-page">
    <el-card class="header-card">
      <div class="page-header">
        <div class="page-title">
          <span class="title-text">异常监控</span>
        </div>
        <div class="header-info">
          <span class="info-item">{{ now }}</span>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="loadData">刷新</el-button>
        </div>
      </div>
    </el-card>

    <el-card class="form-card">
      <el-form inline style="margin-bottom:12px">
        <el-form-item label="检测天数">
          <el-input-number v-model="params.days" :min="1" :max="90" style="width:120px" />
        </el-form-item>
        <el-form-item label="偏差阈值">
          <el-input-number v-model="params.threshold" :min="0.1" :max="1" :step="0.05" :precision="2" style="width:120px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">检测</el-button>
        </el-form-item>
      </el-form>

      <el-alert :title="`发现 ${anomalies.length} 条异常`" :type="anomalies.length ? 'warning' : 'success'" show-icon style="margin-bottom:16px" />

      <el-table :data="anomalies" border stripe>
        <el-table-column label="严重度" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'high' ? 'danger' : 'warning'" size="small">{{ row.severity === 'high' ? '高' : '中' }}</el-tag>
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

const now = new Date().toLocaleString('zh-CN')
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

<style scoped>
.order-page { padding: 16px; background: #f5f5f5; min-height: 100vh }
.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px }
.page-title { display: flex; align-items: center; gap: 12px }
.title-text { font-size: 18px; font-weight: 600; color: #303133 }
.header-info { display: flex; gap: 24px; color: #909399; font-size: 13px }
.header-actions { display: flex; gap: 8px }
.form-card { margin-top: 12px }
</style>
