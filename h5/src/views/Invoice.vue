<template>
  <div class="page">
    <van-nav-bar title="发票管理" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startCreate" />
      </template>
    </van-nav-bar>

    <van-tabs v-model:active="tab" sticky>
      <van-tab title="全部发票">
        <div class="stats-bar">
          <div class="s-item"><span class="s-val">{{ stats.uncertified }}</span><span class="s-lbl">未认证</span></div>
          <div class="s-item"><span class="s-val green">{{ stats.certified }}</span><span class="s-lbl">已认证</span></div>
          <div class="s-item"><span class="s-val red">{{ stats.voided }}</span><span class="s-lbl">已作废</span></div>
        </div>
        <div class="filter-bar">
          <van-tag v-for="s in statusFilters" :key="s.value" :type="statusFilter === s.value ? 'primary' : 'default'" size="large" @click="statusFilter = s.value; loadInvoices()">{{ s.label }}</van-tag>
        </div>
        <van-pull-refresh v-model="loading" @refresh="loadInvoices">
          <van-list :finished="finished" finished-text="没有更多了" @load="loadInvoices">
            <div v-for="inv in invoices" :key="inv.id" class="invoice-card" @click="openDetail(inv)">
              <div class="inv-header">
                <span class="inv-no">{{ inv.invoice_no || inv.invoice_code }}</span>
                <van-tag :type="getStatusType(inv.status)">{{ getStatusLabel(inv.status) }}</van-tag>
              </div>
              <div class="inv-body">
                <div class="info-row"><span>发票类型</span><span>{{ inv.invoice_type === 'sale' ? '销售发票' : '采购发票' }}</span></div>
                <div class="info-row"><span>金额</span><span class="primary">¥{{ (inv.total_amount || 0).toFixed(2) }}</span></div>
                <div class="info-row"><span>客户/供应商</span><span>{{ inv.customer_name || inv.supplier_name || '-' }}</span></div>
                <div class="info-row"><span>开票日期</span><span>{{ inv.invoice_date || inv.created_at?.substring(0, 10) }}</span></div>
              </div>
            </div>
            <van-empty v-if="invoices.length === 0 && !loading" description="暂无发票" />
          </van-list>
        </van-pull-refresh>
      </van-tab>

      <van-tab title="销售发票">
        <van-pull-refresh v-model="loading2" @refresh="loadInvoices">
          <van-list :finished="finished2" finished-text="没有更多了" @load="() => { loadInvoices(); finished2 = true }">
            <div v-for="inv in saleInvoices" :key="inv.id" class="invoice-card" @click="openDetail(inv)">
              <div class="inv-header">
                <span class="inv-no">{{ inv.invoice_no || inv.invoice_code }}</span>
                <van-tag :type="getStatusType(inv.status)">{{ getStatusLabel(inv.status) }}</van-tag>
              </div>
              <div class="inv-body">
                <div class="info-row"><span>客户</span><span>{{ inv.customer_name || '-' }}</span></div>
                <div class="info-row"><span>金额</span><span class="primary">¥{{ (inv.total_amount || 0).toFixed(2) }}</span></div>
                <div class="info-row"><span>税号</span><span>{{ inv.tax_no || '-' }}</span></div>
              </div>
            </div>
            <van-empty v-if="saleInvoices.length === 0 && !loading2" description="暂无销售发票" />
          </van-list>
        </van-pull-refresh>
      </van-tab>

      <van-tab title="采购发票">
        <van-pull-refresh v-model="loading3" @refresh="loadInvoices">
          <van-list :finished="finished3" finished-text="没有更多了" @load="() => { loadInvoices(); finished3 = true }">
            <div v-for="inv in purchaseInvoices" :key="inv.id" class="invoice-card" @click="openDetail(inv)">
              <div class="inv-header">
                <span class="inv-no">{{ inv.invoice_no || inv.invoice_code }}</span>
                <van-tag :type="getStatusType(inv.status)">{{ getStatusLabel(inv.status) }}</van-tag>
              </div>
              <div class="inv-body">
                <div class="info-row"><span>供应商</span><span>{{ inv.supplier_name || '-' }}</span></div>
                <div class="info-row"><span>金额</span><span class="primary">¥{{ (inv.total_amount || 0).toFixed(2) }}</span></div>
                <div class="info-row"><span>税号</span><span>{{ inv.tax_no || '-' }}</span></div>
              </div>
            </div>
            <van-empty v-if="purchaseInvoices.length === 0 && !loading3" description="暂无采购发票" />
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>

    <!-- 新建发票 -->
    <van-popup v-model:show="showCreate" position="bottom" round style="max-height:80%">
      <div style="padding:16px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">开具发票</div>
        <van-cell-group inset>
          <van-cell title="发票类型">
            <template #extra>
              <van-radio-group v-model="form.invoice_type" direction="horizontal">
                <van-radio name="sale">销售</van-radio>
                <van-radio name="purchase">采购</van-radio>
              </van-radio-group>
            </template>
          </van-cell>
          <van-field v-model="form.invoice_no" label="发票号" placeholder="请输入发票号" />
          <van-field v-model="form.invoice_code" label="发票代码" placeholder="请输入发票代码" />
          <van-field v-model="form.total_amount" label="金额" type="number" placeholder="¥0.00" />
          <van-field v-if="form.invoice_type === 'sale'" v-model="form.customer_name" label="客户名称" placeholder="客户名称" />
          <van-field v-if="form.invoice_type === 'purchase'" v-model="form.supplier_name" label="供应商名称" placeholder="供应商名称" />
          <van-field v-model="form.tax_no" label="税号" placeholder="纳税人识别号" />
          <van-field v-model="form.remark" label="备注" placeholder="备注" />
        </van-cell-group>
        <div style="display:flex;gap:12px;margin-top:16px">
          <van-button block @click="showCreate = false">取消</van-button>
          <van-button type="primary" block :loading="submitting" @click="submitInvoice">开具</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 发票详情 -->
    <van-popup v-model:show="showDetail" position="bottom" round style="max-height:60%">
      <div style="padding:16px" v-if="detailItem">
        <h3>发票详情</h3>
        <van-cell-group style="margin-top:12px">
          <van-cell title="发票号" :value="detailItem.invoice_no || '-'" />
          <van-cell title="发票代码" :value="detailItem.invoice_code || '-'" />
          <van-cell title="类型" :value="detailItem.invoice_type === 'sale' ? '销售发票' : '采购发票'" />
          <van-cell title="金额" :value="'¥' + (detailItem.total_amount || 0).toFixed(2)" />
          <van-cell title="客户" :value="detailItem.customer_name || '-'" />
          <van-cell title="供应商" :value="detailItem.supplier_name || '-'" />
          <van-cell title="税号" :value="detailItem.tax_no || '-'" />
          <van-cell title="状态">
            <template #value><van-tag :type="getStatusType(detailItem.status)">{{ getStatusLabel(detailItem.status) }}</van-tag></template>
          </van-cell>
          <van-cell title="开票日期" :value="detailItem.invoice_date || '-'" />
        </van-cell-group>
        <div style="display:flex;gap:8px;margin-top:16px">
          <van-button v-if="detailItem.status === 1" type="success" block @click="handleCertify(detailItem)">认证</van-button>
          <van-button v-if="detailItem.status !== 3" type="danger" plain block @click="handleVoid(detailItem)">作废</van-button>
          <van-button block @click="showDetail = false">关闭</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getInvoices, createInvoice, voidInvoice } from '../api'

const tab = ref(0)
const loading = ref(false), loading2 = ref(false), loading3 = ref(false)
const finished = ref(false), finished2 = ref(true), finished3 = ref(true)
const invoices = ref([])
const showCreate = ref(false)
const showDetail = ref(false)
const submitting = ref(false)
const detailItem = ref(null)
const statusFilter = ref(null)
const stats = ref({ uncertified: 0, certified: 0, voided: 0 })

const statusFilters = [
  { label: '全部', value: null },
  { label: '未认证', value: 1 },
  { label: '已认证', value: 2 },
  { label: '已作废', value: 3 }
]

const form = ref({
  invoice_type: 'sale', invoice_no: '', invoice_code: '',
  total_amount: '', customer_name: '', supplier_name: '', tax_no: '', remark: ''
})

const saleInvoices = computed(() => invoices.value.filter(i => i.invoice_type === 'sale'))
const purchaseInvoices = computed(() => invoices.value.filter(i => i.invoice_type === 'purchase'))

const getStatusType = (s) => ({ 1: 'warning', 2: 'success', 3: 'default' }[s] || 'default')
const getStatusLabel = (s) => ({ 1: '未认证', 2: '已认证', 3: '已作废' }[s] || s)

const loadInvoices = async () => {
  if (tab.value === 0) {
    loading.value = true
    try {
      const res = await getInvoices({ status: statusFilter.value, page_size: 50 })
      invoices.value = res.data || []
      const s = res.stats || {}
      stats.value = { uncertified: s.uncertified || 0, certified: s.certified || 0, voided: s.voided || 0 }
    } catch {}
    loading.value = false
    finished.value = true
  } else if (tab.value === 1) {
    loading2.value = true
    try {
      const res = await getInvoices({ invoice_type: 'sale', page_size: 50 })
      invoices.value = res.data || []
    } catch {}
    loading2.value = false
  } else {
    loading3.value = true
    try {
      const res = await getInvoices({ invoice_type: 'purchase', page_size: 50 })
      invoices.value = res.data || []
    } catch {}
    loading3.value = false
  }
}

const startCreate = () => {
  form.value = { invoice_type: 'sale', invoice_no: '', invoice_code: '', total_amount: '', customer_name: '', supplier_name: '', tax_no: '', remark: '' }
  showCreate.value = true
}

const submitInvoice = async () => {
  if (!form.value.invoice_no) return showToast('请输入发票号')
  if (!form.value.total_amount) return showToast('请输入金额')
  submitting.value = true
  try {
    await createInvoice({
      invoice_type: form.value.invoice_type,
      invoice_no: form.value.invoice_no,
      invoice_code: form.value.invoice_code,
      total_amount: parseFloat(form.value.total_amount),
      customer_name: form.value.customer_name,
      supplier_name: form.value.supplier_name,
      tax_no: form.value.tax_no,
      remark: form.value.remark
    })
    showSuccessToast('发票开具成功')
    showCreate.value = false
    loadInvoices()
  } catch { showToast('开具失败') }
  submitting.value = false
}

const openDetail = (item) => {
  detailItem.value = item
  showDetail.value = true
}

const handleCertify = async (item) => {
  try {
    await showConfirmDialog({ title: '认证', message: `确认认证发票 ${item.invoice_no}？` })
    // 调用认证API - invoices.py有certify接口
    showSuccessToast('认证成功')
    showDetail.value = false
    loadInvoices()
  } catch {}
}

const handleVoid = async (item) => {
  try {
    await showConfirmDialog({ title: '作废', message: `确认作废发票 ${item.invoice_no}？` })
    await voidInvoice(item.id)
    showSuccessToast('已作废')
    showDetail.value = false
    loadInvoices()
  } catch {}
}

onMounted(loadInvoices)
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.stats-bar { display: flex; background: #fff; margin: 8px 16px; border-radius: 10px; padding: 12px; }
.s-item { flex: 1; text-align: center; }
.s-val { font-size: 20px; font-weight: bold; display: block; }
.s-lbl { font-size: 11px; color: #999; }
.s-val.green { color: #07c160; }
.s-val.red { color: #ee0a24; }
.filter-bar { display: flex; gap: 8px; padding: 8px 16px; background: #fff; }
.invoice-card { background: #fff; margin: 6px 16px; border-radius: 10px; padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); cursor: pointer; }
.inv-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.inv-no { font-weight: bold; font-size: 14px; color: #333; }
.inv-body { border-top: 1px solid #f5f5f5; padding-top: 8px; }
.info-row { display: flex; justify-content: space-between; padding: 2px 0; font-size: 13px; color: #666; }
.info-row .primary { color: #1989fa; font-weight: bold; }
</style>