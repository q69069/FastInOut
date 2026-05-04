<template>
  <div class="layout">
    <div class="content">
      <router-view />
    </div>
    <van-tabbar v-model="active" fixed safe-area-inset-bottom>
      <van-tabbar-item to="/home" icon="wap-home">首页</van-tabbar-item>
      <van-tabbar-item v-if="authStore.hasModule('sales')" to="/vehicle-sales" icon="shopping-cart-o">车销</van-tabbar-item>
      <van-tabbar-item v-if="authStore.hasModule('inventory')" to="/vehicle-load" icon="logistics">装车</van-tabbar-item>
      <van-tabbar-item v-if="authStore.hasModule('customers')" to="/customers" icon="friends-o">客户</van-tabbar-item>
      <van-tabbar-item v-if="authStore.hasModule('sales')" to="/settlement" icon="balance-o">交账</van-tabbar-item>
      <van-tabbar-item to="/tools" icon="setting-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const active = ref(0)

const tabPathMap = {
  '/home': 0,
  '/vehicle-sales': 1,
  '/vehicle-load': 2,
  '/customers': 3,
  '/settlement': 4,
  '/tools': 5,
  '/account': 5
}

watch(() => route.path, (path) => {
  active.value = tabPathMap[path] ?? 0
}, { immediate: true })
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; }
.layout { height: 100vh; display: flex; flex-direction: column; background: #f7f8fa; }
.content { flex: 1; overflow-y: auto; padding-bottom: 60px; }
</style>
