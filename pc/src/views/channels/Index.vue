<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>渠道管理</span>
          <el-button type="primary" @click="showDialog('create')">新增渠道</el-button>
        </div>
      </template>

      <el-form :inline="true" style="margin-bottom:16px">
        <el-form-item label="渠道名称">
          <el-input v-model="query.keyword" placeholder="渠道名称/编码" clearable style="width:200px" @keyup.enter="loadData" />
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
        <el-table-column prop="name" label="渠道名称" min-width="150" />
        <el-table-column prop="code" label="渠道编码" width="120" />
        <el-table-column prop="level" label="层级" width="80" />
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑渠道' : '新增渠道'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="渠道名称" required>
          <el-input v-model="form.name" placeholder="请输入渠道名称" />
        </el-form-item>
        <el-form-item label="渠道编码">
          <el-input v-model="form.code" placeholder="请输入渠道编码" @input="_codeEdited = true" />
        </el-form-item>
        <el-form-item label="层级">
          <el-input-number v-model="form.level" :min="1" :max="3" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="备注" />
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
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { pinyin } from 'pinyin-pro'
import { getChannels, createChannel, updateChannel, deleteChannel } from '../../api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const list = ref([])
const total = ref(0)
const currentItem = ref(null)

const query = ref({ page: 1, page_size: 20, keyword: '', status: null })
const form = ref({ name: '', code: '', level: 1, sort_order: 0, remark: '', status: 1 })
const _codeEdited = ref(false)

watch(() => form.value.name, (name) => {
  if (!isEdit.value && !_codeEdited.value && name) {
    form.value.code = pinyin(name, { pattern: 'first', toneType: 'none' }).replace(/\s/g, '')
  }
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getChannels(query.value)
    list.value = res.data || []
    total.value = res.total || 0
  } catch { list.value = [] }
  loading.value = false
}

const showDialog = (mode, item = null) => {
  _codeEdited.value = false
  if (mode === 'create') {
    isEdit.value = false
    form.value = { name: '', code: '', level: 1, sort_order: 0, remark: '', status: 1 }
    currentItem.value = null
  } else {
    isEdit.value = true
    currentItem.value = item
    form.value = { name: item.name, code: item.code || '', level: item.level || 1, sort_order: item.sort_order || 0, remark: item.remark || '', status: item.status }
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.name) { ElMessage.warning('请输入渠道名称'); return }
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateChannel({ id: currentItem.value.id, ...form.value })
      ElMessage.success('更新成功')
    } else {
      await createChannel(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch { ElMessage.error('操作失败') }
  submitting.value = false
}

const handleDelete = async (item) => {
  try {
    await ElMessageBox.confirm(`确认删除渠道「${item.name}」？`, '删除确认', { type: 'warning' })
    await deleteChannel(item.id)
    ElMessage.success('已删除')
    loadData()
  } catch (e) { console.error('操作失败:', e) }
}

onMounted(loadData)
</script>