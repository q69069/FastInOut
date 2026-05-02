<template>
  <div class="tools-page">
    <van-nav-bar title="常用工具" />

    <!-- 快捷操作 -->
    <div class="tools-grid">
      <div class="tool-item" @click="router.push('/transfer')">
        <div class="tool-icon orange">
          <van-icon name="exchange" size="24" />
        </div>
        <div class="tool-name">调拨单</div>
      </div>
      <div class="tool-item" @click="router.push('/check')">
        <div class="tool-icon blue">
          <van-icon name="checked" size="24" />
        </div>
        <div class="tool-name">库存盘点</div>
      </div>
      <div class="tool-item" @click="router.push('/loss-report')">
        <div class="tool-icon red">
          <van-icon name="warning" size="24" />
        </div>
        <div class="tool-name">报损单</div>
      </div>
      <div class="tool-item" @click="router.push('/account')">
        <div class="tool-icon green">
          <van-icon name="balance-o" size="24" />
        </div>
        <div class="tool-name">往来账</div>
      </div>
      <div class="tool-item" @click="router.push('/approve')">
        <div class="tool-icon purple">
          <van-icon name="passed" size="24" />
        </div>
        <div class="tool-name">审核中心</div>
      </div>
    </div>

    <!-- 系统功能 -->
    <div class="section-title">系统功能</div>
    <van-cell-group inset>
      <van-cell title="清除缓存" is-link @click="clearCache">
        <template #icon><van-icon name="clear" style="margin-right: 8px;" /></template>
      </van-cell>
      <van-cell title="检查更新" is-link value="当前版本 1.0.0">
        <template #icon><van-icon name="upgrade" style="margin-right: 8px;" /></template>
      </van-cell>
    </van-cell-group>

    <!-- 用户信息 -->
    <div class="user-info">
      <div class="user-avatar">{{ userInfo.name?.charAt(0) || 'U' }}</div>
      <div class="user-detail">
        <div class="user-name">{{ userInfo.name || '用户' }}</div>
        <div class="user-role">{{ userInfo.role || '销售员' }}</div>
      </div>
    </div>

    <!-- 退出登录 -->
    <div class="logout-btn">
      <van-button type="danger" block @click="handleLogout">退出登录</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const userInfo = ref({
  name: localStorage.getItem('user_name') || localStorage.getItem('user_role') || '用户',
  role: localStorage.getItem('user_role') || '老板'
})

const clearCache = () => {
  localStorage.clear()
  showToast('缓存已清除')
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.tools-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.tools-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; padding: 16px 12px; background: #fff; margin-bottom: 12px; }
.tool-item { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 16px 8px; border-radius: 12px; background: #f7f8fa; }
.tool-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #fff; }
.tool-icon.orange { background: linear-gradient(135deg, #ff6b35, #ff9a56); }
.tool-icon.blue { background: linear-gradient(135deg, #1989fa, #396bec); }
.tool-icon.red { background: linear-gradient(135deg, #ee0a24, #f56c6c); }
.tool-icon.green { background: linear-gradient(135deg, #07c160, #10b980); }
.tool-icon.purple { background: linear-gradient(135deg, #722ed1, #9c27b0); }
.tool-name { font-size: 13px; color: #333; }
.section-title { font-size: 14px; font-weight: bold; color: #333; margin: 16px 12px 8px; padding-left: 4px; }
.user-info { display: flex; align-items: center; gap: 12px; background: #fff; margin: 16px 12px; padding: 16px; border-radius: 12px; }
.user-avatar { width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #ff6b35, #ff9a56); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; }
.user-detail { flex: 1; }
.user-name { font-size: 16px; font-weight: bold; color: #333; }
.user-role { font-size: 12px; color: #999; margin-top: 4px; }
.logout-btn { padding: 20px 16px; }
</style>