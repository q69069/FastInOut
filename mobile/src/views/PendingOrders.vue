<template>
  <div class="page">
    <van-nav-bar title="待办订单" left-arrow @click-left="$router.back()" fixed placeholder />
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="待处理">
        <van-pull-refresh v-model="refreshing" @refresh="loadOrders">
          <div v-if="orders.length === 0" class="empty">
            <van-empty description="暂无待办订单 🎉" />
          </div>
          <div v-for="o in orders" :key="o.id" class="card" @click="showDetail(o)">
            <div class="card-header">
              <span class="code">{{ o.code }}</span>
              <span :class="['status', o.urgent ? 'urgent' : '']">{{ o.urgent ? '🔴 超时' : '🟡 待处理' }}</span>
            </div>
            <div class="customer">{{ o.customer_name }}</div>
            <div class="summary">{{ o.item_count }}种商品 | 合计 ¥{{ o.total_amount?.toFixed(2) }}</div>
            <div class="actions">
              <van-button size="small" plain type="primary" @click.stop="startHandle(o)">开始处理</van-button>
            </div>
          </div>
        </van-pull-refresh>
      </van-tab>
      <van-tab title="已处理">
        <van-empty description="暂无已处理订单" />
      </van-tab>
    </van-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { showToast } from 'vant'

const activeTab = ref(0)
const refreshing = ref(false)
const orders = ref([])

const loadOrders = async () => {
  try {
    const res = await api.get('/sales-orders', { params: { status: 'pending', page: 1, limit: 50 } })
    orders.value = (res.data.data?.items || [])
  } catch (e) {
    showToast('加载失败')
  } finally {
    refreshing.value = false
  }
}

const showDetail = (o) => { /* 弹出详情 */ }
const startHandle = (o) => {
  // 一键导航到客户位置（调用地图）
  showToast(`导航到: ${o.customer_name}`)
}

onMounted(loadOrders)
</script>

<style scoped>
.page { min-height: 100vh; background: #f7f8fa; }
.card {
  margin: 10px 12px; padding: 14px; background: #fff; border-radius: 10px;
  border-left: 4px solid #ff976a;
}
.card-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.code { font-weight: 600; color: #333; }
.status { font-size: 12px; color: #ff976a; }
.status.urgent { color: #ee0a24; font-weight: 600; }
.customer { font-size: 15px; color: #333; margin-bottom: 4px; }
.summary { font-size: 13px; color: #999; margin-bottom: 8px; }
.actions { display: flex; gap: 8px; justify-content: flex-end; }
.empty { padding-top: 60px; }
</style>
