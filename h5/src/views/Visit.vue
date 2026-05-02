<template>
  <div class="visit-page">
    <van-nav-bar title="拜访记录" />
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :loading="loading" :finished="finished" finished-text="没有更多了" @load="loadData">
        <van-cell v-for="item in list" :key="item.id" :title="item.customer_name" :label="item.visit_time" center />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getVisits } from '../api'

const list = ref([])
const loading = ref(false)
const finished = ref(false)

const loadData = async () => {
  try {
    const res = await getVisits()
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
.visit-page { background: #f7f8fa; min-height: 100vh; }
</style>