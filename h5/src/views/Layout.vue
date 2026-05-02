<template>
  <van-tabbar v-model="active" route fixed placeholder safe-area-inset-bottom>
    <van-tabbar-item to="/home" icon="home-o">首页</van-tabbar-item>
    <van-tabbar-item to="/todo" icon="todo-o">待办</van-tabbar-item>
    <van-tabbar-item to="/order" icon="orders-o">下单</van-tabbar-item>
    <van-tabbar-item to="/inventory" icon="search">库存</van-tabbar-item>
    <van-tabbar-item to="/performance" icon="chart-trending-o">业绩</van-tabbar-item>
  </van-tabbar>
</template>

<script setup>
import { ref } from 'vue'

const active = ref(0)
</script>
