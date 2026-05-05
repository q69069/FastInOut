<template>
  <div class="layout">
    <div class="content">
      <router-view />
    </div>
    <van-tabbar v-model="active" fixed safe-area-inset-bottom>
      <van-tabbar-item to="/home" icon="wap-home">首页</van-tabbar-item>
      <van-tabbar-item to="/workbench" icon="orders-o">工作台</van-tabbar-item>
      <van-tabbar-item to="/messages" icon="comment-o">消息</van-tabbar-item>
      <van-tabbar-item to="/tools" icon="setting-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const active = ref(0)

const tabPathMap = {
  '/home': 0,
  '/workbench': 1,
  '/messages': 2,
  '/tools': 3,
  '/account': 3
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