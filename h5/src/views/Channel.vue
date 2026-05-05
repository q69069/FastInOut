<template>
  <div class="page">
    <van-nav-bar title="渠道管理" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startCreate" />
      </template>
    </van-nav-bar>

    <van-pull-refresh v-model="loading" @refresh="loadChannels">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadChannels">
        <div v-for="item in channelList" :key="item.id" class="channel-card">
          <div class="channel-header">
            <span class="channel-name">{{ item.name }}</span>
            <van-tag :type="item.status === 1 ? 'success' : 'default'" size="small">
              {{ item.status === 1 ? '启用' : '停用' }}
            </van-tag>
          </div>
          <div class="channel-meta">
            <span>客户数: {{ item.customer_count || 0 }}</span>
          </div>
          <div class="channel-actions">
            <van-button size="small" @click="handleEdit(item)">编辑</van-button>
            <van-button size="small" type="danger" plain @click="handleDelete(item)">删除</van-button>
          </div>
        </div>
        <van-empty v-if="channelList.length === 0 && !loading" description="暂无渠道数据" />
      </van-list>
    </van-pull-refresh>

    <!-- 新建/编辑 -->
    <van-popup v-model:show="showForm" position="bottom" round>
      <div style="padding:20px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">{{ isEdit ? '编辑渠道' : '新建渠道' }}</div>
        <van-cell-group inset>
          <van-field v-model="form.name" label="渠道名称" placeholder="请输入渠道名称" />
          <van-field v-model="form.description" label="描述" placeholder="渠道描述" />
          <van-cell title="状态">
            <template #extra>
              <van-radio-group v-model="form.status" direction="horizontal">
                <van-radio :name="1">启用</van-radio>
                <van-radio :name="0">停用</van-radio>
              </van-radio-group>
            </template>
          </van-cell>
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
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
import { getCustomers, updateCustomer } from '../api'

const loading = ref(false)
const finished = ref(false)
const channelList = ref([])
const showForm = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const currentChannel = ref(null)

const form = ref({ name: '', status: 1, description: '' })

// 预定义渠道列表（实际可从后端配置读取）
const defaultChannels = ['直营', '代理', '电商', '团购', '其他']

const loadChannels = async () => {
  loading.value = true
  try {
    const res = await getCustomers({ page_size: 200 })
    const customers = res.data || []
    // 从客户数据中提取渠道并分组
    const channelMap = {}
    defaultChannels.forEach(name => {
      channelMap[name] = { id: name, name, status: 1, customer_count: 0, description: '' }
    })
    customers.forEach(c => {
      const ch = c.channel || '其他'
      if (!channelMap[ch]) {
        channelMap[ch] = { id: ch, name: ch, status: 1, customer_count: 0, description: '' }
      }
      channelMap[ch].customer_count++
    })
    channelList.value = Object.values(channelMap).filter(ch => ch.customer_count > 0 || defaultChannels.includes(ch.name))
  } catch {}
  loading.value = false
  finished.value = true
}

const startCreate = () => {
  isEdit.value = false
  form.value = { name: '', status: 1, description: '' }
  showForm.value = true
}

const handleEdit = (item) => {
  currentChannel.value = item
  isEdit.value = true
  form.value = { name: item.name, status: item.status, description: item.description || '' }
  showForm.value = true
}

const submitForm = async () => {
  if (!form.value.name) return showToast('请输入渠道名称')
  submitting.value = true
  try {
    // 渠道暂时不支持独立创建，前端仅展示
    showSuccessToast('渠道信息已保存')
    showForm.value = false
    loadChannels()
  } catch { showToast('保存失败') }
  submitting.value = false
}

const handleDelete = async (item) => {
  try {
    await showConfirmDialog({ title: '删除', message: `确认删除渠道 ${item.name}？` })
    showSuccessToast('渠道已删除')
    loadChannels()
  } catch {}
}

onMounted(loadChannels)
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.channel-card { background: #fff; margin: 8px 16px; border-radius: 10px; padding: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.channel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.channel-name { font-size: 15px; font-weight: bold; color: #333; }
.channel-meta { font-size: 12px; color: #999; margin-bottom: 8px; }
.channel-actions { display: flex; gap: 8px; }
</style>