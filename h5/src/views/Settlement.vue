<template>
  <div class="page">
    <van-nav-bar title="交账管理" left-arrow @click-left="$router.back()" />

    <!-- 交账单列表 -->
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="待交账">
        <van-cell-group inset style="margin:12px 0" v-if="pendingDeliveries.length > 0">
          <van-cell v-for="d in pendingDeliveries" :key="d.id"
            :title="d.delivery_no"
            :label="d.customer_name + ' | ' + d.created_at?.substring(0, 16)"
            :value="'¥' + (d.total_amount || 0).toFixed(2)">
            <template #right-icon>
              <van-checkbox v-model="d.selected" />
            </template>
          </van-cell>
        </van-cell-group>
        <van-empty v-else description="暂无待交账单据" />

        <div v-if="pendingDeliveries.length > 0" style="padding:12px 16px">
          <van-cell title="已选单据" :value="selectedCount + ' 单'" />
          <van-cell title="合计金额" :value="'¥' + selectedTotal.toFixed(2)" />
          <van-cell title="现金合计" :value="'¥' + selectedCash.toFixed(2)" />
          <van-cell title="微信合计" :value="'¥' + selectedWechat.toFixed(2)" />
          <van-cell title="支付宝合计" :value="'¥' + selectedAlipay.toFixed(2)" />
          <van-cell title="赊账合计" :value="'¥' + selectedCredit.toFixed(2)" />
          <van-button type="primary" block size="large" :loading="submitting" :disabled="selectedCount === 0" @click="handleSubmit" style="margin-top:12px">
            提交交账 ({{ selectedCount }} 单)
          </van-button>
        </div>
      </van-tab>

      <van-tab title="交账记录">
        <van-pull-refresh v-model="refreshing" @refresh="loadSettlements">
          <van-list v-model:loading="loading" :finished="finished" finished-text="没有更多了" @load="loadSettlements">
            <van-cell-group v-for="s in settlements" :key="s.id" style="margin:8px 12px">
              <van-cell :title="s.settlement_no" :value="'¥' + (s.total_amount || 0).toFixed(2)">
                <template #label>
                  <van-tag :type="settleStatusType(s.status)">{{ s.status_text || s.status }}</van-tag>
                </template>
              </van-cell>
              <van-cell title="现金" :value="'¥' + (s.cash_amount || 0).toFixed(2)" />
              <van-cell title="电子收款" :value="'¥' + ((s.wechat_amount || 0) + (s.alipay_amount || 0)).toFixed(2)" />
              <van-cell title="赊账" :value="'¥' + (s.credit_amount || 0).toFixed(2)" />
              <van-cell title="提交时间" :value="s.created_at" />
              <van-button v-if="s.status === 'pending'" size="small" type="warning" style="margin:8px 16px" @click="handleCancelSettlement(s)">撤回</van-button>
            </van-cell-group>
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getPendingDeliveries, createSettlement, getSettlements } from '../api'

const activeTab = ref(0)
const submitting = ref(false)
const refreshing = ref(false)
const loading = ref(false)
const finished = ref(false)

const pendingDeliveries = ref([])
const settlements = ref([])
const settlePage = ref(1)

const selectedCount = computed(() => pendingDeliveries.value.filter(d => d.selected).length)
const selectedTotal = computed(() => pendingDeliveries.value.filter(d => d.selected).reduce((s, d) => s + (d.total_amount || 0), 0))
const selectedCash = computed(() => pendingDeliveries.value.filter(d => d.selected).reduce((s, d) => s + (d.cash_amount || 0), 0))
const selectedWechat = computed(() => pendingDeliveries.value.filter(d => d.selected).reduce((s, d) => s + (d.wechat_amount || 0), 0))
const selectedAlipay = computed(() => pendingDeliveries.value.filter(d => d.selected).reduce((s, d) => s + (d.alipay_amount || 0), 0))
const selectedCredit = computed(() => pendingDeliveries.value.filter(d => d.selected).reduce((s, d) => s + (d.credit_amount || 0), 0))

const settleStatusType = (status) => {
  const map = { pending: 'warning', audited: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const loadPending = async () => {
  try {
    const res = await getPendingDeliveries({ page_size: 200 })
    pendingDeliveries.value = (res.data || []).map(d => ({ ...d, selected: false }))
  } catch {}
}

const loadSettlements = async () => {
  try {
    const res = await getSettlements({ page: settlePage.value, page_size: 20 })
    if (settlePage.value === 1) settlements.value = res.data || []
    else settlements.value.push(...(res.data || []))
    finished.value = (res.data || []).length < 20
    settlePage.value++
  } catch { finished.value = true }
  loading.value = false
  refreshing.value = false
}

const handleSubmit = async () => {
  const selected = pendingDeliveries.value.filter(d => d.selected)
  if (!selected.length) return showToast('请选择要交账的单据')

  try {
    await showConfirmDialog({ title: '提交交账', message: `确认提交 ${selected.length} 笔单据交账？` })
  } catch { return }

  submitting.value = true
  try {
    await createSettlement({
      delivery_ids: selected.map(d => d.id),
      total_amount: selectedTotal.value,
      cash_amount: selectedCash.value,
      wechat_amount: selectedWechat.value,
      alipay_amount: selectedAlipay.value,
      credit_amount: selectedCredit.value
    })
    showSuccessToast('交账提交成功')
    await loadPending()
    settlePage.value = 1
    await loadSettlements()
    activeTab.value = 1
  } catch { showToast('提交失败') }
  submitting.value = false
}

const handleCancelSettlement = async (s) => {
  // 交账撤回（如果后端支持）
  showToast('暂不支持撤回')
}

onMounted(() => { loadPending() })
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; }
</style>
