<template>
  <div class="page">
    <van-nav-bar title="渠道管理" left-arrow @click-left="$router.back()">
      <template #right>
        <van-icon name="plus" size="22" @click="startCreate" />
      </template>
    </van-nav-bar>

    <van-search v-model="keyword" placeholder="搜索渠道名称/编码" @search="onSearch" style="margin-bottom:8px" />

    <van-pull-refresh v-model="loading" @refresh="loadChannels">
      <van-list :finished="finished" finished-text="没有更多了" @load="loadChannels">
        <div v-for="item in channelList" :key="item.id" class="channel-card" @click="openDetail(item)">
          <div class="channel-header">
            <span class="channel-name">{{ item.name }}</span>
            <van-tag :type="item.status === 1 ? 'success' : 'default'" size="small">
              {{ item.status === 1 ? '启用' : '停用' }}
            </van-tag>
          </div>
          <div class="channel-info">
            <span v-if="item.code">编码: {{ item.code }}</span>
            <span>层级: {{ item.level }}</span>
          </div>
        </div>
        <van-empty v-if="channelList.length === 0 && !loading" description="暂无渠道数据" />
      </van-list>
    </van-pull-refresh>

    <van-popup v-model:show="showForm" position="bottom" round>
      <div style="padding:20px">
        <div style="font-weight:bold;text-align:center;margin-bottom:16px">{{ isEdit ? '编辑渠道' : '新建渠道' }}</div>
        <van-cell-group inset>
          <van-field v-model="form.name" label="渠道名称" placeholder="请输入渠道名称" />
          <van-field v-model="form.code" label="渠道编码" placeholder="请输入渠道编码" />
          <van-field v-model="form.level" label="层级" type="number" placeholder="1/2/3" />
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
import { getChannels, createChannel, updateChannel } from '../api'

const loading = ref(false)
const finished = ref(false)
const channelList = ref([])
const keyword = ref('')
const showForm = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const currentItem = ref(null)

const form = ref({ name: '', code: '', level: 1, sort_order: 0, remark: '', status: 1 })

const loadChannels = async () => {
  loading.value = true
  try {
    const res = await getChannels({ keyword: keyword.value, page_size: 50 })
    channelList.value = res.data || []
  } catch { channelList.value = [] }
  loading.value = false
  finished.value = true
}

const onSearch = () => { loadChannels() }

const startCreate = () => {
  isEdit.value = false
  form.value = { name: '', code: '', level: 1, sort_order: 0, remark: '', status: 1 }
  currentItem.value = null
  showForm.value = true
}

const openDetail = (item) => {
  isEdit.value = true
  currentItem.value = item
  form.value = { name: item.name, code: item.code || '', level: item.level || 1, sort_order: item.sort_order || 0, remark: item.remark || '', status: item.status }
  showForm.value = true
}

const submitForm = async () => {
  if (!form.value.name) return showToast('请输入渠道名称')
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateChannel({ id: currentItem.value.id, ...form.value })
      showSuccessToast('更新成功')
    } else {
      await createChannel(form.value)
      showSuccessToast('创建成功')
    }
    showForm.value = false
    loadChannels()
  } catch { showToast('保存失败') }
  submitting.value = false
}

onMounted(loadChannels)
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.channel-card { background: #fff; margin: 8px 16px; border-radius: 10px; padding: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); cursor: pointer; }
.channel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.channel-name { font-size: 15px; font-weight: bold; color: #333; }
.channel-info { display: flex; gap: 16px; font-size: 13px; color: #666; }
</style>