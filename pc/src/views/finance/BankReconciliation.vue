<template>
  <div>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>银行对账</span>
              <div>
                <el-button type="primary" @click="showDialog()">新增流水</el-button>
                <el-button type="success" @click="handleAutoMatch">自动匹配</el-button>
              </div>
            </div>
          </template>
          <el-form inline style="margin-bottom:16px">
            <el-form-item>
              <el-select v-model="query.matched" clearable placeholder="匹配状态" style="width:120px">
                <el-option label="已匹配" :value="true" />
                <el-option label="未匹配" :value="false" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width:240px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadData">查询</el-button>
            </el-form-item>
          </el-form>
          <el-table :data="list" border stripe>
            <el-table-column prop="statement_date" label="日期" width="100" />
            <el-table-column prop="bank_account" label="银行账号" width="120" />
            <el-table-column prop="description" label="摘要" min-width="150" />
            <el-table-column prop="debit" label="支出" width="100">
              <template #default="{ row }">
                <span v-if="row.debit" style="color:#f56c6c">{{ row.debit.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="credit" label="收入" width="100">
              <template #default="{ row }">
                <span v-if="row.credit" style="color:#67c23a">{{ row.credit.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="matched" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.matched ? 'success' : 'warning'">{{ row.matched ? '已匹配' : '未匹配' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="matched_type" label="匹配类型" width="80">
              <template #default="{ row }">
                {{ row.matched_type === 'receipt' ? '收款' : row.matched_type === 'payment' ? '付款' : '' }}
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="query.page"
            v-model:page-size="query.page_size"
            :total="total"
            layout="total, prev, pager, next"
            style="margin-top:16px;justify-content:flex-end"
            @current-change="loadData"
          />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>对账汇总</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="总收入">{{ summary.total_credit?.toFixed(2) || '0.00' }}</el-descriptions-item>
            <el-descriptions-item label="总支出">{{ summary.total_debit?.toFixed(2) || '0.00' }}</el-descriptions-item>
            <el-descriptions-item label="余额">
              <span :style="{ color: summary.balance >= 0 ? '#67c23a' : '#f56c6c' }">{{ summary.balance?.toFixed(2) || '0.00' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="已匹配">{{ summary.matched_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="未匹配">{{ summary.unmatched_count || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="dialogVisible" title="新增银行流水" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="日期" required>
          <el-date-picker v-model="form.statement_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="银行账号">
          <el-input v-model="form.bank_account" />
        </el-form-item>
        <el-form-item label="摘要" required>
          <el-input v-model="form.description" />
        </el-form-item>
        <el-form-item label="支出">
          <el-input-number v-model="form.debit" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="收入">
          <el-input-number v-model="form.credit" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" />
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getBankStatements, createBankStatement, autoMatchBankStatements, getBankSummary } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, matched: null })
const dateRange = ref([])
const dialogVisible = ref(false)
const form = ref({})
const summary = ref({})

const loadData = async () => {
  const params = { ...query.value }
  if (dateRange.value?.length === 2) {
    params.start_date = dateRange.value[0]
    params.end_date = dateRange.value[1]
  }
  if (params.matched === null) delete params.matched
  const res = await getBankStatements(params)
  list.value = res.data || []
  total.value = res.total || 0
}

const loadSummary = async () => {
  const res = await getBankSummary()
  summary.value = res.data || {}
}

const showDialog = () => {
  form.value = { statement_date: '', bank_account: '', description: '', debit: 0, credit: 0, remark: '' }
  dialogVisible.value = true
}

const handleSave = async () => {
  await createBankStatement(form.value)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
  loadSummary()
}

const handleAutoMatch = async () => {
  const res = await autoMatchBankStatements()
  ElMessage.success(res.message || '自动匹配完成')
  loadData()
  loadSummary()
}

onMounted(() => {
  loadData()
  loadSummary()
})
</script>
