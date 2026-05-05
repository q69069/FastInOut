<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>客户等级</span>
          <el-button type="primary" @click="showDialog('create')">新增等级</el-button>
        </div>
      </template>

      <el-form :inline="true" style="margin-bottom:16px">
        <el-form-item label="等级名称">
          <el-input v-model="query.keyword" placeholder="等级名称/编码" clearable style="width:200px" @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px" @change="loadData">
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="等级名称" width="120" />
        <el-table-column prop="code" label="等级编码" width="120" />
        <el-table-column prop="discount_rate" label="折扣率" width="100">
          <template #default="{ row }">{{ ((row.discount_rate || 1) * 10).toFixed(1) }}折</template>
        </el-table-column>
        <el-table-column prop="credit_limit" label="信用额度" width="120">
          <template #default="{ row }">¥{{ (row.credit_limit || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="showDialog('edit', row)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        style="margin-top:16px"
        @size-change="loadData"
        @current-change="loadData"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑等级' : '新增等级'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="等级名称" required>
          <el-input v-model="form.name" placeholder="如：A级/B级/C级" />
        </el-form-item>
        <el-form-item label="等级编码">
          <el-input v-model="form.code" placeholder="如：A/B/C" />
        </el-form-item>
        <el-form-item label="折扣率">
          <el-input-number v-model="form.discount_rate" :min="0" :max="1" :precision="2" :step="0.05" />
          <span style="margin-left:8px;color:#999">0.95=九五折</span>
        </el-form-item>
        <el-form-item label="信用额度">
          <el-input-number v-model="form.credit_limit" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" rows="3" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCustomerLevels, createCustomerLevel, updateCustomerLevel, deleteCustomerLevel } from '../../api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const list = ref([])
const total = ref(0)
const currentItem = ref(null)

const query = ref({ page: 1, page_size: 20, keyword: '', status: null })
const form = ref({ name: '', code: '', discount_rate: 1.0, credit_limit: 0, sort_order: 0, remark: '', status: 1 })

const loadData = async () => {
  loading.value = true
  try {
    const res = await getCustomerLevels(query.value)
    list.value = res.data || []
    total.value = res.total || 0
  } catch { list.value = [] }
  loading.value = false
}

const showDialog = (mode, item = null) => {
  if (mode === 'create') {
    isEdit.value = false
    form.value = { name: '', code: '', discount_rate: 1.0, credit_limit: 0, sort_order: 0, remark: '', status: 1 }
    currentItem.value = null
  } else {
    isEdit.value = true
    currentItem.value = item
    form.value = { name: item.name, code: item.code || '', discount_rate: item.discount_rate || 1.0, credit_limit: item.credit_limit || 0, sort_order: item.sort_order || 0, remark: item.remark || '', status: item.status }
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.name) { ElMessage.warning('请输入等级名称'); return }
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateCustomerLevel({ id: currentItem.value.id, ...form.value })
      ElMessage.success('更新成功')
    } else {
      await createCustomerLevel(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch { ElMessage.error('操作失败') }
  submitting.value = false
}

const handleDelete = async (item) => {
  try {
    await ElMessageBox.confirm(`确认删除等级「${item.name}」？`, '删除确认', { type: 'warning' })
    await deleteCustomerLevel(item.id)
    ElMessage.success('已删除')
    loadData()
  } catch {}
}

onMounted(loadData)
</script>