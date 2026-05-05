<template>
  <div class="page">
    <van-nav-bar title="财务中心" left-arrow @click-left="$router.back()" />

    <van-tabs v-model:active="tab" sticky>
      <!-- ==================== 应收款 ==================== -->
      <van-tab title="应收款">
        <div class="stats-card receivable">
          <div class="stat-item">
            <span class="stat-val red">¥{{ receivableTotal }}</span>
            <span class="stat-label">应收总额</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <span class="stat-val orange">¥{{ receivableReceived }}</span>
            <span class="stat-label">已收</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <span class="stat-val">¥{{ receivableOutstanding }}</span>
            <span class="stat-label">未收</span>
          </div>
        </div>

        <div class="filter-bar">
          <van-tag v-for="s in recStatusOptions" :key="s.value" :type="recFilter === s.value ? 'primary' : 'default'" @click="recFilter = s.value; loadReceivables()" size="large" class="filter-tag">{{ s.label }}</van-tag>
        </div>

        <van-pull-refresh v-model="recLoading" @refresh="loadReceivables">
          <van-list :finished="recFinished" finished-text="没有更多了" @load="loadReceivables">
            <div v-for="item in filteredReceivables" :key="item.id" class="record-card">
              <div class="card-header">
                <span style="font-weight:bold">{{ item.customer_name }}</span>
                <van-tag :type="getReceivableStatusType(item)">{{ item.status }}</van-tag>
              </div>
              <div class="card-body">
                <div class="info-row"><span>应收金额</span><span class="red">¥{{ (item.amount || 0).toFixed(2) }}</span></div>
                <div class="info-row"><span>已收金额</span><span class="green">¥{{ (item.received || 0).toFixed(2) }}</span></div>
                <div class="info-row"><span>单据日期</span><span>{{ item.date || '-' }}</span></div>
              </div>
              <div style="display:flex;gap:8px;margin-top:8px">
                <van-button v-if="item.status !== '已结清'" type="primary" size="small" block @click="openReceive(item)">收款登记</van-button>
              </div>
            </div>
            <van-empty v-if="filteredReceivables.length === 0 && !recLoading" description="暂无应收数据" />
          </van-list>
        </van-pull-refresh>
      </van-tab>

      <!-- ==================== 应付款 ==================== -->
      <van-tab title="应付款">
        <div class="stats-card payable">
          <div class="stat-item">
            <span class="stat-val red">¥{{ payableTotal }}</span>
            <span class="stat-label">应付总额</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <span class="stat-val green">¥{{ payablePaid }}</span>
            <span class="stat-label">已付</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <span class="stat-val">¥{{ payableOutstanding }}</span>
            <span class="stat-label">未付</span>
          </div>
        </div>

        <van-pull-refresh v-model="payLoading" @refresh="loadPayables">
          <van-list :finished="payFinished" finished-text="没有更多了" @load="loadPayables">
            <div v-for="item in payables" :key="item.id" class="record-card">
              <div class="card-header">
                <span style="font-weight:bold">{{ item.supplier_name }}</span>
                <van-tag :type="getPayableStatusType(item)">{{ item.status }}</van-tag>
              </div>
              <div class="card-body">
                <div class="info-row"><span>应付金额</span><span class="red">¥{{ (item.amount || 0).toFixed(2) }}</span></div>
                <div class="info-row"><span>已付金额</span><span class="green">¥{{ (item.paid || 0).toFixed(2) }}</span></div>
                <div class="info-row"><span>单据日期</span><span>{{ item.date || '-' }}</span></div>
              </div>
              <div style="display:flex;gap:8px;margin-top:8px">
                <van-button v-if="item.status !== '已结清'" type="warning" size="small" block @click="openPay(item)">付款登记</van-button>
              </div>
            </div>
            <van-empty v-if="payables.length === 0 && !payLoading" description="暂无应付数据" />
          </van-list>
        </van-pull-refresh>
      </van-tab>

      <!-- ==================== 费用报销 ==================== -->
      <van-tab title="费用报销">
        <van-button type="danger" block style="margin:8px 16px" @click="startExpense">新建费用单</van-button>
        <van-pull-refresh v-model="expLoading" @refresh="loadExpenses">
          <van-list :finished="expFinished" finished-text="没有更多了" @load="loadExpenses">
            <div v-for="e in expenses" :key="e.id" class="record-card">
              <div class="card-header">
                <span style="font-weight:bold">{{ e.expense_no }}</span>
                <van-tag :type="getExpenseStatusType(e)">{{ e.status_text || e.status }}</van-tag>
              </div>
              <div class="card-body">
                <div class="info-row"><span>费用类型</span><span>{{ e.category_name || '-' }}</span></div>
                <div class="info-row"><span>报销金额</span><span class="red">¥{{ (e.amount || 0).toFixed(2) }}</span></div>
                <div class="info-row"><span>申请人</span><span>{{ e.applicant_name || '-' }}</span></div>
                <div class="info-row"><span>申请时间</span><span>{{ e.created_at?.substring(0, 16) }}</span></div>
              </div>
              <div v-if="e.status === 'pending'" style="display:flex;gap:8px;margin-top:8px">
                <van-button type="success" size="small" @click="approveExpense(e)">通过</van-button>
                <van-button type="danger" size="small" plain @click="rejectExpense(e)">驳回</van-button>
              </div>
            </div>
            <van-empty v-if="expenses.length === 0 && !expLoading" description="暂无费用单" />
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>

    <!-- 收款弹窗 -->
    <van-popup v-model:show="showReceive" position="bottom" round>
      <div style="padding:20px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">收款登记</div>
        <van-cell-group inset>
          <van-cell title="客户" :value="receiveItem?.customer_name" />
          <van-cell title="应收金额" :value="'¥' + (receiveItem?.amount || 0).toFixed(2)" />
          <van-field v-model="receiveForm.amount" label="收款金额" type="number" placeholder="请输入收款金额" />
          <van-field v-model="receiveForm.payment_method" label="收款方式" placeholder="如：现金/转账" />
          <van-field v-model="receiveForm.remark" label="备注" placeholder="备注" />
        </van-cell-group>
        <div style="display:flex;gap:12px;margin-top:16px">
          <van-button block @click="showReceive = false">取消</van-button>
          <van-button type="primary" block :loading="submitting" @click="confirmReceive">确认收款</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 付款弹窗 -->
    <van-popup v-model:show="showPay" position="bottom" round>
      <div style="padding:20px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">付款登记</div>
        <van-cell-group inset>
          <van-cell title="供应商" :value="payItem?.supplier_name" />
          <van-cell title="应付金额" :value="'¥' + (payItem?.amount || 0).toFixed(2)" />
          <van-field v-model="payForm.amount" label="付款金额" type="number" placeholder="请输入付款金额" />
          <van-field v-model="payForm.payment_method" label="付款方式" placeholder="如：现金/转账" />
          <van-field v-model="payForm.remark" label="备注" placeholder="备注" />
        </van-cell-group>
        <div style="display:flex;gap:12px;margin-top:16px">
          <van-button block @click="showPay = false">取消</van-button>
          <van-button type="primary" block :loading="submitting" @click="confirmPay">确认付款</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 新建费用弹窗 -->
    <van-popup v-model:show="showExpenseForm" position="bottom" round style="max-height:80%">
      <div style="padding:16px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">新建费用单</div>
        <van-cell-group inset>
          <van-cell title="费用类型" is-link :value="expenseForm.category_name || '请选择'" @click="showCategoryPicker = true" />
          <van-cell title="报销金额">
            <template #extra>
              <van-field v-model="expenseForm.amount" type="number" placeholder="¥0.00" style="width:120px" />
            </template>
          </van-cell>
          <van-field v-model="expenseForm.description" label="费用说明" placeholder="请输入费用说明" rows="2" type="textarea" />
          <van-field v-model="expenseForm.remark" label="备注" placeholder="备注" />
        </van-cell-group>
        <div style="display:flex;gap:12px;margin-top:16px">
          <van-button block @click="showExpenseForm = false">取消</van-button>
          <van-button type="danger" block :loading="submitting" @click="submitExpense">提交费用</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 费用类型选择 -->
    <van-popup v-model:show="showCategoryPicker" position="bottom" round>
      <van-picker title="费用类型" :columns="categoryColumns" @confirm="onCategoryConfirm" @cancel="showCategoryPicker = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import {
  getReceivables, receivePayment, getPayments, makePayment,
  getExpenses, createExpense, getExpenseCategories
} from '../api'

const tab = ref(0)
const submitting = ref(false)
const showReceive = ref(false)
const showPay = ref(false)
const showExpenseForm = ref(false)
const showCategoryPicker = ref(false)

const receivableTotal = ref('0.00')
const receivableReceived = ref('0.00')
const receivableOutstanding = ref('0.00')
const recFilter = ref('all')
const recStatusOptions = [{ label: '全部', value: 'all' }, { label: '未结清', value: '未结清' }, { label: '部分收款', value: '部分收款' }, { label: '已结清', value: '已结清' }]
const receivables = ref([])
const recLoading = ref(false)
const recFinished = ref(false)

const payableTotal = ref('0.00')
const payablePaid = ref('0.00')
const payableOutstanding = ref('0.00')
const payables = ref([])
const payLoading = ref(false)
const payFinished = ref(false)

const expenses = ref([])
const expenseCategories = ref([])
const expLoading = ref(false)
const expFinished = ref(false)

const receiveItem = ref(null)
const receiveForm = ref({ amount: '', payment_method: '', remark: '' })
const payItem = ref(null)
const payForm = ref({ amount: '', payment_method: '', remark: '' })
const expenseForm = ref({ category_id: null, category_name: '', amount: '', description: '', remark: '' })

const filteredReceivables = computed(() => {
  if (recFilter.value === 'all') return receivables.value
  return receivables.value.filter(i => i.status === recFilter.value)
})

const categoryColumns = computed(() => expenseCategories.value.map(c => ({ text: c.name, value: c.id })))

const getReceivableStatusType = (item) => ({ '已结清': 'success', '部分收款': 'warning', '未结清': 'danger' }[item.status] || 'default')
const getPayableStatusType = (item) => ({ '已结清': 'success', '部分付款': 'warning', '未结清': 'danger' }[item.status] || 'default')
const getExpenseStatusType = (e) => ({ pending: 'warning', approved: 'success', rejected: 'danger' }[e.status] || 'info')

const loadReceivables = async () => {
  recLoading.value = true
  try {
    const res = await getReceivables()
    const data = res.data || {}
    receivables.value = Array.isArray(data) ? data : (data.list || [])
    receivableTotal.value = (data.total || 0).toFixed(2)
    receivableReceived.value = (data.received || 0).toFixed(2)
    receivableOutstanding.value = (data.outstanding || 0).toFixed(2)
  } catch {}
  recLoading.value = false
  recFinished.value = true
}

const loadPayables = async () => {
  payLoading.value = true
  try {
    const res = await getPayments()
    const data = res.data || {}
    payables.value = Array.isArray(data) ? data : (data.list || [])
    payableTotal.value = (data.total || 0).toFixed(2)
    payablePaid.value = (data.paid || 0).toFixed(2)
    payableOutstanding.value = (data.outstanding || 0).toFixed(2)
  } catch {}
  payLoading.value = false
  payFinished.value = true
}

const loadExpenses = async () => {
  expLoading.value = true
  try {
    const res = await getExpenses({ page_size: 100 })
    expenses.value = res.data || []
  } catch {}
  expLoading.value = false
  expFinished.value = true
}

const loadExpenseCategories = async () => {
  try {
    const res = await getExpenseCategories()
    expenseCategories.value = res.data || []
  } catch {}
}

const openReceive = (item) => {
  receiveItem.value = item
  receiveForm.value = { amount: '', payment_method: '', remark: '' }
  showReceive.value = true
}

const confirmReceive = async () => {
  if (!receiveForm.value.amount) return showToast('请输入收款金额')
  submitting.value = true
  try {
    await receivePayment({ receivable_id: receiveItem.value.id, amount: parseFloat(receiveForm.value.amount), payment_method: receiveForm.value.payment_method, remark: receiveForm.value.remark })
    showSuccessToast('收款成功')
    showReceive.value = false
    loadReceivables()
  } catch { showToast('收款失败') }
  submitting.value = false
}

const openPay = (item) => {
  payItem.value = item
  payForm.value = { amount: '', payment_method: '', remark: '' }
  showPay.value = true
}

const confirmPay = async () => {
  if (!payForm.value.amount) return showToast('请输入付款金额')
  submitting.value = true
  try {
    await makePayment({ payable_id: payItem.value.id, amount: parseFloat(payForm.value.amount), payment_method: payForm.value.payment_method, remark: payForm.value.remark })
    showSuccessToast('付款成功')
    showPay.value = false
    loadPayables()
  } catch { showToast('付款失败') }
  submitting.value = false
}

const startExpense = () => {
  expenseForm.value = { category_id: null, category_name: '', amount: '', description: '', remark: '' }
  showExpenseForm.value = true
}

const onCategoryConfirm = ({ selectedOptions }) => {
  expenseForm.value.category_id = selectedOptions[0].value
  expenseForm.value.category_name = selectedOptions[0].text
  showCategoryPicker.value = false
}

const submitExpense = async () => {
  if (!expenseForm.value.category_id) return showToast('请选择费用类型')
  if (!expenseForm.value.amount) return showToast('请输入报销金额')
  submitting.value = true
  try {
    await createExpense({ category_id: expenseForm.value.category_id, amount: parseFloat(expenseForm.value.amount), description: expenseForm.value.description, remark: expenseForm.value.remark })
    showSuccessToast('费用单已提交')
    showExpenseForm.value = false
    expFinished.value = false
    loadExpenses()
  } catch { showToast('提交失败') }
  submitting.value = false
}

const approveExpense = async (e) => {
  try {
    await showConfirmDialog({ title: '审批通过', message: `确认通过费用单 ${e.expense_no}？` })
    await apiApproveExpense(e.id)
    showSuccessToast('已通过')
    loadExpenses()
  } catch {}
}

const rejectExpense = async (e) => {
  try {
    await showConfirmDialog({ title: '驳回', message: `确认驳回费用单 ${e.expense_no}？` })
    await apiRejectExpense(e.id)
    showSuccessToast('已驳回')
    loadExpenses()
  } catch {}
}

onMounted(() => {
  loadReceivables()
  loadPayables()
  loadExpenses()
  loadExpenseCategories()
})
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.stats-card { display: flex; margin: 8px 16px; border-radius: 12px; padding: 16px; color: #fff; }
.receivable { background: linear-gradient(135deg, #ff6b35, #ff9a56); }
.payable { background: linear-gradient(135deg, #07c160, #10b980); }
.stat-item { flex: 1; text-align: center; }
.stat-val { font-size: 20px; font-weight: bold; display: block; }
.stat-label { font-size: 11px; opacity: 0.9; margin-top: 2px; }
.stat-divider { width: 1px; background: rgba(255,255,255,0.3); }
.red { color: #ee0a24; }
.orange { color: #ff9a56; }
.green { color: #07c160; }
.filter-bar { display: flex; gap: 8px; padding: 8px 16px; }
.filter-tag { cursor: pointer; }
.record-card {
  background: #fff; margin: 8px 16px; border-radius: 10px;
  padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.card-body { border-top: 1px solid #f5f5f5; padding-top: 6px; }
.info-row { display: flex; justify-content: space-between; padding: 2px 0; font-size: 13px; color: #666; }
</style>
