<template>
  <div class="page">
    <van-nav-bar title="客户管理" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startCreate" />
      </template>
    </van-nav-bar>

    <!-- 客户列表 -->
    <div v-if="!showCreate && !showDetail">
      <van-search v-model="keyword" placeholder="搜索客户名称/电话" @search="onSearch" />

      <van-pull-refresh v-model="refreshing" @refresh="loadData">
        <van-list :loading="loading" :finished="finished" finished-text="没有更多了" @load="loadData">
          <div v-for="item in list" :key="item.id" class="customer-card" @click="openDetail(item)">
            <div class="customer-header">
              <span class="customer-name">{{ item.name }}</span>
              <van-tag :type="getLevelType(item.level)" size="small">{{ item.level || '普通' }}</van-tag>
            </div>
            <div class="customer-info">
              <van-icon name="phone-o" />
              <span>{{ item.phone || '无' }}</span>
            </div>
            <div class="customer-info">
              <van-icon name="location-o" />
              <span>{{ item.address || '无' }}</span>
            </div>
            <div class="customer-balance">
              <div class="balance-item">
                <span class="balance-label">应收</span>
                <span class="balance-value red">¥{{ (item.receivable_balance || 0).toFixed(2) }}</span>
              </div>
              <div class="balance-item">
                <span class="balance-label">信用额度</span>
                <span class="balance-value">¥{{ (item.credit_limit || 0).toFixed(2) }}</span>
              </div>
              <div class="balance-item">
                <span class="balance-label">价格等级</span>
                <span class="balance-value">{{ item.price_level || '-' }}</span>
              </div>
            </div>
          </div>
          <van-empty v-if="list.length === 0 && !loading" description="暂无客户数据" />
        </van-list>
      </van-pull-refresh>
    </div>

    <!-- 新建客户 -->
    <div v-else-if="showCreate" style="padding:12px 16px">
      <van-cell-group inset title="客户信息">
        <van-cell title="客户名称" required>
          <template #extra>
            <van-field v-model="form.name" placeholder="请输入客户名称" style="width:180px" />
          </template>
        </van-cell>
        <van-cell title="联系电话">
          <template #extra>
            <van-field v-model="form.phone" type="tel" placeholder="请输入电话" style="width:180px" />
          </template>
        </van-cell>
        <van-cell title="地址">
          <template #extra>
            <van-field v-model="form.address" placeholder="请输入地址" style="width:200px" />
          </template>
        </van-cell>
        <van-cell title="客户等级" is-link :value="form.level || '请选择'" @click="showLevelPicker = true" />
        <van-cell title="价格等级" is-link :value="form.price_level || '请选择'" @click="showPriceLevelPicker = true" />
        <van-cell title="信用额度">
          <template #extra>
            <van-field v-model.number="form.credit_limit" type="number" placeholder="¥0.00" style="width:120px" />
          </template>
        </van-cell>
        <van-cell title="备注">
          <template #extra>
            <van-field v-model="form.remark" placeholder="备注" style="width:200px" />
          </template>
        </van-cell>
      </van-cell-group>

      <div style="display:flex;gap:8px;margin-top:16px">
        <van-button block @click="showCreate = false">取消</van-button>
        <van-button type="primary" block :loading="submitting" @click="handleCreate">保存客户</van-button>
      </div>
    </div>

    <!-- 客户详情 + 应收明细 -->
    <div v-else-if="showDetail" style="padding:12px 16px">
      <div class="detail-header">
        <h3>{{ detail.name }}</h3>
        <van-tag :type="getLevelType(detail.level)">{{ detail.level || '普通' }}</van-tag>
      </div>

      <van-cell-group inset style="margin:8px 0">
        <van-cell title="电话" :value="detail.phone || '-'" />
        <van-cell title="地址" :value="detail.address || '-'" />
        <van-cell title="信用额度" :value="'¥' + (detail.credit_limit || 0).toFixed(2)" />
        <van-cell title="应收余额" :value="'¥' + (detail.receivable_balance || 0).toFixed(2)" />
        <van-cell title="价格等级" :value="detail.price_level || '-'" />
      </van-cell-group>

      <!-- 应收明细 -->
      <div style="font-weight:bold;margin:8px 0">应收明细</div>
      <van-cell-group v-for="r in receivableDetail" :key="r.id" style="margin-bottom:6px">
        <van-cell :title="r.delivery_no || r.code" :label="r.created_at?.substring(0, 10)">
          <template #value>
            <span class="red">¥{{ (r.amount || 0).toFixed(2) }}</span>
          </template>
        </van-cell>
        <van-cell title="已收" :value="'¥' + (r.received || 0).toFixed(2)" />
      </van-cell-group>

      <div style="display:flex;gap:8px;margin-top:12px">
        <van-button block @click="showDetail = false">返回</van-button>
        <van-button type="primary" block @click="handleOrder(detail)">立即下单</van-button>
        <van-button type="success" block @click="openReceive(detail)">收款</van-button>
      </div>
    </div>

    <!-- 收款弹窗 -->
    <van-popup v-model:show="showReceive" position="bottom" round>
      <div style="padding:20px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">应收收款</div>
        <van-cell-group inset>
          <van-cell title="客户" :value="receiveItem?.name" />
          <van-cell title="应收余额" :value="'¥' + ((receiveItem?.receivable_balance || 0)).toFixed(2)" class="red" />
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

    <!-- 选择器 -->
    <van-popup v-model:show="showLevelPicker" position="bottom" round>
      <van-picker title="客户等级" :columns="levelColumns" @confirm="onLevelConfirm" @cancel="showLevelPicker = false" />
    </van-popup>
    <van-popup v-model:show="showPriceLevelPicker" position="bottom" round>
      <van-picker title="价格等级" :columns="priceLevelColumns" @confirm="onPriceLevelConfirm" @cancel="showPriceLevelPicker = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import { getCustomers, createCustomer, updateCustomer, getReceivableDetail, receivePayment } from '../api'

const router = useRouter()
const showCreate = ref(false)
const showDetail = ref(false)
const showReceive = ref(false)
const submitting = ref(false)
const showLevelPicker = ref(false)
const showPriceLevelPicker = ref(false)

const list = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)
const keyword = ref('')

const detail = ref({})
const receivableDetail = ref([])
const receiveItem = ref(null)
const receiveForm = ref({ amount: '', payment_method: '', remark: '' })

const form = ref({ name: '', phone: '', address: '', level: '', price_level: '', credit_limit: null, remark: '' })

const levelColumns = [
  { text: '普通', value: '普通' },
  { text: 'VIP', value: 'VIP' },
  { text: 'A', value: 'A' },
  { text: 'B', value: 'B' },
  { text: 'C', value: 'C' }
]
const priceLevelColumns = [
  { text: '标准价', value: '标准价' },
  { text: 'A价', value: 'A价' },
  { text: 'B价', value: 'B价' },
  { text: 'C价', value: 'C价' }
]

const getLevelType = (level) => ({ VIP: 'danger', A: 'warning', B: 'success', C: 'primary' }[level] || 'default')

const loadData = async () => {
  loading.value = true
  try {
    const res = await getCustomers({ keyword: keyword.value, page: page.value, page_size: 20 })
    if (page.value === 1) list.value = res.data || []
    else list.value.push(...(res.data || []))
    finished.value = (res.data || []).length < 20
    page.value++
  } catch {}
  loading.value = false
  refreshing.value = false
}

const onSearch = () => {
  page.value = 1; list.value = []; loadData()
}

const startCreate = () => {
  form.value = { name: '', phone: '', address: '', level: '', price_level: '', credit_limit: null, remark: '' }
  showCreate.value = true
}

const onLevelConfirm = ({ selectedOptions }) => {
  form.value.level = selectedOptions[0].value; showLevelPicker.value = false
}
const onPriceLevelConfirm = ({ selectedOptions }) => {
  form.value.price_level = selectedOptions[0].value; showPriceLevelPicker.value = false
}

const handleCreate = async () => {
  if (!form.value.name) return showToast('请输入客户名称')
  submitting.value = true
  try {
    await createCustomer(form.value)
    showSuccessToast('客户已创建')
    showCreate.value = false
    page.value = 1; loadData()
  } catch { showToast('创建失败') }
  submitting.value = false
}

const openDetail = async (item) => {
  try {
    const res = await getReceivableDetail(item.id)
    receivableDetail.value = res.data || []
  } catch { receivableDetail.value = [] }
  detail.value = item
  showDetail.value = true
}

const handleOrder = (customer) => {
  router.push(`/order?customer_id=${customer.id}`)
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
    await receivePayment({ customer_id: receiveItem.value.id, amount: parseFloat(receiveForm.value.amount), payment_method: receiveForm.value.payment_method, remark: receiveForm.value.remark })
    showSuccessToast('收款成功')
    showReceive.value = false
    page.value = 1; loadData()
  } catch { showToast('收款失败') }
  submitting.value = false
}

onMounted(loadData)
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.customer-card {
  background: #fff; margin: 8px 16px; border-radius: 10px;
  padding: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.customer-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.customer-name { font-size: 15px; font-weight: bold; color: #333; }
.customer-info { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #666; margin-bottom: 4px; }
.customer-balance { display: flex; gap: 16px; padding-top: 8px; border-top: 1px solid #f5f5f5; margin-top: 6px; }
.balance-item { display: flex; flex-direction: column; }
.balance-label { font-size: 11px; color: #999; }
.balance-value { font-size: 13px; font-weight: bold; color: #333; }
.red { color: #ee0a24; }
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
</style>
