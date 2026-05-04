<template>
  <div>
    <el-card>
      <template #header>提成报表</template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item label="期间">
          <el-date-picker v-model="period" type="month" value-format="YYYY-MM" placeholder="选择月份" style="width:160px" />
        </el-form-item>
        <el-form-item><el-button type="primary" @click="loadData">查询</el-button></el-form-item>
        <el-form-item>
          <el-button type="warning" @click="showCalculateDialog">自动计算提成</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="data" border stripe>
        <el-table-column prop="employee_name" label="业务员" width="120" />
        <el-table-column prop="period" label="期间" width="100" />
        <el-table-column prop="base_amount" label="销售基数" width="120" align="right">
          <template #default="{ row }">¥{{ Number(row.base_amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="commission_rate" label="提成比例" width="100" align="right">
          <template #default="{ row }">{{ (row.commission_rate*100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="commission_amount" label="提成金额" width="120" align="right">
          <template #default="{ row }">¥{{ Number(row.commission_amount||0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status==='paid'?'success':'info'" size="small">{{ row.status==='paid'?'已发':'待发' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="calcVisible" title="自动计算提成" width="400px">
      <el-form label-width="80px">
        <el-form-item label="期间" required>
          <el-date-picker v-model="calcForm.period" type="month" value-format="YYYY-MM" style="width:100%" />
        </el-form-item>
        <el-form-item label="提成比例">
          <el-input-number v-model="calcForm.rate" :min="0" :max="1" :step="0.01" :precision="2" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="calcVisible=false">取消</el-button>
        <el-button type="primary" @click="handleCalculate" :loading="calculating">计算</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCommissions, calculateCommissions } from '../../api'

const period = ref('')
const data = ref([])
const calcVisible = ref(false)
const calculating = ref(false)
const calcForm = ref({ period: '', rate: 0.05 })

const loadData = async () => {
  const params = {}
  if (period.value) params.period = period.value
  const res = await getCommissions(params)
  data.value = res.data || []
}

const showCalculateDialog = () => {
  calcForm.value = { period: period.value || '', rate: 0.05 }
  calcVisible.value = true
}

const handleCalculate = async () => {
  if (!calcForm.value.period) return ElMessage.warning('请选择期间')
  calculating.value = true
  try {
    await calculateCommissions(calcForm.value)
    ElMessage.success('提成计算完成')
    calcVisible.value = false
    loadData()
  } finally { calculating.value = false }
}

onMounted(() => { loadData() })
</script>
