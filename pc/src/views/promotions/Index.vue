<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>促销方案</span>
          <el-button type="primary" @click="showDialog()">新增方案</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="搜索方案名称" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item>
          <el-select v-model="query.status" clearable placeholder="状态" style="width:100px">
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" border stripe>
        <el-table-column prop="name" label="方案名称" min-width="180" />
        <el-table-column prop="promo_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.promo_type === 'threshold' ? 'warning' : 'success'">
              {{ row.promo_type === 'threshold' ? '满减' : '折扣' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="规则" min-width="200">
          <template #default="{ row }">
            <span v-if="row.promo_type === 'threshold'">满 {{ row.threshold_amount }} 减 {{ row.discount_value }}</span>
            <span v-else>{{ (row.discount_value * 10).toFixed(1) }} 折</span>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始时间" width="180" />
        <el-table-column prop="end_date" label="结束时间" width="180" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="showDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑方案' : '新增方案'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="方案名称" required>
          <el-input v-model="form.name" placeholder="如：满100减10" />
        </el-form-item>
        <el-form-item label="促销类型">
          <el-radio-group v-model="form.promo_type">
            <el-radio value="threshold">满减</el-radio>
            <el-radio value="discount">折扣</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.promo_type === 'threshold'" label="满减门槛" required>
          <el-input-number v-model="form.threshold_amount" :min="0.01" :precision="2" />
          <span style="margin-left:8px">元</span>
        </el-form-item>
        <el-form-item :label="form.promo_type === 'threshold' ? '减免金额' : '折扣比例'" required>
          <el-input-number v-if="form.promo_type === 'threshold'" v-model="form.discount_value" :min="0.01" :precision="2" />
          <el-input-number v-else v-model="form.discount_value" :min="0.01" :max="0.99" :precision="2" :step="0.05" />
          <span style="margin-left:8px">{{ form.promo_type === 'threshold' ? '元' : '(如0.85=八五折)' }}</span>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker v-model="form.start_date" type="datetime" placeholder="选择开始时间" style="width:100%" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker v-model="form.end_date" type="datetime" placeholder="选择结束时间" style="width:100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPromotions, createPromotion, updatePromotion, deletePromotion } from '../../api'

const list = ref([])
const total = ref(0)
const query = ref({ page: 1, page_size: 20, keyword: '', status: '' })
const dialogVisible = ref(false)
const form = ref({})

const loadData = async () => {
  const params = { ...query.value }
  if (params.status === '') delete params.status
  const res = await getPromotions(params)
  list.value = res.data || []
  total.value = res.total || 0
}

const showDialog = (row) => {
  form.value = row ? { ...row } : {
    name: '', promo_type: 'threshold', threshold_amount: 100, discount_value: 10,
    start_date: null, end_date: null, status: 1, remark: ''
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.name) { ElMessage.error('请输入方案名称'); return }
  if (form.value.id) {
    await updatePromotion(form.value.id, form.value)
  } else {
    await createPromotion(form.value)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  loadData()
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该促销方案？', '提示', { type: 'warning' })
  await deletePromotion(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
