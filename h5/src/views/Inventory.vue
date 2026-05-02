<template>
  <div class="inventory-page">
    <van-search v-model="keyword" placeholder="搜索商品名称/编码" @search="loadData" />
    <van-pull-refresh v-model="refreshing" @refresh="loadData">
      <van-list>
        <van-cell-group inset>
          <van-cell v-for="item in list" :key="item.id" :title="item.product_name" :label="item.warehouse_name">
            <template #value>
              <span :class="item.quantity < item.safe_stock ? 'low' : ''">
                {{ item.quantity }} {{ item.unit }}
              </span>
            </template>
          </van-cell>
        </van-cell-group>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getInventory } from '../api'

const keyword = ref('')
const list = ref([])
const refreshing = ref(false)

const loadData = async () => {
  try {
    const res = await getInventory({ keyword: keyword.value })
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
.inventory-page {
  min-height: 100vh;
  background: #f7f8fa;
}
.low {
  color: #ee0a24;
}
</style>
