<template>
  <el-container style="height:100vh">
    <el-aside width="220px" style="background:#304156">
      <div class="logo">FastInOut</div>
      <el-menu
        :default-active="route.path"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-sub-menu index="archives">
          <template #title>
            <el-icon><Folder /></el-icon>
            <span>档案</span>
          </template>
          <el-menu-item index="/products">商品管理</el-menu-item>
          <el-menu-item index="/customers">客户管理</el-menu-item>
          <el-menu-item index="/customer-prices">客户价格等级</el-menu-item>
          <el-menu-item index="/suppliers">供应商管理</el-menu-item>
          <el-menu-item index="/customers/crm">客户关系管理</el-menu-item>
          <el-menu-item index="/units">单位管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="purchase">
          <template #title>
            <el-icon><ShoppingCart /></el-icon>
            <span>采购</span>
          </template>
          <el-menu-item index="/purchases">采购订单</el-menu-item>
          <el-menu-item index="/purchase-returns">采购退货</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="sale">
          <template #title>
            <el-icon><Sell /></el-icon>
            <span>销售</span>
          </template>
          <el-menu-item index="/sales">销售订单</el-menu-item>
          <el-menu-item index="/sales-returns">销售退货</el-menu-item>
          <el-menu-item index="/salesmen">业务员管理</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/promotions">
          <el-icon><PriceTag /></el-icon>
          <span>促销</span>
        </el-menu-item>
        <el-sub-menu index="warehouse">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>仓库</span>
          </template>
          <el-menu-item index="/inventory">库存查询</el-menu-item>
          <el-menu-item index="/transfers">库存调拨</el-menu-item>
          <el-menu-item index="/warehouses">仓库管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="finance">
          <template #title>
            <el-icon><Money /></el-icon>
            <span>财务</span>
          </template>
          <el-menu-item index="/finance">收支管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="reports">
          <template #title>
            <el-icon><DataBoard /></el-icon>
            <span>报表</span>
          </template>
          <el-menu-item index="/reports/profit">利润统计</el-menu-item>
          <el-menu-item index="/reports/inventory">库存汇总</el-menu-item>
          <el-menu-item index="/reports/sales-ranking">销售排行</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background:#fff;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #eee">
        <span style="font-size:18px;color:#333">{{ route.meta.title || '首页' }}</span>
        <el-dropdown @command="handleCommand">
          <span style="cursor:pointer;color:#666">
            <el-icon><User /></el-icon> admin
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main style="background:#f5f7fa;padding:20px">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const handleCommand = (cmd) => {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  background: #263445;
}
</style>
