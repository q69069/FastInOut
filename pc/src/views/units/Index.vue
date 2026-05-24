<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>单位列表</span>
          <el-button type="primary" @click="showUnitDialog()">新增单位</el-button>
        </div>
      </template>
      <el-form inline style="margin-bottom:16px">
        <el-form-item>
          <el-input v-model="unitQuery.keyword" placeholder="搜索单位名称/符号" clearable @keyup.enter="loadUnits" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadUnits">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="units" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="单位名称" />
        <el-table-column prop="symbol" label="符号" width="100" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="showUnitDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteUnit(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="unitQuery.page"
        v-model:page-size="unitQuery.page_size"
        :total="unitTotal"
        layout="total, prev, pager, next"
        style="margin-top:16px;justify-content:flex-end"
        @current-change="loadUnits"
      />
    </el-card>

    <el-dialog v-model="unitDialogVisible" :title="unitForm.id ? '编辑单位' : '新增单位'" width="500px">
      <el-form :model="unitForm" label-width="80px">
        <el-form-item label="单位名称" required>
          <el-input v-model="unitForm.name" placeholder="如：个、箱、件" />
        </el-form-item>
        <el-form-item label="符号">
          <el-input v-model="unitForm.symbol" placeholder="如：pcs、box" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="unitForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="unitDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUnit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUnits, createUnit, updateUnit, deleteUnit, getAllUnits } from '../../api'

const units = ref([])
const unitTotal = ref(0)
const unitQuery = ref({ page: 1, page_size: 20, keyword: '' })
const unitDialogVisible = ref(false)
const unitForm = ref({})

const loadUnits = async () => {
  const res = await getUnits(unitQuery.value)
  units.value = res.data || []
  unitTotal.value = res.total || 0
}

const loadAllUnits = async () => {
  const res = await getAllUnits()
}

const showUnitDialog = (row) => {
  unitForm.value = row ? { ...row } : { name: '', symbol: '', description: '' }
  unitDialogVisible.value = true
}

const handleSaveUnit = async () => {
  if (unitForm.value.id) {
    await updateUnit(unitForm.value.id, unitForm.value)
  } else {
    await createUnit(unitForm.value)
  }
  ElMessage.success('保存成功')
  unitDialogVisible.value = false
  loadUnits()
}

const handleDeleteUnit = async (row) => {
  await ElMessageBox.confirm('确定删除该单位？', '提示', { type: 'warning' })
  await deleteUnit(row.id)
  ElMessage.success('删除成功')
  loadUnits()
}

onMounted(() => {
  loadUnits()
})
</script>
