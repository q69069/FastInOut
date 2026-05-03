<template>
  <div class="forbidden-container">
    <div class="forbidden-content">
      <div class="icon">403</div>
      <h2>无权访问</h2>
      <p>您没有权限访问此页面，请联系管理员授权。</p>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.forbidden-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}

.forbidden-content {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.icon {
  font-size: 72px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 20px;
}

h2 {
  margin: 0 0 16px;
  color: #303133;
}

p {
  margin: 0 0 24px;
  color: #606266;
}
</style>