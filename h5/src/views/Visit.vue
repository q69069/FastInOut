<template>
  <div class="visit-page">
    <van-pull-refresh v-model="refreshing" @refresh="loadData">
      <van-list>
        <van-cell-group inset>
          <van-cell v-for="item in list" :key="item.id" :title="item.customer_name" :label="item.visit_time">
            <template #value>
              <van-tag :type="item.result === 'success' ? 'success' : 'warning'">
                {{ item.result_text }}
              </van-tag>
            </template>
          </van-cell>
        </van-cell-group>
      </van-list>
    </van-pull-refresh>
    <van-floating-button icon="plus" position="right-bottom" @click="showAdd = true" />
    <van-dialog v-model:show="showAdd" title="新建拜访" @confirm="handleAdd">
      <van-form>
        <van-field v-model="form.customer_id" label="客户" placeholder="选择客户" />
        <van-field v-model="form.remark" label="备注" placeholder="拜访备注" />
      </van-form>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getVisits, createVisit } from '../api'

const list = ref([])
const refreshing = ref(false)
const showAdd = ref(false)
const form = ref({ customer_id: null, remark: '' })

const loadData = async () => {
  try {
    const res = await getVisits()
    list.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    refreshing.value = false
  }
}

const handleAdd = async () => {
  await createVisit(form.value)
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.visit-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-top: 16px;
}
</style>
