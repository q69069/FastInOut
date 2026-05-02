<template>
  <div class="receivables-page">
    <van-nav-bar title="应收查询" />
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :loading="loading" :finished="finished" finished-text="没有更多了" @load="loadData">
        <van-cell v-for="item in list" :key="item.id" :title="item.customer_name" :label="`账龄: ${item.days}天`">
          <template #extra>
            <span :style="{ color: item.days > 30 ? '#ee0a24' : '#1989fa' }">
              ¥{{ item.amount }}
            </span>
          </template>
        </van-cell>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getReceivables } from '../api'

const list = ref([])
const loading = ref(false)
const finished = ref(false)

const loadData = async () => {
  try {
    const res = await getReceivables()
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
.receivables-page { background: #f7f8fa; min-height: 100vh; }
</style>