<template>
  <div class="stamp-wrapper">
    <div v-if="isReversed" class="stamp stamp-red">已冲红</div>
    <div v-else-if="isAudited" class="stamp stamp-green">已审核</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: [Number, String], default: 0 },
  // 数字状态中，哪些值算"已审核"，默认 [1,2]（采购/销售 1=已确认，调拨/盘点 2=已审核）
  confirmedStatuses: { type: Array, default: () => [1, 2] }
})

const stringConfirmed = [
  'confirmed', 'completed', 'loaded', 'adjusted', 'settled',
  'warehouse_confirmed', 'finance_confirmed', 'locked'
]
const stringReversed = ['reversed', 'voided']

const isAudited = computed(() => {
  const s = props.status
  if (typeof s === 'string') {
    return stringConfirmed.includes(s)
  }
  return props.confirmedStatuses.includes(s)
})

const isReversed = computed(() => {
  const s = props.status
  if (typeof s === 'string') {
    return stringReversed.includes(s)
  }
  return s === 3 || s === 4
})
</script>

<style scoped>
.stamp-wrapper {
  position: absolute;
  top: 10px;
  right: 20px;
  z-index: 10;
  pointer-events: none;
}
.stamp {
  padding: 6px 16px;
  border: 3px solid;
  border-radius: 8px;
  font-size: 20px;
  font-weight: bold;
  transform: rotate(-15deg);
  opacity: 0.55;
  white-space: nowrap;
}
.stamp-green {
  color: #67C23A;
  border-color: #67C23A;
}
.stamp-red {
  color: #F56C6C;
  border-color: #F56C6C;
}
</style>
