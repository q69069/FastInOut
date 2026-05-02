<template>
  <div class="home">
    <div class="header">
      <div class="user-info">
        <span class="welcome">欢迎使用</span>
        <span class="username">{{ userName }}</span>
      </div>
    </div>
    <van-grid :column="3" class="menu-grid">
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
import { computed } from 'vue'

const userName = computed(() => {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user).name : '业务员'
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: #f7f8fa;
}
.header {
  background: linear-gradient(135deg, #1989fa, #396bec);
  padding: 32px 16px;
  color: #fff;
}
.user-info {
  display: flex;
  flex-direction: column;
}
.welcome {
  font-size: 14px;
  opacity: 0.8;
}
.username {
  font-size: 20px;
  font-weight: bold;
  margin-top: 4px;
}
.menu-grid {
  margin-top: 16px;
  background: #fff;
}
</style>
