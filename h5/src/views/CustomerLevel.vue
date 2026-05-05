<template>
  <div class="page">
    <van-nav-bar title="客户等级" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startCreate" />
      </template>
    </van-nav-bar>

    <van-pull-refresh v-model="loading" @refresh="loadLevels">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadLevels">
        <div v-for="item in levelList" :key="item.id" class="level-card" @click="openDetail(item)">
          <div class="level-header">
            <span class="level-name">{{ item.name }}</span>
            <van-tag :type="item.status === 1 ? 'success' : 'default'" size="small">
              {{ item.status === 1 ? '启用' : '停用' }}
            </van-tag>
          </div>
          <div class="level-stats">
            <div class="stat">
              <span class="stat-val red">{{ ((item.discount_rate || 1) * 10).toFixed(1) }}折</span>
              <span class="stat-lbl">折扣率</span>
            </div>
            <div class="stat">
              <span class="stat-val">¥{{ (item.credit_limit || 0).toFixed(0) }}</span>
              <span class="stat-lbl">信用额度</span>
            </div>
            <div class="stat">
              <span class="stat-val">{{ item.sort_order }}</span>
              <span class="stat-lbl">排序</span>
            </div>
          </div>
        </div>
        <van-empty v-if="levelList.length === 0 && !loading" description="暂无客户等级" />
      </van-list>
    </van-pull-refresh>

    <van-popup v-model:show="showForm" position="bottom" round>
      <div style="padding:20px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">{{ isEdit ? '编辑等级' : '新建等级' }}</div>
        <van-cell-group inset>
          <van-field v-model="form.name" label="等级名称" placeholder="如：A级/B级/C级" />
          <van-field v-model="form.code" label="等级编码" placeholder="如：A/B/C" />
          <van-field v-model="form.discount_rate" label="折扣率" type="number" placeholder="0.95=九五折" />
          <van-field v-model="form.credit_limit" label="信用额度" type="number" placeholder="信用额度" />
          <van-field v-model="form.sort_order" label="排序" type="number" placeholder="数字越小越靠前" />
          <van-cell title="状态">
            <template #extra>
              <van-radio-group v-model="form.status" direction="horizontal">
                <van-radio :name="1">启用</van-radio>
                <van-radio :name="0">停用</van-radio>
              </van-radio-group>
            </template>
          </van-cell>
          <van-field v-model="form.remark" label="备注" placeholder="备注" />
        </van-cell-group>
        <div style="display:flex;gap:12px;margin-top:16px">
          <van-button block @click="showForm = false">取消</van-button>
          <van-button type="primary" block :loading="submitting" @click="submitForm">保存</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import { getCustomerLevels, createCustomerLevel, updateCustomerLevel } from '../api'

const loading = ref(false)
const finished = ref(false)
const levelList = ref([])
const showForm = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const currentItem = ref(null)

const form = ref({ name: '', code: '', discount_rate: 1.0, credit_limit: 0, sort_order: 0, remark: '', status: 1 })

const loadLevels = async () => {
  loading.value = true
  try {
    const res = await getCustomerLevels({ page_size: 50 })
    levelList.value = res.data || []
  } catch { levelList.value = [] }
  loading.value = false
  finished.value = true
}

const startCreate = () => {
  isEdit.value = false
  form.value = { name: '', code: '', discount_rate: 1.0, credit_limit: 0, sort_order: 0, remark: '', status: 1 }
  currentItem.value = null
  showForm.value = true
}

const openDetail = (item) => {
  isEdit.value = true
  currentItem.value = item
  form.value = { name: item.name, code: item.code || '', discount_rate: item.discount_rate || 1.0, credit_limit: item.credit_limit || 0, sort_order: item.sort_order || 0, remark: item.remark || '', status: item.status }
  showForm.value = true
}

const submitForm = async () => {
  if (!form.value.name) return showToast('请输入等级名称')
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateCustomerLevel({ id: currentItem.value.id, ...form.value })
      showSuccessToast('更新成功')
    } else {
      await createCustomerLevel(form.value)
      showSuccessToast('创建成功')
    }
    showForm.value = false
    loadLevels()
  } catch { showToast('保存失败') }
  submitting.value = false
}

onMounted(loadLevels)
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.level-card { background: #fff; margin: 8px 16px; border-radius: 10px; padding: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); cursor: pointer; }
.level-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.level-name { font-size: 16px; font-weight: bold; color: #333; }
.level-stats { display: flex; gap: 16px; }
.stat { display: flex; flex-direction: column; align-items: center; }
.stat-val { font-size: 16px; font-weight: bold; }
.stat-val.red { color: #ee0a24; }
.stat-lbl { font-size: 11px; color: #999; margin-top: 2px; }
</style>