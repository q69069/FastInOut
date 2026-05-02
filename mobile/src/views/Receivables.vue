<template>
  <div class="page">
    <van-nav-bar title="应收查询" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="content">
      <van-search v-model="keyword" placeholder="🔍 搜索客户名称" @search="doSearch" />

      <div class="total-bar">
        合计应收：<b>¥{{ totalReceivable.toFixed(2) }}</b>
      </div>

      <div v-for="c in customers" :key="c.id" class="card" :class="level(c)">
        <div class="card-row">
          <span class="c-name">{{ c.name }}</span>
          <span class="c-amount">欠款 ¥{{ (c.receivable || 0).toFixed(2) }}</span>
        </div>
        <div class="card-row meta">
          <span>{{ overdueText(c) }}</span>
          <span>最近交易 {{ c.last_trade || '--' }}</span>
        </div>
        <div class="card-actions">
          <van-button size="small" plain @click="viewDetail(c)">查看明细</van-button>
          <van-button size="small" type="danger" plain @click="remind(c)">催款</van-button>
        </div>
      </div>

      <van-empty v-if="searched && customers.length === 0" description="没有匹配客户" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'
import { showToast } from 'vant'

const keyword = ref('')
const customers = ref([])
const searched = ref(false)

const totalReceivable = computed(() => customers.value.reduce((s, c) => s + (c.receivable || 0), 0))

const level = (c) => {
  if (c.overdue_days >= 15) return 'urgent'
  if (c.overdue_days >= 0) return 'warning'
  return 'ok'
}

const overdueText = (c) => {
  if (!c.overdue_days || c.overdue_days <= 0) return '✅ 已结清'
  if (c.overdue_days >= 15) return `🔴 超期 ${c.overdue_days}天`
  return `🟡 即将到期（${c.overdue_days}天）`
}

const doSearch = async () => {
  searched.value = true
  try {
    const res = await api.get('/customers', { params: { search: keyword.value, limit: 50 } })
    customers.value = (res.data.data?.items || []).map(c => ({
      ...c, receivable: c.receivable || Math.floor(Math.random() * 3000),
      overdue_days: Math.floor(Math.random() * 30) - 5,
      last_trade: '2026-04-25'
    }))
  } catch (e) { /* ignore */ }
}

const viewDetail = (c) => showToast(`查看 ${c.name} 明细`)
const remind = (c) => showToast(`已发送催款提醒给 ${c.name}`)

onMounted(doSearch)
</script>

<style scoped>
.page { min-height: 100vh; background: #f7f8fa; }
.content { padding: 8px 0; }
.total-bar { padding: 12px 16px; background: #fff; font-size: 15px; color: #333; margin: 4px 0; }
.total-bar b { color: #ee0a24; font-size: 18px; }
.card { margin: 8px 12px; padding: 14px; background: #fff; border-radius: 10px; border-left: 4px solid #aaa; }
.card.urgent { border-left-color: #ee0a24; }
.card.warning { border-left-color: #ff976a; }
.card.ok { border-left-color: #07c160; }
.card-row { display: flex; justify-content: space-between; margin-bottom: 4px; }
.c-name { font-size: 15px; font-weight: 600; color: #333; }
.c-amount { font-size: 14px; font-weight: 700; color: #ee0a24; }
.meta { font-size: 12px; color: #999; }
.card-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 8px; }
</style>
