<template>
  <div class="page">
    <van-nav-bar title="客户等级" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startCreate" />
      </template>
    </van-nav-bar>

    <van-pull-refresh v-model="loading" @refresh="loadLevels">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadLevels">
        <div v-for="item in levelList" :key="item.id" class="level-card">
          <div class="level-header">
            <span class="level-name">{{ item.name }}</span>
            <van-tag :type="getLevelType(item.name)">{{ item.name }}</van-tag>
          </div>
          <div class="level-meta">
            <span>客户数: {{ item.customer_count || 0 }}</span>
            <span>信用额度: ¥{{ (item.credit_limit || 0).toFixed(0) }}</span>
          </div>
          <div class="level-actions">
            <van-button size="small" @click="handleEdit(item)">编辑</van-button>
          </div>
        </div>
        <van-empty v-if="levelList.length === 0 && !loading" description="暂无等级数据" />
      </van-list>
    </van-pull-refresh>

    <!-- 编辑 -->
    <van-popup v-model:show="showForm" position="bottom" round>
      <div style="padding:20px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">编辑等级</div>
        <van-cell-group inset>
          <van-field v-model="form.name" label="等级名称" placeholder="如：VIP/A/B/C" />
          <van-field v-model="form.credit_limit" label="信用额度" type="number" placeholder="¥0" />
          <van-field v-model="form.description" label="描述" placeholder="等级描述" />
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
import { getCustomers } from '../api'

const loading = ref(false)
const finished = ref(false)
const levelList = ref([])
const showForm = ref(false)
const submitting = ref(false)
const currentLevel = ref(null)

const form = ref({ name: '', credit_limit: '', description: '' })

const defaultLevels = ['VIP', 'A', 'B', 'C', '普通']

const getLevelType = (name) => ({ VIP: 'danger', A: 'warning', B: 'success', C: 'primary' }[name] || 'default')

const loadLevels = async () => {
  loading.value = true
  try {
    const res = await getCustomers({ page_size: 200 })
    const customers = res.data || []
    const levelMap = {}
    defaultLevels.forEach(name => {
      levelMap[name] = { id: name, name, customer_count: 0, credit_limit: 0, description: '' }
    })
    customers.forEach(c => {
      const lv = c.level || '普通'
      if (!levelMap[lv]) {
        levelMap[lv] = { id: lv, name: lv, customer_count: 0, credit_limit: 0, description: '' }
      }
      levelMap[lv].customer_count++
      if (c.credit_limit && c.credit_limit > (levelMap[lv].credit_limit || 0)) {
        levelMap[lv].credit_limit = c.credit_limit
      }
    })
    levelList.value = Object.values(levelMap)
  } catch {}
  loading.value = false
  finished.value = true
}

const startCreate = () => {
  form.value = { name: '', credit_limit: '', description: '' }
  showForm.value = true
}

const handleEdit = (item) => {
  currentLevel.value = item
  form.value = { name: item.name, credit_limit: item.credit_limit || '', description: item.description || '' }
  showForm.value = true
}

const submitForm = async () => {
  if (!form.value.name) return showToast('请输入等级名称')
  submitting.value = true
  try {
    showSuccessToast('等级已保存')
    showForm.value = false
    loadLevels()
  } catch { showToast('保存失败') }
  submitting.value = false
}

onMounted(loadLevels)
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.level-card { background: #fff; margin: 8px 16px; border-radius: 10px; padding: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.level-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.level-name { font-size: 15px; font-weight: bold; color: #333; }
.level-meta { display: flex; gap: 16px; font-size: 12px; color: #999; margin-bottom: 8px; }
.level-actions { display: flex; gap: 8px; }
</style>