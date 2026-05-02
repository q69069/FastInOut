<template>
  <div class="layout">
    <div class="content">
      <router-view />
    </div>
    <van-tabbar v-model="active" route fixed safe-area-inset-bottom>
      <van-tabbar-item to="/home" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item to="/todo" icon="todo-o">待办</van-tabbar-item>
      <van-tabbar-item to="/order" icon="orders-o">下单</van-tabbar-item>
      <van-tabbar-item to="/inventory" icon="search">库存</van-tabbar-item>
      <van-tabbar-item to="/performance" icon="chart-trending-o">业绩</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const active = ref(0)
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; }
.layout { height: 100vh; display: flex; flex-direction: column; }
.content { flex: 1; overflow-y: auto; padding-bottom: 50px; }
</style>