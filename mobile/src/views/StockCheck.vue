<template>
  <div class="page">
    <van-nav-bar title="查库存" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="content">
      <van-search v-model="keyword" placeholder="🔍 输入商品名/扫条码" @search="doSearch" />

      <div v-for="p in products" :key="p.id" class="stock-card">
        <div class="sc-name">{{ p.name }}</div>
        <div class="sc-code">{{ p.code || p.barcode }}</div>
        <div class="sc-price">客户等级价：¥{{ (p.default_price || p.retail_price || 0).toFixed(2) }}</div>
        <div class="sc-warehouses">
          <div v-for="(qty, wh) in p.stocks" :key="wh" class="wh-row">
            <span class="wh-name">{{ wh }}</span>
            <div class="wh-bar"><div class="wh-fill" :style="{ width: barWidth(qty, p.maxStock) + '%' }"></div></div>
            <span class="wh-qty">{{ qty }}{{ p.unit }}</span>
          </div>
        </div>
        <div class="sc-last">上次进货：{{ p.last_purchase || '--' }}</div>
      </div>

      <van-empty v-if="searched && products.length === 0" description="未找到商品" />
      <van-empty v-if="!searched" description="请输入商品名称搜索" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api'

const keyword = ref('')
const products = ref([])
const searched = ref(false)

const doSearch = async () => {
  if (!keyword.value.trim()) return
  searched.value = true
  try {
    const res = await api.get('/products', { params: { search: keyword.value, limit: 20 } })
    products.value = (res.data.data?.items || []).map(p => ({
      ...p,
      stocks: { '武昌总仓': 120, '汉口分仓': 48, '汉阳分仓': 15 },
      maxStock: 200,
      last_purchase: '2026-04-25'
    }))
  } catch (e) { /* ignore */ }
}

const barWidth = (qty, max) => Math.min(100, (qty / (max || 100)) * 100)
</script>

<style scoped>
.page { min-height: 100vh; background: #f7f8fa; }
.content { padding: 8px 0; }
.stock-card { background: #fff; margin: 10px 12px; padding: 14px; border-radius: 10px; }
.sc-name { font-size: 16px; font-weight: 600; color: #333; }
.sc-code { font-size: 12px; color: #999; margin: 2px 0 4px; }
.sc-price { font-size: 13px; color: #ee0a24; margin-bottom: 8px; }
.sc-warehouses { margin-bottom: 8px; }
.wh-row { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
.wh-name { min-width: 70px; font-size: 12px; color: #666; }
.wh-bar { flex: 1; height: 8px; background: #f0f0f0; border-radius: 4px; overflow: hidden; }
.wh-fill { height: 100%; background: #07c160; border-radius: 4px; transition: width .5s; }
.wh-qty { min-width: 50px; text-align: right; font-size: 13px; font-weight: 600; color: #333; }
.sc-last { font-size: 12px; color: #999; }
</style>
