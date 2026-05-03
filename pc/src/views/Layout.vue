<template>
  <el-container style="height:100vh">
    <!-- Hover展开侧边栏 -->
    <div
      class="sidebar-wrapper"
      @mouseenter="expandSidebar"
      @mouseleave="collapseSidebar"
    >
      <el-aside :width="collapsed ? '60px' : '220px'" class="sidebar" style="background:#304156;transition:width 0.3s">
        <div class="logo" :class="{ collapsed: collapsed }">
          {{ collapsed ? 'FIO' : 'FastInOut' }}
        </div>
        <el-menu
          :default-active="currentTab.path"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          :collapse="collapsed"
          :collapse-transition="false"
        >
          <el-menu-item v-if="authStore.hasModule('home') || authStore.hasModule('dashboard')" index="/dashboard" @click="openTab('/dashboard', '首页')">
            <el-icon><DataBoard /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-sub-menu v-if="authStore.hasModule('products') || authStore.hasModule('customers')" index="archives">
            <template #title>
              <el-icon><Folder /></el-icon>
              <span>档案</span>
            </template>
            <el-menu-item v-if="authStore.hasModule('products')" index="/products" @click="openTab('/products', '商品管理')">商品管理</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('customers')" index="/customers" @click="openTab('/customers', '客户管理')">客户管理</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('customers')" index="/customer-prices" @click="openTab('/customer-prices', '客户价格等级')">客户价格等级</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('suppliers')" index="/suppliers" @click="openTab('/suppliers', '供应商管理')">供应商管理</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('suppliers')" index="/supplier-reconciliation" @click="openTab('/supplier-reconciliation', '供应商对账')">供应商对账</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('customers')" index="/customers/crm" @click="openTab('/customers/crm', '客户关系管理')">客户关系管理</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('products')" index="/units" @click="openTab('/units', '单位管理')">单位管理</el-menu-item>
          </el-sub-menu>
          <el-sub-menu v-if="authStore.hasModule('purchases')" index="purchase">
            <template #title>
              <el-icon><ShoppingCart /></el-icon>
              <span>采购</span>
            </template>
            <el-menu-item v-if="authStore.hasModule('purchases')" index="/purchases" @click="openTab('/purchases', '采购订单')">采购订单</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('purchases')" index="/purchase-returns" @click="openTab('/purchase-returns', '采购退货')">采购退货</el-menu-item>
          </el-sub-menu>
          <el-sub-menu v-if="authStore.hasModule('sales')" index="sale">
            <template #title>
              <el-icon><Sell /></el-icon>
              <span>销售</span>
            </template>
            <el-menu-item v-if="authStore.hasModule('sales')" index="/sales" @click="openTab('/sales', '销售订单')">销售订单</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('sales')" index="/sales-returns" @click="openTab('/sales-returns', '销售退货')">销售退货</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('salesmen')" index="/salesmen" @click="openTab('/salesmen', '业务员管理')">业务员管理</el-menu-item>
          </el-sub-menu>
          <el-menu-item v-if="authStore.hasModule('promotions')" index="/promotions" @click="openTab('/promotions', '促销')">
            <el-icon><PriceTag /></el-icon>
            <span>促销</span>
          </el-menu-item>
          <el-sub-menu v-if="authStore.hasModule('inventory') || authStore.hasModule('warehouses')" index="warehouse">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>仓库</span>
            </template>
            <el-menu-item v-if="authStore.hasModule('inventory')" index="/inventory" @click="openTab('/inventory', '库存查询')">库存查询</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('inventory')" index="/transfers" @click="openTab('/transfers', '库存调拨')">库存调拨</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('warehouses')" index="/warehouses" @click="openTab('/warehouses', '仓库管理')">仓库管理</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('batches')" index="/batches" @click="openTab('/batches', '批次管理')">批次管理</el-menu-item>
          </el-sub-menu>
          <el-sub-menu v-if="authStore.hasModule('finance')" index="finance">
            <template #title>
              <el-icon><Money /></el-icon>
              <span>财务</span>
            </template>
            <el-menu-item v-if="authStore.hasModule('finance')" index="/finance" @click="openTab('/finance', '收支管理')">收支管理</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('finance')" index="/bank-reconciliation" @click="openTab('/bank-reconciliation', '银行对账')">银行对账</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('finance')" index="/invoices" @click="openTab('/invoices', '发票管理')">发票管理</el-menu-item>
          </el-sub-menu>
          <el-sub-menu v-if="authStore.hasModule('reports')" index="reports">
            <template #title>
              <el-icon><DataBoard /></el-icon>
              <span>报表</span>
            </template>
            <el-menu-item v-if="authStore.hasModule('reports')" index="/reports/profit" @click="openTab('/reports/profit', '利润统计')">利润统计</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('reports')" index="/reports/inventory" @click="openTab('/reports/inventory', '库存汇总')">库存汇总</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('reports')" index="/reports/sales-ranking" @click="openTab('/reports/sales-ranking', '销售排行')">销售排行</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('reports')" index="/reports/trend" @click="openTab('/reports/trend', '趋势图')">趋势图</el-menu-item>
          </el-sub-menu>
          <el-sub-menu v-if="authStore.hasModule('roles') || authStore.hasModule('employees')" index="system">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统</span>
            </template>
            <el-menu-item v-if="authStore.hasModule('roles')" index="/system/roles" @click="openTab('/system/roles', '角色管理')">角色管理</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('system')" index="/system/backup" @click="openTab('/system/backup', '数据备份')">数据备份</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('system')" index="/system/print-templates" @click="openTab('/system/print-templates', '打印模板')">打印模板</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('system')" index="/system/data-import" @click="openTab('/system/data-import', '数据导入')">数据导入</el-menu-item>
            <el-menu-item v-if="authStore.hasModule('system')" index="/system/logs" @click="openTab('/system/logs', '操作日志')">操作日志</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
    </div>

    <el-container>
      <!-- 顶部标签栏 -->
      <div class="tab-bar">
        <div class="tabs-container">
          <div
            v-for="(tab, index) in tabs"
            :key="tab.path"
            :class="['tab-item', { active: currentTab.path === tab.path, pinned: tab.pinned }]"
            @click="switchTab(tab)"
            @contextmenu.prevent="showContextMenu($event, tab, index)"
          >
            <span class="tab-title">{{ tab.title }}</span>
            <span v-if="!tab.pinned" class="tab-close" @click.stop="closeTab(tab)">&times;</span>
          </div>
        </div>
        <div class="tab-actions">
          <el-dropdown @command="handleTabAction">
            <span class="tab-more">&#8226;&#8226;&#8226;</span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="close-others">关闭其他</el-dropdown-item>
                <el-dropdown-item command="close-all">关闭所有</el-dropdown-item>
                <el-dropdown-item command="refresh">刷新当前</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 主内容区 -->
      <el-main style="background:#f5f7fa;padding:0;overflow:hidden">
        <div class="page-container">
          <router-view v-slot="{ Component }">
            <keep-alive :include="keepAliveRoutes">
              <component :is="Component" :key="route.path" />
            </keep-alive>
          </router-view>
        </div>
      </el-main>
    </el-container>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      @click.stop
    >
      <div class="context-item" @click="pinTab(contextMenu.tab)">
        {{ contextMenu.tab?.pinned ? '取消固定' : '固定标签' }}
      </div>
      <div class="context-item" @click="closeTab(contextMenu.tab)" v-if="!contextMenu.tab?.pinned">
        关闭
      </div>
      <div class="context-item" @click="closeOtherTabs" v-if="!contextMenu.tab?.pinned">
        关闭其他
      </div>
      <div class="context-divider" v-if="contextMenu.tab?.pinned"></div>
      <div class="context-item" @click="refreshPage" v-if="currentTab.path === contextMenu.tab?.path">
        刷新
      </div>
    </div>
  </el-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 侧边栏状态
const collapsed = ref(true)
let hoverTimer = null

const expandSidebar = () => {
  clearTimeout(hoverTimer)
  collapsed.value = false
}

const collapseSidebar = () => {
  hoverTimer = setTimeout(() => {
    collapsed.value = true
  }, 300)
}

// 标签页管理
const tabs = ref([
  { path: '/dashboard', title: '首页', pinned: true }
])
const currentTab = computed(() => tabs.value.find(t => t.path === route.path) || tabs.value[0])
const keepAliveRoutes = computed(() => tabs.value.map(t => t.path.replace('/', '')))

const openTab = (path, title) => {
  const existing = tabs.value.find(t => t.path === path)
  if (existing) {
    router.push(path)
    return
  }
  tabs.value.push({ path, title, pinned: false })
  router.push(path)
}

const switchTab = (tab) => {
  router.push(tab.path)
}

const closeTab = (tab) => {
  if (tab.pinned) return
  const index = tabs.value.findIndex(t => t.path === tab.path)
  tabs.value.splice(index, 1)
  if (currentTab.value.path === tab.path && tabs.value.length > 0) {
    router.push(tabs.value[tabs.value.length - 1].path)
  }
}

const closeOtherTabs = () => {
  tabs.value = tabs.value.filter(t => t.pinned || t.path === currentTab.value.path)
}

// 右键菜单
const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
  tab: null
})

const showContextMenu = (e, tab, index) => {
  contextMenu.visible = true
  contextMenu.x = e.clientX
  contextMenu.y = e.clientY
  contextMenu.tab = tab
}

const hideContextMenu = () => {
  contextMenu.visible = false
}

const pinTab = (tab) => {
  tab.pinned = !tab.pinned
  hideContextMenu()
}

const refreshPage = () => {
  router.go(0)
  hideContextMenu()
}

// Tab操作
const handleTabAction = (cmd) => {
  if (cmd === 'close-others') {
    tabs.value = tabs.value.filter(t => t.pinned || t.path === currentTab.value.path)
  } else if (cmd === 'close-all') {
    tabs.value = tabs.value.filter(t => t.pinned)
    if (tabs.value.length > 0) {
      router.push(tabs.value[0].path)
    }
  } else if (cmd === 'refresh') {
    router.go(0)
  }
}

// 快捷键 Alt+数字
const handleKeydown = (e) => {
  if (e.altKey && e.key >= '1' && e.key <= '9') {
    const index = parseInt(e.key) - 1
    if (tabs.value[index]) {
      switchTab(tabs.value[index])
    }
  }
}

// 点击空白关闭右键菜单
const handleClick = () => {
  if (contextMenu.visible) {
    hideContextMenu()
  }
}

// 监听路由变化，自动添加标签
watch(() => route.path, (newPath) => {
  const meta = route.meta
  const title = meta.title || '未命名'
  const existing = tabs.value.find(t => t.path === newPath)
  if (!existing && newPath !== '/login') {
    // 新页面自动加标签，最多保留10个
    if (tabs.value.length < 10) {
      tabs.value.push({ path: newPath, title, pinned: false })
    }
  }
})

onMounted(() => {
  document.addEventListener('click', handleClick)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClick)
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.sidebar-wrapper {
  display: flex;
  flex-shrink: 0;
  z-index: 100;
}

.sidebar {
  overflow: hidden;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  background: #263445;
  transition: all 0.3s;
}

.logo.collapsed {
  font-size: 14px;
  letter-spacing: 2px;
}

.tab-bar {
  height: 42px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 8px;
}

.tabs-container {
  display: flex;
  overflow-x: auto;
  flex: 1;
  gap: 4px;
}

.tabs-container::-webkit-scrollbar {
  display: none;
}

.tab-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: #f5f7fa;
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  white-space: nowrap;
  font-size: 13px;
  color: #666;
  transition: all 0.2s;
  border: 1px solid #e4e7ed;
  border-bottom: none;
}

.tab-item:hover {
  background: #ecf5ff;
  color: #409eff;
}

.tab-item.active {
  background: #fff;
  color: #409eff;
  border-color: #409eff;
  font-weight: 500;
}

.tab-item.pinned {
  background: #fdf6ec;
  border-color: #e6a23c;
}

.tab-title {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tab-close {
  margin-left: 8px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  line-height: 1;
}

.tab-close:hover {
  background: rgba(64, 158, 255, 0.2);
}

.tab-actions {
  flex-shrink: 0;
}

.tab-more {
  cursor: pointer;
  padding: 4px 8px;
  font-size: 18px;
  color: #999;
}

.tab-more:hover {
  color: #409eff;
}

.context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  z-index: 9999;
  padding: 4px 0;
  min-width: 120px;
}

.context-item {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 13px;
  color: #666;
}

.context-item:hover {
  background: #f5f7fa;
  color: #409eff;
}

.context-divider {
  height: 1px;
  background: #e4e7ed;
  margin: 4px 0;
}

.page-container {
  height: calc(100vh - 42px);
  overflow-y: auto;
  padding: 16px;
}
</style>