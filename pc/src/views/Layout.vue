<template>
  <div class="layout">
    <!-- 左侧侧边栏 -->
    <div class="sidebar">
      <div class="logo">FIO</div>
      <div class="nav-list">
        <div
          v-for="item in visibleMainModules"
          :key="item.key"
          class="nav-item"
          :class="{ active: activeModule === item.key }"
          @click="toggleModule(item)"
          @mouseenter="hoverModule(item, $event)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span class="nav-label">{{ item.label }}</span>
          <el-icon class="arrow"><ArrowRight /></el-icon>
        </div>
      </div>
      <div class="sidebar-footer">
        <div class="user-badge">
          <el-avatar size="small" style="background:#409eff">{{ authStore.displayName?.[0] || 'A' }}</el-avatar>
          <div class="user-info">
            <div class="user-name">{{ authStore.displayName }}</div>
            <div class="user-role">{{ authStore.roleName }}</div>
          </div>
          <el-icon class="logout-btn" @click="logout" title="退出登录"><SwitchButton /></el-icon>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-area">
      <!-- 顶部标签栏 - 悬浮不占位 -->
      <div class="topbar">
        <div class="tabs-wrap">
          <div
            v-for="(tab, idx) in tabs"
            :key="tab.path"
            :class="['top-tab', { active: currentTab.path === tab.path, pinned: tab.pinned }]"
            @click="switchTab(tab)"
            @contextmenu.prevent="showContextMenu($event, tab, idx)"
          >
            <span class="tab-label">{{ tab.title }}</span>
            <span v-if="!tab.pinned" class="tab-close" @click.stop="closeTab(tab)">×</span>
          </div>
        </div>
        <div class="topbar-actions">
          <el-dropdown @command="handleTabAction" trigger="click">
            <span class="more-btn">···</span>
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

      <!-- 页面内容 -->
      <div class="content-area">
        <router-view v-slot="{ Component }">
          <keep-alive :include="keepAliveRoutes">
            <component :is="Component" :key="route.path" />
          </keep-alive>
        </router-view>
      </div>
    </div>

    <!-- 子模块下拉浮层 - 跟随hover的主模块水平居中 -->
    <transition name="dropdown-fade">
      <div
        v-if="activeModule && currentSubs.length > 0"
        class="submenu-dropdown"
        :style="dropdownStyle"
        @mouseleave="startHideTimer"
        @mouseenter="cancelHideTimer"
      >
        <div class="submenu-header">{{ currentModuleLabel }}</div>
        <div class="submenu-items">
          <div
            v-for="sub in currentSubs"
            :key="sub.path"
            class="submenu-item"
            :class="{ highlight: isHighlight(sub.path) }"
            @click="openTab(sub.path, sub.label)"
          >
            {{ sub.label }}
          </div>
        </div>
      </div>
    </transition>

    <!-- 右键菜单 -->
    <div
      v-if="ctx.visible"
      class="ctx-menu"
      :style="{ left: ctx.x + 'px', top: ctx.y + 'px' }"
      @click.stop
    >
      <div class="ctx-item" @click="pinTab">{{ ctx.tab?.pinned ? '取消固定' : '固定标签' }}</div>
      <div class="ctx-item" @click="ctxCloseTab" v-if="!ctx.tab?.pinned">关闭</div>
      <div class="ctx-item" @click="ctxCloseOthers">关闭其他</div>
      <div class="ctx-divider" v-if="ctx.tab?.pinned" />
      <div class="ctx-item" @click="ctxRefresh" v-if="ctx.tab?.path === currentTab.path">刷新</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// ========== 侧边栏主模块 ==========
const mainModules = [
  { key: 'home', label: '首页', icon: 'DataBoard', subs: [{ path: '/dashboard', label: '首页', module: 'home' }] },
  { key: 'archives', label: '档案', icon: 'Folder', subs: [
    { path: '/products', label: '商品管理', module: 'products' },
    { path: '/customers', label: '客户管理', module: 'customers' },
    { path: '/customer-prices', label: '客户价格等级', module: 'customers' },
    { path: '/suppliers', label: '供应商管理', module: 'suppliers' },
    { path: '/supplier-reconciliation', label: '供应商对账', module: 'suppliers' },
    { path: '/customers/crm', label: '客户关系管理', module: 'customers' },
    { path: '/units', label: '单位管理', module: 'products' },
    { path: '/brands', label: '品牌管理', module: 'products' },
    { path: '/channels', label: '渠道管理', module: 'customers' },
    { path: '/customer-levels', label: '客户等级', module: 'customers' },
  ]},
  { key: 'purchase', label: '采购', icon: 'ShoppingCart', subs: [
    { path: '/purchases', label: '采购订单', module: 'purchases' },
    { path: '/purchase-receipts', label: '采购入库单', module: 'purchases' },
    { path: '/purchase-returns', label: '采购退货', module: 'purchases' },
    { path: '/purchase-return-deliveries', label: '采购退货出库单', module: 'purchases' },
  ]},
  { key: 'sale', label: '销售', icon: 'Sell', subs: [
    { path: '/sales', label: '销售订单', module: 'sales' },
    { path: '/sales-deliveries', label: '销售单管理', module: 'sales' },
    { path: '/return-deliveries', label: '退货单管理', module: 'sales' },
    { path: '/sales-returns', label: '销售退货', module: 'sales' },
    { path: '/salesmen', label: '业务员管理', module: 'sales' },
    { path: '/settlements', label: '交账管理', module: 'sales' },
    { path: '/monitor', label: '异常监控', module: 'sales' },
  ]},
  { key: 'promotions', label: '促销', icon: 'PriceTag', subs: [
    { path: '/promotions', label: '促销方案', module: 'promotions' },
  ]},
  { key: 'warehouse', label: '仓库', icon: 'Box', subs: [
    { path: '/inventory', label: '库存查询', module: 'inventory' },
    { path: '/transfers', label: '库存调拨', module: 'inventory' },
    { path: '/stocktaking', label: '盘点管理', module: 'inventory' },
    { path: '/vehicle-loads', label: '装车单管理', module: 'inventory' },
    { path: '/damage-reports', label: '报损单', module: 'inventory' },
    { path: '/warehouses', label: '仓库管理', module: 'warehouses' },
    { path: '/batches', label: '批次管理', module: 'batches' },
  ]},
  { key: 'finance', label: '财务', icon: 'Money', subs: [
    { path: '/finance', label: '收支管理', module: 'finance' },
    { path: '/expenses', label: '费用管理', module: 'finance' },
    { path: '/account-ledger', label: '往来账', module: 'finance' },
    { path: '/advance-payments', label: '预收付款', module: 'finance' },
    { path: '/reconciliations', label: '客户对账', module: 'finance' },
    { path: '/bank-reconciliation', label: '银行对账', module: 'finance' },
    { path: '/invoices', label: '发票管理', module: 'finance' },
  ]},
  { key: 'reports', label: '报表', icon: 'Document', subs: [
    { path: '/reports/profit', label: '利润统计', module: 'reports' },
    { path: '/reports/inventory', label: '库存汇总', module: 'reports' },
    { path: '/reports/sales-ranking', label: '销售排行', module: 'reports' },
    { path: '/reports/trend', label: '趋势图', module: 'reports' },
    { path: '/reports/sales-detail', label: '销售明细报表', module: 'reports' },
    { path: '/reports/commission', label: '提成报表', module: 'reports' },
  ]},
  { key: 'system', label: '系统', icon: 'Setting', subs: [
    { path: '/system/roles', label: '角色管理', module: 'roles' },
    { path: '/system/backup', label: '数据备份', module: 'system' },
    { path: '/system/print-templates', label: '打印模板', module: 'system' },
    { path: '/system/data-import', label: '数据导入', module: 'system' },
    { path: '/system/logs', label: '操作日志', module: 'system' },
    { path: '/audit-logs', label: '审计日志', module: 'system' },
    { path: '/system/company-config', label: '公司设置', module: 'system' },
  ]},
]

const hasMod = (key) => authStore.hasModule(key) || authStore.isAdmin
const visibleMainModules = computed(() => mainModules.filter(m => {
  if (m.key === 'home') return true
  if (m.key === 'archives') return hasMod('products') || hasMod('customers')
  if (m.key === 'warehouse') return hasMod('inventory') || hasMod('warehouses')
  if (m.key === 'system') return hasMod('roles') || hasMod('system')
  if (m.key === 'sale') return hasMod('sales') || hasMod('sale')
  if (m.key === 'purchase') return hasMod('purchases') || hasMod('purchase')
  if (m.key === 'promotions') return hasMod('promotion') || hasMod('promotions')
  return hasMod(m.key)
}))

// ========== 侧边栏交互 ==========
const activeModule = ref(null)
const hoverTop = ref(60)

const hoverModule = (item, event) => {
  if (item.subs?.length) {
    cancelHideTimer()
    activeModule.value = item.key
    if (event && event.currentTarget) {
      const el = event.currentTarget
      const top = el.offsetTop
      const height = el.offsetHeight
      hoverTop.value = top + height / 2
    }
  }
}
const toggleModule = (item) => {
  if (!item.subs?.length) {
    openTab(item.subs[0].path, item.subs[0].label)
    return
  }
  activeModule.value = activeModule.value === item.key ? null : item.key
}
const startHideTimer = () => { hideTimer = setTimeout(() => { activeModule.value = null }, 200) }
const cancelHideTimer = () => clearTimeout(hideTimer)
let hideTimer = null

const currentSubs = computed(() => {
  const m = mainModules.find(m => m.key === activeModule.value)
  if (!m) return []
  return m.subs.filter(s => !s.module || authStore.isAdmin || hasMod(s.module))
})
const currentModuleLabel = computed(() => mainModules.find(m => m.key === activeModule.value)?.label || '')

// ========== 浮层位置 - 跟随当前hover的主模块，水平居中，带边界检测 ==========
const dropdownStyle = computed(() => {
  const SUBMENU_WIDTH = 200
  const SUBMENU_MAX_HEIGHT = window.innerHeight - 80
  const estimatedHeight = Math.min(currentSubs.value.length * 40 + 42, SUBMENU_MAX_HEIGHT)

  let top = hoverTop.value

  // 边界检测：如果向上会溢出视口，则向下延伸
  if (top - estimatedHeight / 2 < 0) {
    top = 8
  } else if (top + estimatedHeight / 2 > window.innerHeight) {
    top = window.innerHeight - estimatedHeight - 8
  } else {
    top = top - estimatedHeight / 2
  }

  return {
    left: '180px',
    top: `${top}px`,
    maxHeight: `${estimatedHeight}px`,
  }
})

const isHighlight = (path) => route.path === path

// ========== 标签页 ==========
const tabs = ref([{ path: '/dashboard', title: '首页', pinned: true }])
const currentTab = computed(() => tabs.value.find(t => t.path === route.path) || tabs.value[0])
const keepAliveRoutes = computed(() => tabs.value.map(t => t.path.replace('/', '')))
const HIGHEST_TABS = 12

const openTab = (path, title) => {
  activeModule.value = null
  const exist = tabs.value.find(t => t.path === path)
  if (exist) { router.push(path); return }
  if (tabs.value.length < HIGHEST_TABS) tabs.value.push({ path, title, pinned: false })
  router.push(path)
}

const switchTab = (tab) => router.push(tab.path)
const closeTab = (tab) => {
  if (tab.pinned) return
  const idx = tabs.value.findIndex(t => t.path === tab.path)
  tabs.value.splice(idx, 1)
  if (currentTab.value.path === tab.path && tabs.value.length) router.push(tabs.value[Math.max(0, idx - 1)].path)
}
const handleTabAction = (cmd) => {
  if (cmd === 'close-others') tabs.value = tabs.value.filter(t => t.pinned || t.path === currentTab.value.path)
  else if (cmd === 'close-all') {
    const dashboardTab = tabs.value.find(t => t.path === '/dashboard')
    tabs.value = dashboardTab ? [dashboardTab] : [{ path: '/dashboard', title: '首页', pinned: true }]
    router.push('/dashboard')
  }
  else if (cmd === 'refresh') router.go(0)
}

// ========== 右键菜单 ==========
const ctx = reactive({ visible: false, x: 0, y: 0, tab: null })
const showContextMenu = (e, tab) => { ctx.visible = true; ctx.x = e.clientX; ctx.y = e.clientY; ctx.tab = tab }
const hideCtx = () => { ctx.visible = false }
const pinTab = () => { ctx.tab && (ctx.tab.pinned = !ctx.tab.pinned); hideCtx() }
const ctxCloseTab = () => { if (ctx.tab) closeTab(ctx.tab); hideCtx() }
const ctxCloseOthers = () => { tabs.value = tabs.value.filter(t => t.pinned || t.path === ctx.tab?.path); hideCtx() }
const ctxRefresh = () => { router.go(0); hideCtx() }

// ========== 路由监听 ==========
watch(() => route.path, (p) => {
  if (p === '/login') return
  const exist = tabs.value.find(t => t.path === p)
  const title = route.meta?.title || '未命名'
  if (!exist && tabs.value.length < HIGHEST_TABS) tabs.value.push({ path: p, title, pinned: false })
})

onMounted(() => {
  document.addEventListener('click', hideCtx)
  document.addEventListener('keydown', e => {
    if (e.altKey && e.key >= '1' && e.key <= '9') {
      const t = tabs.value[parseInt(e.key) - 1]
      if (t) switchTab(t)
    }
  })
})
onUnmounted(() => {
  document.removeEventListener('click', hideCtx)
  clearTimeout(hideTimer)
})

const logout = () => { authStore.logout(); router.push('/login') }
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #f0f2f5;
}

/* ===== 侧边栏 ===== */
.sidebar {
  width: 180px;
  flex-shrink: 0;
  background: linear-gradient(180deg, #1f2d3d 0%, #1a253a 100%);
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255,255,255,0.06);
}

.logo {
  height: 56px;
  line-height: 56px;
  text-align: center;
  font-size: 20px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 3px;
  background: rgba(0,0,0,0.2);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.nav-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}
.nav-list::-webkit-scrollbar { width: 0 }

.nav-item {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  color: rgba(255,255,255,0.55);
  cursor: pointer;
  font-size: 13px;
  gap: 10px;
  transition: all 0.15s;
  border-left: 3px solid transparent;
  user-select: none;
}
.nav-item:hover, .nav-item.active {
  background: rgba(64,158,255,0.15);
  color: #fff;
  border-left-color: #409eff;
}
.nav-item .el-icon { font-size: 16px; flex-shrink: 0 }
.nav-label { flex: 1 }
.arrow { font-size: 12px; opacity: 0 }
.nav-item:hover .arrow, .nav-item.active .arrow { opacity: 1 }

/* ===== 侧边栏底部 ===== */
.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.user-badge { display: flex; align-items: center; gap: 8px }
.logout-btn { margin-left: auto; color: rgba(255,255,255,0.4); cursor: pointer; font-size: 16px; padding: 2px; }
.logout-btn:hover { color: #f56c6c }
.user-name { font-size: 12px; color: #fff; font-weight: 500; line-height: 1.2 }
.user-role { font-size: 10px; color: rgba(255,255,255,0.4) }

/* ===== 主内容区 ===== */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

/* ===== 顶部标签栏 - 悬浮 ===== */
.topbar {
  height: 44px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: stretch;
  padding: 0 8px;
  gap: 0;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.tabs-wrap {
  display: flex;
  overflow-x: auto;
  flex: 1;
  align-items: center;
  gap: 2px;
}
.tabs-wrap::-webkit-scrollbar { height: 0 }

.top-tab {
  display: flex;
  align-items: center;
  padding: 0 12px;
  height: 32px;
  border-radius: 6px 6px 0 0;
  cursor: pointer;
  font-size: 12px;
  color: #666;
  background: #f5f5f5;
  white-space: nowrap;
  transition: all 0.15s;
  border: 1px solid transparent;
  border-bottom: none;
  gap: 6px;
}
.top-tab:hover { background: #e8f0fe; color: #409eff }
.top-tab.active {
  background: #f0f2f5;
  color: #409eff;
  font-weight: 600;
  border-color: #e8e8e8;
  box-shadow: 0 -1px 2px rgba(0,0,0,0.05);
}
.top-tab.pinned { background: #fff8f0; color: #e6a23c }
.tab-label { max-width: 100px; overflow: hidden; text-overflow: ellipsis }
.tab-close { font-size: 14px; line-height: 1; opacity: 0.6; padding: 0 2px }
.tab-close:hover { opacity: 1; color: #f56c6c }

.topbar-actions {
  display: flex;
  align-items: center;
  padding: 0 4px;
}
.more-btn {
  cursor: pointer;
  padding: 4px 8px;
  font-size: 16px;
  color: #999;
  letter-spacing: 2px;
}
.more-btn:hover { color: #409eff }

/* ===== 内容区 ===== */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}
.content-area::-webkit-scrollbar { width: 6px }
.content-area::-webkit-scrollbar-track { background: transparent }
.content-area::-webkit-scrollbar-thumb { background: #dcdfe6; border-radius: 3px }

/* ===== 子模块下拉 - 跟随hover的主模块水平居中 ===== */
.submenu-dropdown {
  position: fixed;
  left: 180px;
  width: 200px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18), 0 0 1px rgba(0,0,0,0.1);
  z-index: 999;
  overflow: hidden;
  overflow-y: auto;
}
.submenu-header {
  padding: 12px 16px 10px;
  font-size: 13px;
  font-weight: 700;
  color: #303133;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  letter-spacing: 0.5px;
}
.submenu-items { padding: 6px 0 }
.submenu-item {
  padding: 9px 16px;
  font-size: 13px;
  color: #444;
  cursor: pointer;
  transition: all 0.12s;
  border-left: 3px solid transparent;
}
.submenu-item:hover {
  background: #f0f7ff;
  color: #409eff;
  border-left-color: #409eff;
}
.submenu-item.highlight {
  background: #ecf5ff;
  color: #409eff;
  border-left-color: #409eff;
  font-weight: 500;
}

/* ===== 右键菜单 ===== */
.ctx-menu {
  position: fixed;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  z-index: 9999;
  padding: 4px 0;
  min-width: 130px;
}
.ctx-item {
  padding: 8px 14px;
  font-size: 12px;
  color: #444;
  cursor: pointer;
}
.ctx-item:hover { background: #f0f7ff; color: #409eff }
.ctx-divider { height: 1px; background: #f0f0f0; margin: 4px 0 }

/* ===== 动画 ===== */
.dropdown-fade-enter-active, .dropdown-fade-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}
.dropdown-fade-enter-from, .dropdown-fade-leave-to {
  opacity: 0;
}
</style>
