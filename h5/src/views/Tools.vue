<template>
  <div class="page">
    <!-- 用户信息区 -->
    <div class="user-header">
      <div class="avatar">{{ authStore.displayName?.charAt(0) || 'U' }}</div>
      <div class="user-info">
        <div class="name">{{ authStore.displayName || '用户' }}</div>
        <div class="role">{{ authStore.roleName || '员工' }}</div>
      </div>
    </div>

    <!-- 快捷功能 -->
    <div class="section">
      <div class="section-title">快捷功能</div>
      <van-cell-group inset>
        <van-cell title="打印小票" is-link @click="$router.push('/print')">
          <template #icon><van-icon name="printer-o" style="margin-right:8px;color:#1989fa" /></template>
        </van-cell>
        <van-cell v-if="hasModule('sales') || hasModule('purchases')" title="审核中心" is-link @click="$router.push('/approve')">
          <template #icon><van-icon name="passed" style="margin-right:8px;color:#ff976a" /></template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 系统设置 -->
    <div class="section">
      <div class="section-title">系统设置</div>
      <van-cell-group inset>
        <van-cell v-if="hasModule('products')" title="品牌管理" is-link @click="$router.push('/brand')">
          <template #icon><van-icon name="flag-o" style="margin-right:8px;color:#1989fa" /></template>
        </van-cell>
        <van-cell v-if="hasModule('customers')" title="渠道管理" is-link @click="$router.push('/channel')">
          <template #icon><van-icon name="cluster-o" style="margin-right:8px;color:#07c160" /></template>
        </van-cell>
        <van-cell v-if="hasModule('customers')" title="客户等级" is-link @click="$router.push('/customer-level')">
          <template #icon><van-icon name="user-o" style="margin-right:8px;color:#ff976a" /></template>
        </van-cell>
        <van-cell v-if="hasModule('reports')" title="报表中心" is-link @click="$router.push('/reports')">
          <template #icon><van-icon name="chart-trending-o" style="margin-right:8px;color:#722ed1" /></template>
        </van-cell>
        <van-cell v-if="hasModule('finance')" title="发票管理" is-link @click="$router.push('/invoice')">
          <template #icon><van-icon name="invoice-o" style="margin-right:8px;color:#ee0a24" /></template>
        </van-cell>
        <van-cell title="检查更新" value="当前版本 1.0.0">
          <template #icon><van-icon name="upgrade" style="margin-right:8px;color:#323233" /></template>
        </van-cell>
        <van-cell title="清除缓存" is-link @click="clearCache">
          <template #icon><van-icon name="clear" style="margin-right:8px;color:#323233" /></template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 退出登录 -->
    <div class="logout-btn">
      <van-button type="danger" block @click="handleLogout">退出登录</van-button>
    </div>
  </div>
</template>

<script setup>
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const hasModule = (key) => authStore.hasModule(key) || authStore.isAdmin

const clearCache = () => {
  showToast('缓存已清除')
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.page { background: #f7f8fa; min-height: 100vh; padding-bottom: 20px; }
.user-header {
  display: flex; align-items: center; gap: 12px;
  background: linear-gradient(135deg, #ff6b35, #ff9a56);
  padding: 24px 16px;
  color: #fff;
}
.avatar { width: 56px; height: 56px; border-radius: 50%; background: rgba(255,255,255,0.25); display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; }
.name { font-size: 18px; font-weight: bold; }
.role { font-size: 13px; opacity: 0.85; margin-top: 2px; }
.section { margin: 16px 0; }
.section-title { font-size: 13px; font-weight: bold; color: #666; margin-bottom: 4px; padding-left: 16px; }
.logout-btn { padding: 16px; }
</style>