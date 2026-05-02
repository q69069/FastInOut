<template>
  <div class="todo-page">
    <van-nav-bar title="待办任务" />
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :loading="loading" :finished="finished" finished-text="没有更多了" @load="loadData">
        <van-cell v-for="item in list" :key="item.id" :title="item.title" :label="item.description" center>
          <template #right-icon>
            <van-tag :type="item.status === '超时' ? 'danger' : item.status === '今日' ? 'warning' : 'success'">
              {{ item.status }}
            </van-tag>
          </template>
        </van-cell>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTodoTasks } from '../api'

const list = ref([])
const loading = ref(false)
const finished = ref(false)

const loadData = async () => {
  try {
    const res = await getTodoTasks()
    list.value = res.data || []
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
    finished.value = true
  }
}

onMounted(loadData)
</script>

<style scoped>
.todo-page { background: #f7f8fa; min-height: 100vh; }
</style>