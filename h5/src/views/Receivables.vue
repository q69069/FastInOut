<template>
  <div class="receivables-page">
    <van-pull-refresh v-model="refreshing" @refresh="loadData">
      <van-list>
        <van-cell-group inset>
          <van-cell v-for="item in list" :key="item.id" :title="item.customer_name" :label="item.overdue_days ? `逾期${item.overdue_days}天` : ''">
            <template #value>
              <span :class="item.overdue_days ? 'overdue' : ''">¥{{ item.amount }}</span>
            </template>
          </van-cell>
        </van-cell-group>
      </van-list>
    </van-pull-refresh>
    <div class="total-card">
      <span>合计应收：</span>
      <span class="amount">¥{{ totalAmount }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getReceivables } from '../api'

const list = ref([])
const refreshing = ref(false)

const totalAmount = computed(() => {
  return list.value.reduce((sum, item) => sum + (item.amount || 0), 0).toFixed(2)
})

const loadData = async () => {
  try {
    const res = await getReceivables()
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
.receivables-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 60px;
}
.overdue {
  color: #ee0a24;
}
.total-card {
  position: fixed;
  bottom: 50px;
  left: 0;
  right: 0;
  background: #fff;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
}
.amount {
  font-size: 18px;
  font-weight: bold;
  color: #ee0a24;
}
</style>
