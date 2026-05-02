<template>
  <div class="supplier-page">
    <van-nav-bar title="供应商管理" />
    <van-search v-model="keyword" placeholder="搜索供应商名称/电话" @search="loadData" />

    <!-- 供应商列表 -->
    <van-pull-refresh v-model="loading" @refresh="loadData">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadData">
        <div v-for="item in list" :key="item.id" class="supplier-card">
          <div class="supplier-header">
            <div class="supplier-name">{{ item.name }}</div>
            <van-tag :type="item.status === 1 ? 'success' : 'default'" size="small">
              {{ item.status === 1 ? '合作中' : '已停止' }}
            </van-tag>
          </div>
          <div class="supplier-info">
            <div class="info-item">
              <van-icon name="phone-o" />
              <span>{{ item.phone || '无' }}</span>
            </div>
            <div class="info-item">
              <van-icon name="location-o" />
              <span>{{ item.address || '无' }}</span>
            </div>
          </div>
          <div class="supplier-balance">
            <div class="balance-item">
              <span class="balance-label">应付余额</span>
              <span class="balance-value red">¥{{ item.payable_balance || 0 }}</span>
            </div>
          </div>
          <div class="supplier-actions">
            <van-button size="small" @click="handleDetail(item)">详情</van-button>
            <van-button size="small" type="primary" @click="handleOrder(item)">采购</van-button>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSuppliers } from '../api'

const router = useRouter()
const list = ref([])
const loading = ref(false)
const finished = ref(false)
const keyword = ref('')

const handleDetail = (item) => {
  console.log('查看供应商', item)
}

const handleOrder = (item) => {
  router.push(`/purchase?supplier_id=${item.id}`)
}

const loadData = async () => {
  try {
    const res = await getSuppliers({ keyword: keyword.value })
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
.supplier-page { background: #f7f8fa; min-height: 100vh; }
.supplier-card { background: #fff; margin: 12px; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.supplier-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.supplier-name { font-size: 16px; font-weight: bold; color: #333; }
.supplier-info { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.info-item { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #666; }
.supplier-balance { padding: 10px 0; border-top: 1px solid #f5f5f5; border-bottom: 1px solid #f5f5f5; margin-bottom: 12px; }
.balance-item { display: flex; flex-direction: column; gap: 2px; }
.balance-label { font-size: 11px; color: #999; }
.balance-value { font-size: 15px; font-weight: bold; color: #333; }
.balance-value.red { color: #ee0a24; }
.supplier-actions { display: flex; gap: 8px; }
</style>