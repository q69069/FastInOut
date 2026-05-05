<template>
  <div class="page">
    <van-nav-bar title="供应商管理" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startCreate" />
      </template>
    </van-nav-bar>

    <div v-if="!showCreate && !showDetail">
      <van-search v-model="keyword" placeholder="搜索供应商名称/电话" @search="onSearch" />

      <van-pull-refresh v-model="refreshing" @refresh="loadData">
        <van-list :loading="loading" :finished="finished" finished-text="没有更多了" @load="loadData">
          <div v-for="item in list" :key="item.id" class="supplier-card" @click="openDetail(item)">
            <div class="supplier-header">
              <span class="supplier-name">{{ item.name }}</span>
              <van-tag :type="item.status === 1 ? 'success' : 'default'" size="small">{{ item.status === 1 ? '合作中' : '已停止' }}</van-tag>
            </div>
            <div class="info-item"><van-icon name="phone-o" /><span>{{ item.phone || '无' }}</span></div>
            <div class="info-item"><van-icon name="location-o" /><span>{{ item.address || '无' }}</span></div>
            <div class="balance-row">
              <span>应付余额</span>
              <span class="red">¥{{ (item.payable_balance || 0).toFixed(2) }}</span>
            </div>
          </div>
          <van-empty v-if="list.length === 0 && !loading" description="暂无供应商数据" />
        </van-list>
      </van-pull-refresh>
    </div>

    <!-- 新建供应商 -->
    <div v-else-if="showCreate" style="padding:12px 16px">
      <van-cell-group inset title="供应商信息">
        <van-cell title="名称" required>
          <template #extra><van-field v-model="form.name" placeholder="请输入供应商名称" style="width:180px" /></template>
        </van-cell>
        <van-cell title="联系人">
          <template #extra><van-field v-model="form.contact" placeholder="联系人" style="width:180px" /></template>
        </van-cell>
        <van-cell title="电话">
          <template #extra><van-field v-model="form.phone" type="tel" placeholder="请输入电话" style="width:180px" /></template>
        </van-cell>
        <van-cell title="地址">
          <template #extra><van-field v-model="form.address" placeholder="请输入地址" style="width:200px" /></template>
        </van-cell>
        <van-cell title="备注">
          <template #extra><van-field v-model="form.remark" placeholder="备注" style="width:200px" /></template>
        </van-cell>
      </van-cell-group>

      <div style="display:flex;gap:8px;margin-top:16px">
        <van-button block @click="showCreate = false">取消</van-button>
        <van-button type="primary" block :loading="submitting" @click="handleCreate">保存</van-button>
      </div>
    </div>

    <!-- 供应商详情 + 对账单 -->
    <div v-else-if="showDetail" style="padding:12px 16px">
      <div class="detail-header">
        <h3>{{ detail.name }}</h3>
        <van-tag :type="detail.status === 1 ? 'success' : 'default'">{{ detail.status === 1 ? '合作中' : '已停止' }}</van-tag>
      </div>
      <van-cell-group inset style="margin:8px 0">
        <van-cell title="联系人" :value="detail.contact || '-'" />
        <van-cell title="电话" :value="detail.phone || '-'" />
        <van-cell title="地址" :value="detail.address || '-'" />
        <van-cell title="应付余额" :value="'¥' + (detail.payable_balance || 0).toFixed(2)" />
        <van-cell title="备注" :value="detail.remark || '-'" />
      </van-cell-group>

      <div style="font-weight:bold;margin:8px 0">对账明细</div>
      <van-cell-group v-for="s in statements" :key="s.id" style="margin-bottom:6px">
        <van-cell :title="s.code" :label="s.created_at?.substring(0, 10)">
          <template #value><span :class="s.type === 'in' ? 'green' : 'red'">{{ s.type === 'in' ? '+' : '-' }}¥{{ (s.amount || 0).toFixed(2) }}</span></template>
        </van-cell>
      </van-cell-group>
      <van-empty v-if="statements.length === 0" description="暂无对账数据" />

      <div style="display:flex;gap:8px;margin-top:12px">
        <van-button block @click="showDetail = false">返回</van-button>
        <van-button type="primary" block @click="handleOrder(detail)">立即采购</van-button>
      </div>
    </div>

    <!-- 付款弹窗 -->
    <van-popup v-model:show="showPay" position="bottom" round>
      <div style="padding:20px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">向供应商付款</div>
        <van-cell-group inset>
          <van-cell title="供应商" :value="payItem?.name" />
          <van-cell title="应付余额" :value="'¥' + ((payItem?.payable_balance || 0)).toFixed(2)" class="red" />
          <van-field v-model="payForm.amount" label="付款金额" type="number" placeholder="请输入付款金额" />
          <van-field v-model="payForm.payment_method" label="付款方式" placeholder="如：转账/现金" />
          <van-field v-model="payForm.remark" label="备注" placeholder="备注" />
        </van-cell-group>
        <div style="display:flex;gap:12px;margin-top:16px">
          <van-button block @click="showPay = false">取消</van-button>
          <van-button type="primary" block :loading="submitting" @click="confirmPay">确认付款</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showSuccessToast } from 'vant'
import { getSuppliers, createSupplier, updateSupplier, getSupplierStatement, makePayment } from '../api'

const router = useRouter()
const showCreate = ref(false)
const showDetail = ref(false)
const showPay = ref(false)
const submitting = ref(false)
const list = ref([])
const detail = ref({})
const statements = ref([])
const payItem = ref(null)
const payForm = ref({ amount: '', payment_method: '', remark: '' })
const form = ref({ name: '', contact: '', phone: '', address: '', remark: '' })
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const page = ref(1)
const keyword = ref('')

const loadData = async () => {
  loading.value = true
  try {
    const res = await getSuppliers({ keyword: keyword.value, page: page.value, page_size: 20 })
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
  form.value = { name: '', contact: '', phone: '', address: '', remark: '' }
  showCreate.value = true
}

const handleCreate = async () => {
  if (!form.value.name) return showToast('请输入供应商名称')
  submitting.value = true
  try {
    await createSupplier(form.value)
    showSuccessToast('供应商已创建')
    showCreate.value = false
    page.value = 1; loadData()
  } catch { showToast('创建失败') }
  submitting.value = false
}

const openDetail = async (item) => {
  detail.value = item
  try {
    const res = await getSupplierStatement({ supplier_id: item.id })
    statements.value = res.data || []
  } catch { statements.value = [] }
  showDetail.value = true
}

const handleOrder = (item) => {
  router.push(`/purchase?supplier_id=${item.id}`)
}

const confirmPay = async () => {
  if (!payForm.value.amount) return showToast('请输入付款金额')
  submitting.value = true
  try {
    await makePayment({ supplier_id: payItem.value.id, amount: parseFloat(payForm.value.amount), payment_method: payForm.value.payment_method, remark: payForm.value.remark })
    showSuccessToast('付款成功')
    showPay.value = false
    page.value = 1; loadData()
  } catch { showToast('付款失败') }
  submitting.value = false
}

onMounted(loadData)
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.supplier-card {
  background: #fff; margin: 8px 16px; border-radius: 10px;
  padding: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.supplier-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.supplier-name { font-size: 15px; font-weight: bold; color: #333; }
.info-item { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #666; margin-bottom: 4px; }
.balance-row { display: flex; justify-content: space-between; padding-top: 8px; border-top: 1px solid #f5f5f5; margin-top: 6px; font-size: 13px; }
.red { color: #ee0a24; }
.green { color: #07c160; }
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
</style>
