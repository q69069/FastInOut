<template>
  <el-dialog v-model="visible" title="冲红申请" width="420px" :close-on-click-modal="false">
    <el-form>
      <el-form-item label="冲红原因" required>
        <el-input v-model="reason" type="textarea" :rows="4" placeholder="请输入冲红原因（必填）" maxlength="200" show-word-limit />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="danger" @click="handleConfirm" :disabled="!reason.trim()">确认冲红</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'confirm'])

const visible = ref(false)
const reason = ref('')

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) reason.value = ''
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const handleCancel = () => {
  visible.value = false
}

const handleConfirm = () => {
  if (!reason.value.trim()) {
    ElMessage.warning('请输入冲红原因')
    return
  }
  emit('confirm', reason.value.trim())
  visible.value = false
}
</script>
