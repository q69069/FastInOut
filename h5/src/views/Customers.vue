<template>
  <div class="customers-page">
    <van-nav-bar title="客户管理" />
    <van-search v-model="keyword" placeholder="搜索客户名称/电话" @search="loadData" />

    <!-- 客户列表 -->
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadData">
        <div v-for="item in list" :key="item.id" class="customer-card">
          <div class="customer-header">
            <div class="customer-name">{{ item.name }}</div>
            <van-tag :type="getLevelType(item.level)" size="small">{{ item.level || '普通' }}</van-tag>
          </div>
          <div class="customer-info">
            <div class="info-item">
              <van-icon name="phone-o" />
              <span>{{ item.phone || '无' }}</span>
            </div>
            <div class="info-item">
              <van-icon name="location-o" />
              <span>{{ item.address || '无' }}</span>
            </div>
          </div>
          <div class="customer-balance">
            <div class="balance-item">
              <span class="balance-label">应收</span>
              <span class="balance-value red">¥{{ item.receivable_balance || 0 }}</span>
            </div>
            <div class="balance-item">
              <span class="balance-label">信用额度</span>
              <span class="balance-value">¥{{ item.credit_limit || 0 }}</span>
            </div>
          </div>
          <div class="customer-actions">
            <van-button size="small" type="primary" @click="handleOrder(item)">下单</van-button>
            <van-button size="small" @click="handleVisit(item)">拜访</van-button>
            <van-button size="small" @click="handleReceivable(item)">应收</van-button>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCustomers } from '../api'

const router = useRouter()
const list = ref([])
const loading = ref(false)
const finished = ref(false)
const keyword = ref('')

const getLevelType = (level) => {
  if (level === 'VIP') return 'danger'
  if (level === 'A') return 'warning'
  if (level === 'B') return 'success'
  return 'default'
}

const handleOrder = (customer) => {
  router.push(`/order?customer_id=${customer.id}`)
}

const handleVisit = (customer) => {
  router.push(`/visit?customer_id=${customer.id}`)
}

const handleReceivable = (customer) => {
  router.push(`/receivables?customer_id=${customer.id}`)
}

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
.customer-card {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.customer-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.customer-name { font-size: 16px; font-weight: bold; color: #333; }
.customer-info { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.info-item { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #666; }
.customer-balance { display: flex; gap: 20px; padding: 10px 0; border-top: 1px solid #f5f5f5; border-bottom: 1px solid #f5f5f5; margin-bottom: 12px; }
.balance-item { display: flex; flex-direction: column; gap: 2px; }
.balance-label { font-size: 11px; color: #999; }
.balance-value { font-size: 15px; font-weight: bold; color: #333; }
.balance-value.red { color: #ee0a24; }
.customer-actions { display: flex; gap: 8px; }
</style>