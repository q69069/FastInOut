<template>
  <div class="todo-page">
    <van-pull-refresh v-model="refreshing" @refresh="loadData">
      <van-list>
        <van-cell-group inset>
          <van-cell v-for="item in list" :key="item.id" :title="item.title" :value="item.status_text" />
        </van-cell-group>
      </van-list>
    </van-pull-refresh>
    <div class="empty" v-if="list.length === 0">
      <van-empty description="暂无待办任务" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTodoTasks } from '../api'

const list = ref([])
const refreshing = ref(false)

const loadData = async () => {
  try {
    const res = await getTodoTasks()
    list.value = res.data || []
  } catch (e) {
    console.error(e)
  } finally {
    refreshing.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.todo-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-top: 16px;
}
.empty {
  margin-top: 60px;
}
</style>
