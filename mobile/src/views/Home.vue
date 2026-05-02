<template>
  <div class="home-page">
    <van-nav-bar title="工作台" fixed placeholder>
      <template #right>
        <van-icon name="contact" size="22" @click="showLogout = true" />
      </template>
    </van-nav-bar>

    <!-- 欢迎卡片 -->
    <div class="welcome-card">
      <van-icon name="user-circle-o" size="40" color="#667eea" />
      <div class="welcome-text">
        <div class="name">{{ auth.userName }}</div>
        <div class="role">{{ roleLabel }}</div>
      </div>
    </div>

    <!-- 8大窗口入口 -->
    <div class="menu-grid">
      <div class="menu-item" v-for="item in menuItems" :key="item.path" @click="go(item.path)">
        <div class="menu-icon" :style="{ background: item.color }">
          <van-icon :name="item.icon" size="28" color="#fff" />
        </div>
        <span class="menu-label">{{ item.name }}</span>
      </div>
    </div>

    <van-dialog v-model:show="showLogout" title="退出登录" show-cancel-button
      @confirm="doLogout" message="确定要退出吗？" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const showLogout = ref(false)

const roleLabel = computed(() => {
  const map = { admin: '管理员', sales: '业务员', warehouse: '仓管', finance: '财务' }
  return map[auth.roleType] || auth.roleType
})

const menuItems = [
  { name: '待办订单', path: '/pending-orders', icon: 'orders-o', color: '#ee0a24' },
  { name: '拜访计划', path: '/visit-plan', icon: 'map-marked', color: '#ff976a' },
  { name: '门店打卡', path: '/store-checkin', icon: 'photograph', color: '#07c160' },
  { name: '快速下单', path: '/quick-order', icon: 'cart-o', color: '#1989fa' },
  { name: '打印小票', path: '/print-receipt', icon: 'printer', color: '#7232dd' },
  { name: '业绩查看', path: '/performance', icon: 'chart-trending-o', color: '#ff6b6b' },
  { name: '查库存', path: '/stock-check', icon: 'box', color: '#f5a623' },
  { name: '应收查询', path: '/receivables', icon: 'balance-list-o', color: '#4ecdc4' }
]

const go = (path) => router.push(path)

const doLogout = () => {
  auth.logout()
  router.replace('/login')
}
</script>

<style scoped>
.home-page { padding-bottom: 20px; }
.welcome-card {
  display: flex; align-items: center; gap: 12px;
  margin: 12px; padding: 16px; background: #fff; border-radius: 12px;
}
.welcome-text .name { font-size: 18px; font-weight: 600; color: #333; }
.welcome-text .role { font-size: 13px; color: #999; margin-top: 2px; }
.menu-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
  padding: 8px 12px;
}
.menu-item {
  display: flex; flex-direction: column; align-items: center;
  background: #fff; border-radius: 12px; padding: 14px 8px;
  cursor: pointer; transition: transform .15s;
}
.menu-item:active { transform: scale(.95); }
.menu-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; margin-bottom: 6px;
}
.menu-label { font-size: 12px; color: #555; text-align: center; line-height: 1.3; }
</style>
