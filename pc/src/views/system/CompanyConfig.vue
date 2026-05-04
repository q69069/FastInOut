<template>
  <div>
    <el-card>
      <template #header>公司设置</template>
      <el-form label-width="200px" style="max-width:600px">
        <el-form-item v-for="item in configs" :key="item.config_key" :label="item.description || item.config_key">
          <el-input v-model="item.config_value" :placeholder="item.description" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="saving">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const configs = ref([])
const saving = ref(false)

const loadData = async () => {
  // 使用通用 API 获取配置
  const { default: api } = await import('../../api')
  const res = await api.get('/company-configs')
  configs.value = res.data || []
}

const handleSave = async () => {
  saving.value = true
  try {
    const { default: api } = await import('../../api')
    for (const item of configs.value) {
      await api.put(`/company-configs/${item.id}`, { config_value: item.config_value })
    }
    ElMessage.success('设置已保存')
  } finally { saving.value = false }
}

onMounted(() => { loadData() })
</script>
