<template>
  <el-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" :title="title" :width="width" destroy-on-close>
    <el-descriptions :column="2" border v-if="fields.length">
      <el-descriptions-item v-for="f in fields" :key="f.label" :label="f.label" :span="f.span || 1">
        <template v-if="f.type === 'tag'">
          <el-tag :type="f.tagType || 'info'" size="small">{{ f.value }}</el-tag>
        </template>
        <template v-else-if="f.type === 'money'">
          <span :style="{ color: f.color || '#303133', fontWeight: 600 }">¥{{ Number(f.value || 0).toFixed(2) }}</span>
        </template>
        <template v-else>{{ f.value ?? '-' }}</template>
      </el-descriptions-item>
    </el-descriptions>

    <el-table :data="items" border size="small" style="margin-top:16px" v-if="items.length" show-summary :summary-method="summaryMethod">
      <el-table-column v-for="col in itemColumns" :key="col.prop" :prop="col.prop" :label="col.label" :width="col.width" :align="col.align || 'left'" :min-width="col.minWidth">
        <template #default="{ row }" v-if="col.type === 'money'">
          ¥{{ Number(row[col.prop] || 0).toFixed(2) }}
        </template>
      </el-table-column>
    </el-table>
  </el-dialog>
</template>

<script setup>
defineOptions({ name: 'DocumentDetail' })

defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '单据详情' },
  width: { type: String, default: '700px' },
  fields: { type: Array, default: () => [] },
  items: { type: Array, default: () => [] },
  itemColumns: { type: Array, default: () => [] },
  summaryMethod: { type: Function, default: null }
})

defineEmits(['update:modelValue'])
</script>
