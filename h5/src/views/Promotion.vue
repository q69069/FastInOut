<template>
  <div class="page">
    <van-nav-bar title="促销管理" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startCreate" />
      </template>
    </van-nav-bar>

    <div class="filter-bar">
      <van-tag v-for="s in statusFilters" :key="s.value" :type="statusFilter === s.value ? 'primary' : 'default'" size="large" @click="statusFilter = s.value; loadPromotions()">{{ s.label }}</van-tag>
    </div>

    <van-pull-refresh v-model="loading" @refresh="loadPromotions">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadPromotions">
        <div v-for="p in promotions" :key="p.id" class="promo-card" @click="openDetail(p)">
          <div class="promo-header">
            <span class="promo-name">{{ p.name }}</span>
            <van-tag :type="getStatusType(p.status)">{{ p.status === 1 ? '活动中' : '已结束' }}</van-tag>
          </div>
          <div class="promo-body">
            <div class="promo-type">
              <van-tag :type="p.promo_type === 'threshold' ? 'warning' : 'primary'" size="small">
                {{ p.promo_type === 'threshold' ? '满减促销' : '折扣促销' }}
              </van-tag>
            </div>
            <div v-if="p.promo_type === 'threshold'" class="promo-rule">
              满{{ p.threshold_amount }}减{{ p.discount_amount }}
            </div>
            <div v-else class="promo-rule">
              {{ (p.discount_value * 10).toFixed(1) }}折
            </div>
            <div class="promo-period">
              {{ p.start_date }} 至 {{ p.end_date }}
            </div>
          </div>
          <div class="promo-footer">
            <span class="promo-products">{{ p.product_names || p.product_name || '全商品' }}</span>
          </div>
        </div>
        <van-empty v-if="promotions.length === 0 && !loading" description="暂无促销方案" />
      </van-list>
    </van-pull-refresh>

    <!-- 新建/编辑 -->
    <van-popup v-model:show="showForm" position="bottom" round style="max-height:85%">
      <div style="padding:16px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">{{ isEdit ? '编辑促销' : '新建促销' }}</div>
        <van-cell-group inset>
          <van-field v-model="form.name" label="活动名称" placeholder="请输入活动名称" />
          <van-cell title="促销类型">
            <template #extra>
              <van-radio-group v-model="form.promo_type" direction="horizontal">
                <van-radio name="threshold">满减</van-radio>
                <van-radio name="discount">折扣</van-radio>
              </van-radio-group>
            </template>
          </van-cell>
          <van-field v-if="form.promo_type === 'threshold'" v-model="form.threshold_amount" label="门槛金额" type="number" placeholder="满多少" />
          <van-field v-if="form.promo_type === 'threshold'" v-model="form.discount_amount" label="优惠金额" type="number" placeholder="减多少" />
          <van-field v-if="form.promo_type === 'discount'" v-model="form.discount_value" label="折扣比例" type="number" placeholder="如 0.85 表示八五折" />
          <van-cell title="开始日期" is-link :value="form.start_date || '请选择'" @click="showStartPicker = true" />
          <van-cell title="结束日期" is-link :value="form.end_date || '请选择'" @click="showEndPicker = true" />
          <van-field v-model="form.product_name" label="适用商品" placeholder="留空表示全部商品" />
          <van-field v-model="form.remark" label="备注" placeholder="备注" />
        </van-cell-group>
        <div style="display:flex;gap:12px;margin-top:16px">
          <van-button block @click="showForm = false">取消</van-button>
          <van-button type="danger" block :loading="submitting" @click="submitPromo">保存</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 详情 -->
    <van-popup v-model:show="showDetail" position="bottom" round style="max-height:60%">
      <div style="padding:16px" v-if="detailItem">
        <h3>{{ detailItem.name }}</h3>
        <van-cell-group style="margin-top:12px">
          <van-cell title="类型" :value="detailItem.promo_type === 'threshold' ? '满减促销' : '折扣促销'" />
          <van-cell v-if="detailItem.promo_type === 'threshold'" title="门槛" :value="'满' + detailItem.threshold_amount" />
          <van-cell v-if="detailItem.promo_type === 'threshold'" title="优惠" :value="'减' + detailItem.discount_amount" />
          <van-cell v-if="detailItem.promo_type === 'discount'" title="折扣" :value="(detailItem.discount_value * 10).toFixed(1) + '折'" />
          <van-cell title="开始日期" :value="detailItem.start_date" />
          <van-cell title="结束日期" :value="detailItem.end_date" />
          <van-cell title="状态">
            <template #value><van-tag :type="getStatusType(detailItem.status)">{{ detailItem.status === 1 ? '活动中' : '已结束' }}</van-tag></template>
          </van-cell>
          <van-cell title="适用商品" :value="detailItem.product_name || '全商品'" />
          <van-cell title="备注" :value="detailItem.remark || '-'" />
        </van-cell-group>
        <div style="display:flex;gap:8px;margin-top:16px">
          <van-button type="primary" size="small" @click="handleEdit(detailItem)">编辑</van-button>
          <van-button type="danger" plain size="small" @click="handleDelete(detailItem)">删除</van-button>
          <van-button block @click="showDetail = false">关闭</van-button>
        </div>
      </div>
    </van-popup>

    <!-- Date Pickers -->
    <van-popup v-model:show="showStartPicker" position="bottom" round>
      <van-date-picker @confirm="onStartConfirm" @cancel="showStartPicker = false" />
    </van-popup>
    <van-popup v-model:show="showEndPicker" position="bottom" round>
      <van-date-picker @confirm="onEndConfirm" @cancel="showEndPicker = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getPromotions, createPromotion, updatePromotion, deletePromotion } from '../api'

const loading = ref(false)
const finished = ref(false)
const promotions = ref([])
const showForm = ref(false)
const showDetail = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const detailItem = ref(null)
const statusFilter = ref(null)
const showStartPicker = ref(false)
const showEndPicker = ref(false)

const statusFilters = [
  { label: '全部', value: null },
  { label: '进行中', value: 1 },
  { label: '已结束', value: 0 }
]

const form = ref({
  name: '', promo_type: 'threshold', threshold_amount: '', discount_amount: '',
  discount_value: '', start_date: '', end_date: '', product_name: '', remark: ''
})

const getStatusType = (s) => s === 1 ? 'success' : 'default'

const loadPromotions = async () => {
  loading.value = true
  try {
    const res = await getPromotions({ status: statusFilter.value, page_size: 50 })
    promotions.value = res.data || []
  } catch {}
  loading.value = false
  finished.value = true
}

const startCreate = () => {
  isEdit.value = false
  form.value = { name: '', promo_type: 'threshold', threshold_amount: '', discount_amount: '', discount_value: '', start_date: '', end_date: '', product_name: '', remark: '' }
  showForm.value = true
}

const handleEdit = (item) => {
  isEdit.value = true
  detailItem.value = item
  form.value = {
    name: item.name, promo_type: item.promo_type,
    threshold_amount: item.threshold_amount || '', discount_amount: item.discount_amount || '',
    discount_value: item.discount_value || '', start_date: item.start_date || '', end_date: item.end_date || '',
    product_name: item.product_name || '', remark: item.remark || ''
  }
  showDetail.value = false
  showForm.value = true
}

const submitPromo = async () => {
  if (!form.value.name) return showToast('请输入活动名称')
  if (!form.value.start_date) return showToast('请选择开始日期')
  if (!form.value.end_date) return showToast('请选择结束日期')
  submitting.value = true
  try {
    const payload = { ...form.value }
    if (payload.promo_type === 'threshold') {
      payload.threshold_amount = parseFloat(payload.threshold_amount)
      payload.discount_amount = parseFloat(payload.discount_amount)
    } else {
      payload.discount_value = parseFloat(payload.discount_value)
    }
    if (isEdit.value) {
      await updatePromotion(detailItem.value.id, payload)
      showSuccessToast('更新成功')
    } else {
      await createPromotion(payload)
      showSuccessToast('创建成功')
    }
    showForm.value = false
    loadPromotions()
  } catch { showToast('保存失败') }
  submitting.value = false
}

const openDetail = (item) => {
  detailItem.value = item
  showDetail.value = true
}

const handleDelete = async (item) => {
  try {
    await showConfirmDialog({ title: '删除', message: `确认删除促销方案 ${item.name}？` })
    await deletePromotion(item.id)
    showSuccessToast('已删除')
    showDetail.value = false
    loadPromotions()
  } catch {}
}

const onStartConfirm = ({ selectedValues }) => {
  form.value.start_date = selectedValues.join('-')
  showStartPicker.value = false
}
const onEndConfirm = ({ selectedValues }) => {
  form.value.end_date = selectedValues.join('-')
  showEndPicker.value = false
}

onMounted(loadPromotions)
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.filter-bar { display: flex; gap: 8px; padding: 8px 16px; background: #fff; margin-bottom: 8px; }
.promo-card { background: #fff; margin: 8px 16px; border-radius: 10px; padding: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); cursor: pointer; }
.promo-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.promo-name { font-size: 15px; font-weight: bold; color: #333; }
.promo-body { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.promo-rule { font-size: 18px; font-weight: bold; color: #ee0a24; }
.promo-period { font-size: 12px; color: #999; }
.promo-footer { border-top: 1px solid #f5f5f5; padding-top: 6px; }
.promo-products { font-size: 12px; color: #666; }
</style>