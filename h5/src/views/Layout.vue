<template>
  <div class="layout">
    <div class="content">
      <router-view />
    </div>
    <van-tabbar v-model="active" fixed safe-area-inset-bottom>
      <van-tabbar-item v-for="tab in visibleTabs" :key="tab.path" :to="tab.path" :icon="tab.icon">{{ tab.name }}</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const active = ref(0)

const allTabs = [
  { path: '/home', name: '首页', icon: 'wap-home', roles: ['老板', '销售', '财务', '库管', '后台'] },
  { path: '/dashboard', name: '看板', icon: 'chart-trending-o', roles: ['老板', '财务'] },
  { path: '/customers', name: '客户', icon: 'friends', roles: ['老板', '销售'] },
  { path: '/performance', name: '业绩', icon: 'chart-trending-o', roles: ['老板', '销售', '财务'] },
  { path: '/inventory', name: '仓库', icon: 'logistics', roles: ['老板', '库管'] },
  { path: '/supplier', name: '供应商', icon: 'shop-o', roles: ['老板', '采购'] },
  { path: '/employee', name: '员工', icon: 'manager-o', roles: ['老板'] },
  { path: '/tools', name: '工具', icon: 'setting-o', roles: ['老板', '销售', '财务', '库管', '后台'] }
]

const getUserRole = () => localStorage.getItem('user_role') || '老板'

const visibleTabs = computed(() => {
  const role = getUserRole()
  return allTabs.filter(tab => tab.roles.includes(role))
})

watch(() => route.path, (path) => {
  const idx = visibleTabs.value.findIndex(t => t.path === path)
  if (idx >= 0) active.value = idx
}, { immediate: true })
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; }
.layout { height: 100vh; display: flex; flex-direction: column; background: #f7f8fa; }
.content { flex: 1; overflow-y: auto; padding-bottom: 60px; }
</style>