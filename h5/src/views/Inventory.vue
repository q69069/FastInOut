<template>
  <div class="inventory-page">
    <van-nav-bar title="库存查询" />
    <van-search v-model="keyword" placeholder="搜索商品" @search="loadData" />
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :loading="loading" :finished="finished" finished-text="没有更多了" @load="loadData">
        <van-cell v-for="item in list" :key="item.id" :title="item.product_name" :label="item.warehouse_name">
          <template #extra>
            <span style="color: #1989fa;">{{ item.quantity }}</span>
          </template>
        </van-cell>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getInventory } from '../api'

const list = ref([])
const loading = ref(false)
const finished = ref(false)
const keyword = ref('')

const loadData = async () => {
  try {
    const res = await getInventory({ keyword: keyword.value })
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
.inventory-page { background: #f7f8fa; min-height: 100vh; }
</style>