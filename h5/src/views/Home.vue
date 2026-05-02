<template>
  <div class="home">
    <div class="header">
      <div class="user-info">
        <span class="welcome">欢迎使用</span>
        <span class="username">{{ authStore.displayName || '业务员' }}</span>
      </div>
    </div>
    <van-grid :column="3" class="menu-grid" square clickable>
      <van-grid-item to="/todo" icon="todo-o" text="待办" />
      <van-grid-item to="/visit" icon="location-o" text="拜访" />
      <van-grid-item to="/checkin" icon="clock-o" text="打卡" />
      <van-grid-item to="/order" icon="orders-o" text="下单" />
      <van-grid-item to="/print" icon="printer-o" text="打印" />
      <van-grid-item to="/inventory" icon="search" text="查库存" />
      <van-grid-item to="/receivables" icon="balance-o" text="应收" />
      <van-grid-item to="/performance" icon="chart-trending-o" text="业绩" />
    </van-grid>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
const authStore = useAuthStore()
</script>

<style scoped>
.home { min-height: 100%; background: #f7f8fa; }
.header { background: linear-gradient(135deg, #1989fa, #396bec); padding: 40px 16px; color: #fff; }
.welcome { font-size: 14px; opacity: 0.8; }
.username { font-size: 22px; font-weight: bold; margin-top: 8px; display: block; }
.menu-grid { margin-top: 16px; background: #fff; }
</style>