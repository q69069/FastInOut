<template>
  <div class="page">
    <van-nav-bar title="消息中心" left-arrow @click-left="$router.back()">
      <template #right>
        <van-badge :content="unreadCount > 0 ? unreadCount : ''" :max="99">
          <van-icon name="bell" size="20" @click="loadMessages" />
        </van-badge>
      </template>
    </van-nav-bar>

    <van-tabs v-model:active="tab" sticky>
      <van-tab title="全部">
        <van-pull-refresh v-model="loading" @refresh="loadMessages">
          <van-list :finished="finished" finished-text="没有更多了" @load="loadMessages">
            <div v-for="msg in messages" :key="msg.id" :class="['msg-card', msg.status === 'unread' ? 'unread' : '']" @click="handleRead(msg)">
              <div class="msg-header">
                <van-tag :type="getTypeTag(msg.type)" size="small">{{ getTypeLabel(msg.type) }}</van-tag>
                <span class="msg-time">{{ msg.created_at?.substring(0, 16) }}</span>
              </div>
              <div class="msg-title">{{ msg.title }}</div>
              <div class="msg-content">{{ msg.content }}</div>
              <div v-if="msg.reference_type" class="msg-ref">关联: {{ msg.reference_type }} #{{ msg.reference_id }}</div>
            </div>
            <van-empty v-if="messages.length === 0 && !loading" description="暂无消息" />
          </van-list>
        </van-pull-refresh>
      </van-tab>
      <van-tab title="未读">
        <van-pull-refresh v-model="loading2" @refresh="loadUnread">
          <van-list :finished="finished2" finished-text="没有更多了" @load="loadUnread">
            <div v-for="msg in unreadMessages" :key="msg.id" class="msg-card unread" @click="handleRead(msg)">
              <div class="msg-header">
                <van-tag type="danger" size="small">未读</van-tag>
                <span class="msg-time">{{ msg.created_at?.substring(0, 16) }}</span>
              </div>
              <div class="msg-title">{{ msg.title }}</div>
              <div class="msg-content">{{ msg.content }}</div>
            </div>
            <van-empty v-if="unreadMessages.length === 0 && !loading2" description="暂无未读消息" />
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>

    <div style="padding:12px 16px">
      <van-button v-if="unreadCount > 0" type="primary" block @click="handleMarkAllRead">全部标记已读</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast, showSuccessToast } from 'vant'
import { getMessages, getUnreadCount, markMessageRead, markAllRead } from '../api'

const tab = ref(0)
const loading = ref(false)
const loading2 = ref(false)
const finished = ref(false)
const finished2 = ref(false)
const messages = ref([])
const unreadMessages = ref([])
const unreadCount = ref(0)

const getTypeLabel = (type) => ({ approval: '审批', alert: '预警', system: '系统', invoice: '发票' }[type] || '通知')
const getTypeTag = (type) => ({ approval: 'warning', alert: 'danger', system: 'primary', invoice: 'success' }[type] || 'default')

const loadMessages = async () => {
  loading.value = true
  try {
    const res = await getMessages()
    messages.value = res.data || []
  } catch {}
  loading.value = false
  finished.value = true
  await loadUnreadCount()
}

const loadUnread = async () => {
  loading2.value = true
  try {
    const res = await getMessages({ status: 'unread' })
    unreadMessages.value = res.data || []
  } catch {}
  loading2.value = false
  finished2.value = true
}

const loadUnreadCount = async () => {
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.count || 0
  } catch {}
}

const handleRead = async (msg) => {
  if (msg.status === 'unread') {
    try {
      await markMessageRead(msg.id)
      msg.status = 'read'
      await loadUnreadCount()
    } catch {}
  }
}

const handleMarkAllRead = async () => {
  try {
    await showConfirmDialog({ title: '全部已读', message: '确认将所有消息标记为已读？' })
    const promises = messages.value.filter(m => m.status === 'unread').map(m => markMessageRead(m.id))
    await Promise.all(promises)
    showSuccessToast('已全部标记已读')
    messages.value.forEach(m => m.status = 'read')
    unreadMessages.value = []
    unreadCount.value = 0
  } catch {
    showToast('操作失败')
  }
}

onMounted(() => {
  loadMessages()
  loadUnreadCount()
})
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.msg-card { background: #fff; margin: 8px 16px; border-radius: 10px; padding: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.msg-card.unread { border-left: 3px solid #1989fa; }
.msg-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.msg-time { font-size: 12px; color: #999; }
.msg-title { font-size: 14px; font-weight: bold; color: #333; margin-bottom: 6px; }
.msg-content { font-size: 13px; color: #666; line-height: 1.5; }
.msg-ref { font-size: 12px; color: #999; margin-top: 6px; padding-top: 6px; border-top: 1px solid #f5f5f5; }
</style>