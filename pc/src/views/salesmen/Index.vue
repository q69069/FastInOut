<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>业务员管理</span>
          <div style="display:flex;gap:12px;align-items:center">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width:260px"
              @change="loadStats"
            />
            <el-button type="primary" @click="showDialog()">新增业务员</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20" style="margin-bottom:20px">
        <el-col :span="24">
          <div ref="chartRef" style="height:300px"></div>
        </el-col>
      </el-row>

      <el-table :data="list" border stripe>
        <el-table-column prop="employee_name" label="业务员" width="120" />
        <el-table-column label="提成比例" width="100">
          <template #default="{ row }">
            {{ ((row.commission_rate || 0) * 100).toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column label="目标金额" width="120">
          <template #default="{ row }">
            {{ (row.target_amount || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="实际销售" width="120">
          <template #default="{ row }">
            {{ getActual(row.employee_id) }}
          </template>
        </el-table-column>
        <el-table-column label="提成金额" width="120">
          <template #default="{ row }">
            {{ getCommission(row.employee_id) }}
          </template>
        </el-table-column>
        <el-table-column label="订单数" width="80">
          <template #default="{ row }">
            {{ getOrderCount(row.employee_id) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="showDialog(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑业务员' : '新增业务员'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="员工" required>
          <el-select v-model="form.employee_id" filterable placeholder="选择员工" :disabled="isEdit">
            <el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="提成比例">
          <el-input-number v-model="commissionPercent" :min="0" :max="100" :precision="1" :step="0.5" />
          <span style="margin-left:8px">%</span>
        </el-form-item>
        <el-form-item label="月度目标">
          <el-input-number v-model="form.target_amount" :min="0" :precision="2" :step="1000" style="width:200px" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getSalesmen, getSalesmanStats, createSalesman, updateSalesman, getEmployees } from '../../api'

const list = ref([])
const stats = ref([])
const employees = ref([])
const dateRange = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const form = ref({ employee_id: null, commission_rate: 0, target_amount: 0 })
const chartRef = ref(null)
let chart = null

const commissionPercent = computed({
  get: () => (form.value.commission_rate || 0) * 100,
  set: (val) => { form.value.commission_rate = (val || 0) / 100 }
})

const statsMap = computed(() => {
  const map = {}
  for (const s of stats.value) {
    map[s.employee_id] = s
  }
  return map
})

const getActual = (employeeId) => {
  return (statsMap.value[employeeId]?.actual_amount || 0).toFixed(2)
}
const getCommission = (employeeId) => {
  return (statsMap.value[employeeId]?.commission || 0).toFixed(2)
}
const getOrderCount = (employeeId) => {
  return statsMap.value[employeeId]?.order_count || 0
}

const loadList = async () => {
  try {
    const res = await getSalesmen()
    list.value = res.data || []
  } catch (e) { console.error("[list]", e) }
}

const loadStats = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const res = await getSalesmanStats(params)
    stats.value = res.data || []
    renderChart()
  } catch (e) { console.error("[list]", e) }
}

const loadEmployees = async () => {
  try {
    const res = await getEmployees({ page_size: 100 })
    employees.value = res.data || []
  } catch (e) { console.error("[list]", e) }
}

const showDialog = (row) => {
  if (row) {
    isEdit.value = true
    editId.value = row.id
    form.value = {
      employee_id: row.employee_id,
      commission_rate: row.commission_rate,
      target_amount: row.target_amount
    }
  } else {
    isEdit.value = false
    editId.value = null
    form.value = { employee_id: null, commission_rate: 0, target_amount: 0 }
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.employee_id) {
    ElMessage.warning('请选择员工')
    return
  }
  if (isEdit.value) {
    await updateSalesman(editId.value, form.value)
  } else {
    await createSalesman(form.value)
  }
  ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
  dialogVisible.value = false
  loadList()
  loadStats()
}

const renderChart = () => {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  const names = list.value.map(s => s.employee_name)
  const actualData = list.value.map(s => statsMap.value[s.employee_id]?.actual_amount || 0)
  const targetData = list.value.map(s => s.target_amount || 0)

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['实际销售', '目标金额'] },
    xAxis: { type: 'category', data: names },
    yAxis: { type: 'value' },
    series: [
      { name: '实际销售', type: 'bar', data: actualData, itemStyle: { color: '#409EFF' } },
      { name: '目标金额', type: 'bar', data: targetData, itemStyle: { color: '#E6A23C' } }
    ]
  })
}

onMounted(async () => {
  try {
    await Promise.all([loadEmployees(), loadList(), loadStats()])
    nextTick(() => renderChart())
  } catch (e) { console.error("[list]", e) }
})
</script>
