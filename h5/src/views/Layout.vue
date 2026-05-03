<template>
  <div class="layout">
    <div class="content">
      <router-view />
    </div>
    <van-tabbar v-model="active" fixed safe-area-inset-bottom>
      <van-tabbar-item to="/home" icon="wap-home">首页</van-tabbar-item>
      <van-tabbar-item v-if="authStore.hasModule('dashboard')" to="/dashboard" icon="chart-trending-o">看板</van-tabbar-item>
      <van-tabbar-item v-if="authStore.hasModule('customers')" to="/customers" icon="friends">客户</van-tabbar-item>
      <van-tabbar-item v-if="authStore.hasModule('performance')" to="/performance" icon="graphic">业绩</van-tabbar-item>
      <van-tabbar-item v-if="authStore.hasModule('tools') || authStore.hasModule('profile')" to="/tools" icon="setting-o">工具</van-tabbar-item>
      <van-tabbar-item v-if="authStore.hasModule('inventory')" to="/inventory" icon="logistics">库存</van-tabbar-item>
      <van-tabbar-item v-if="authStore.hasModule('finance')" to="/receivables" icon="balance-o">财务</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores'

const route = useRoute()
const authStore = useAuthStore()
const active = ref(0)

watch(() => route.path, (path) => {
  if (path === '/home') active.value = 0
  else if (path === '/dashboard') active.value = 1
  else if (path === '/customers') active.value = 2
  else if (path === '/performance') active.value = 3
  else if (path === '/inventory') active.value = 4
  else if (path === '/tools') active.value = 5
  else if (path === '/receivables') active.value = 6
}, { immediate: true })
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; }
.layout { height: 100vh; display: flex; flex-direction: column; background: #f7f8fa; }
.content { flex: 1; overflow-y: auto; padding-bottom: 60px; }
</style>