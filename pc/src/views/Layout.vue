<template>
  <el-container style="height:100vh">
    <!-- 侧边栏 - 始终展开220px -->
    <div class="sidebar-wrapper">
      <el-aside width="220px" class="sidebar" style="background:#1f2d3d">
        <div class="logo">FastInOut</div>

        <!-- 主模块列表 -->
        <div class="main-modules">
          <div
            v-for="item in visibleMainModules"
            :key="item.key"
            class="main-module"
            :class="{ active: activePopup === item.key }"
            @mouseenter="showPopup(item)"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </div>
        </div>
      </el-aside>

      <!-- Hover浮层 - 子模块列表 -->
      <transition name="popup-fade">
        <div
          v-if="activePopup && currentSubModules.length > 0"
          class="submenu-popup"
          @mouseenter="keepPopup"
          @mouseleave="hidePopupDelay"
        >
          <div class="popup-header">{{ currentPopupLabel }}</div>
          <div class="submenu-list">
            <div
              v-for="sub in currentSubModules"
              :key="sub.path"
              class="submenu-item"
              @click="openTab(sub.path, sub.label)"
            >
              {{ sub.label }}
            </div>
          </div>
        </div>
      </transition>
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
          <el-dropdown @command="handleTabAction" trigger="click">
            <span class="tab-more">&#8226;&#8226;&#8226;</span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="close-others">关闭其他</el-dropdown-item>
                <el-dropdown-item command="close-all">关闭所有</el-dropdown-item>
                <el-dropdown-item command="refresh">刷新当前</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-dropdown @command="handleUserAction" trigger="click">
            <span class="user-info">{{ authStore.displayName }} ({{ authStore.roleName }})</span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
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
import {
  DataBoard, Folder, ShoppingCart, Sell, PriceTag, Box,
  Money, Setting, Document
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 侧边栏主模块定义
const mainModules = [
  {
    key: 'home',
    label: '首页',
    icon: 'DataBoard',
    submodules: [
      { path: '/dashboard', label: '首页' }
    ]
  },
  {
    key: 'archives',
    label: '档案',
    icon: 'Folder',
    submodules: [
      { path: '/products', label: '商品管理', module: 'products' },
      { path: '/customers', label: '客户管理', module: 'customers' },
      { path: '/customer-prices', label: '客户价格等级', module: 'customers' },
      { path: '/suppliers', label: '供应商管理', module: 'suppliers' },
      { path: '/supplier-reconciliation', label: '供应商对账', module: 'suppliers' },
      { path: '/customers/crm', label: '客户关系管理', module: 'customers' },
      { path: '/units', label: '单位管理', module: 'products' }
    ]
  },
  {
    key: 'purchase',
    label: '采购',
    icon: 'ShoppingCart',
    submodules: [
      { path: '/purchases', label: '采购订单', module: 'purchases' },
      { path: '/purchase-returns', label: '采购退货', module: 'purchases' }
    ]
  },
  {
    key: 'sale',
    label: '销售',
    icon: 'Sell',
    submodules: [
      { path: '/sales', label: '销售订单', module: 'sales' },
      { path: '/sales-returns', label: '销售退货', module: 'sales' },
      { path: '/salesmen', label: '业务员管理', module: 'sales' }
    ]
  },
  {
    key: 'promotions',
    label: '促销',
    icon: 'PriceTag',
    submodules: [
      { path: '/promotions', label: '促销方案', module: 'promotions' }
    ]
  },
  {
    key: 'warehouse',
    label: '仓库',
    icon: 'Box',
    submodules: [
      { path: '/inventory', label: '库存查询', module: 'inventory' },
      { path: '/transfers', label: '库存调拨', module: 'inventory' },
      { path: '/warehouses', label: '仓库管理', module: 'warehouses' },
      { path: '/batches', label: '批次管理', module: 'batches' }
    ]
  },
  {
    key: 'finance',
    label: '财务',
    icon: 'Money',
    submodules: [
      { path: '/finance', label: '收支管理', module: 'finance' },
      { path: '/bank-reconciliation', label: '银行对账', module: 'finance' },
      { path: '/invoices', label: '发票管理', module: 'finance' }
    ]
  },
  {
    key: 'reports',
    label: '报表',
    icon: 'Document',
    submodules: [
      { path: '/reports/profit', label: '利润统计', module: 'reports' },
      { path: '/reports/inventory', label: '库存汇总', module: 'reports' },
      { path: '/reports/sales-ranking', label: '销售排行', module: 'reports' },
      { path: '/reports/trend', label: '趋势图', module: 'reports' }
    ]
  },
  {
    key: 'system',
    label: '系统',
    icon: 'Setting',
    submodules: [
      { path: '/system/roles', label: '角色管理', module: 'roles' },
      { path: '/system/backup', label: '数据备份', module: 'system' },
      { path: '/system/print-templates', label: '打印模板', module: 'system' },
      { path: '/system/data-import', label: '数据导入', module: 'system' },
      { path: '/system/logs', label: '操作日志', module: 'system' }
    ]
  }
]

// 根据权限过滤可见的主模块
const visibleMainModules = computed(() => {
  return mainModules.filter(m => {
    if (m.key === 'home') return true
    if (m.key === 'archives') return authStore.hasModule('products') || authStore.hasModule('customers')
    if (m.key === 'warehouse') return authStore.hasModule('inventory') || authStore.hasModule('warehouses')
    if (m.key === 'system') return authStore.hasModule('roles') || authStore.hasModule('system')
    return authStore.hasModule(m.key)
  })
})

// 弹窗相关
const activePopup = ref(null)
let hideTimer = null

const showPopup = (item) => {
  clearTimeout(hideTimer)
  activePopup.value = item.key
}

const keepPopup = () => {
  clearTimeout(hideTimer)
}

const hidePopupDelay = () => {
  hideTimer = setTimeout(() => {
    activePopup.value = null
  }, 200)
}

const currentPopupLabel = computed(() => {
  const m = mainModules.find(m => m.key === activePopup.value)
  return m ? m.label : ''
})

const currentSubModules = computed(() => {
  const m = mainModules.find(m => m.key === activePopup.value)
  if (!m) return []

  // 根据权限过滤子模块
  return m.submodules.filter(sub => {
    if (!sub.module || authStore.isAdmin) return true
    return authStore.hasModule(sub.module)
  })
})

// 标签页管理
const tabs = ref([
  { path: '/dashboard', title: '首页', pinned: true }
])
const currentTab = computed(() => tabs.value.find(t => t.path === route.path) || tabs.value[0])
const keepAliveRoutes = computed(() => tabs.value.map(t => t.path.replace('/', '')))

const openTab = (path, title) => {
  activePopup.value = null
  const existing = tabs.value.find(t => t.path === path)
  if (existing) {
    router.push(path)
    return
  }
  if (tabs.value.length < 10) {
    tabs.value.push({ path, title, pinned: false })
  }
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

// 用户操作（退出登录）
const handleUserAction = (cmd) => {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
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
  clearTimeout(hideTimer)
})
</script>

<style scoped>
.sidebar-wrapper {
  display: flex;
  flex-shrink: 0;
  z-index: 100;
  position: relative;
}

.sidebar {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  background: #1a1a1a;
  letter-spacing: 2px;
}

.main-modules {
  flex: 1;
  padding: 8px 0;
  overflow-y: auto;
}

.main-module {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: #bfcbd9;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  gap: 10px;
}

.main-module:hover,
.main-module.active {
  background: rgba(64, 158, 255, 0.15);
  color: #409eff;
}

.main-module .el-icon {
  font-size: 18px;
  flex-shrink: 0;
}

/* 浮层样式 */
.submenu-popup {
  position: absolute;
  left: 220px;
  top: 0;
  width: 200px;
  min-height: 200px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid #e4e7ed;
  z-index: 1000;
  overflow: hidden;
}

.popup-header {
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.submenu-list {
  padding: 8px 0;
}

.submenu-item {
  padding: 10px 16px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.15s;
}

.submenu-item:hover {
  background: #ecf5ff;
  color: #409eff;
}

/* 动画 */
.popup-fade-enter-active,
.popup-fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.popup-fade-enter-from,
.popup-fade-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* 标签栏样式 */
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

.user-info {
  cursor: pointer;
  padding: 4px 12px;
  font-size: 13px;
  color: #606266;
  border-radius: 4px;
  background: #f5f7fa;
  margin-left: 8px;
}

.user-info:hover {
  color: #409eff;
  background: #ecf5ff;
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