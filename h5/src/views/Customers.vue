<template>
  <div class="customers-page">
    <van-nav-bar title="客户管理" />
    <van-search v-model="keyword" placeholder="搜索客户" @search="loadData" />
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :loading="loading" :finished="finished" finished-text="没有更多了" @load="loadData">
        <van-cell v-for="item in list" :key="item.id" :title="item.name" :label="item.phone || item.address" center>
          <template #extra>
            <van-button size="small" type="primary" @click="$router.push('/order?customer_id=' + item.id)">下单</van-button>
          </template>
        </van-cell>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCustomers } from '../api'

const list = ref([])
const loading = ref(false)
const finished = ref(false)
const keyword = ref('')

const loadData = async () => {
  try {
    const res = await getCustomers({ keyword: keyword.value })
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
.customers-page { background: #f7f8fa; min-height: 100vh; }
</style>