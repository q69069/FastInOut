<template>
  <div class="page">
    <div class="header">
      <div class="title">工作台</div>
    </div>

    <div class="content">
      <!-- 业务操作 -->
      <div v-if="hasAny(['sales','customers','purchases'])" class="section">
        <div class="section-title">业务操作</div>
        <div class="grid">
          <div v-if="hasModule('sales')" class="grid-item" @click="$router.push('/order')">
            <div class="item-icon orange"><van-icon name="orders-o" /></div>
            <span class="item-label">快速下单</span>
          </div>
          <div v-if="hasModule('customers')" class="grid-item" @click="$router.push('/customers')">
            <div class="item-icon blue"><van-icon name="friends-o" /></div>
            <span class="item-label">客户管理</span>
          </div>
          <div v-if="hasModule('customers')" class="grid-item" @click="$router.push('/visit')">
            <div class="item-icon green"><van-icon name="location-o" /></div>
            <span class="item-label">拜访记录</span>
          </div>
          <div v-if="hasModule('customers')" class="grid-item" @click="$router.push('/checkin')">
            <div class="item-icon teal"><van-icon name="clock-o" /></div>
            <span class="item-label">门店打卡</span>
          </div>
          <div v-if="hasModule('purchases')" class="grid-item" @click="$router.push('/purchase')">
            <div class="item-icon purple"><van-icon name="shopping-cart-o" /></div>
            <span class="item-label">采购开单</span>
          </div>
          <div v-if="hasModule('purchases')" class="grid-item" @click="$router.push('/purchase-return-dlv')">
            <div class="item-icon red"><van-icon name="replay" /></div>
            <span class="item-label">采购退货</span>
          </div>
        </div>
      </div>

      <!-- 车销流程 -->
      <div v-if="hasAny(['inventory','sales'])" class="section">
        <div class="section-title">车销流程</div>
        <div class="grid">
          <div v-if="hasModule('inventory')" class="grid-item" @click="$router.push('/vehicle-load')">
            <div class="item-icon orange"><van-icon name="logistics" /></div>
            <span class="item-label">装车</span>
          </div>
          <div v-if="hasModule('sales')" class="grid-item" @click="$router.push('/vehicle-sales')">
            <div class="item-icon blue"><van-icon name="shopping-cart-o" /></div>
            <span class="item-label">车销开单</span>
          </div>
          <div v-if="hasModule('sales')" class="grid-item" @click="$router.push('/settlement')">
            <div class="item-icon green"><van-icon name="balance-o" /></div>
            <span class="item-label">交账</span>
          </div>
        </div>
      </div>

      <!-- 库存仓储 -->
      <div v-if="hasModule('inventory')" class="section">
        <div class="section-title">库存仓储</div>
        <div class="grid">
          <div class="grid-item" @click="$router.push('/inventory')">
            <div class="item-icon blue"><van-icon name="cluster-o" /></div>
            <span class="item-label">库存查询</span>
          </div>
          <div class="grid-item" @click="$router.push('/transfer')">
            <div class="item-icon teal"><van-icon name="exchange" /></div>
            <span class="item-label">调拨</span>
          </div>
          <div class="grid-item" @click="$router.push('/check')">
            <div class="item-icon green"><van-icon name="search" /></div>
            <span class="item-label">盘点</span>
          </div>
          <div class="grid-item" @click="$router.push('/loss-report')">
            <div class="item-icon red"><van-icon name="warning-o" /></div>
            <span class="item-label">报损</span>
          </div>
          <div class="grid-item" @click="$router.push('/turnover')">
            <div class="item-icon purple"><van-icon name="chart-trending-o" /></div>
            <span class="item-label">周转率</span>
          </div>
        </div>
      </div>

      <!-- 档案管理 -->
      <div v-if="hasAny(['products','customers','suppliers'])" class="section">
        <div class="section-title">档案管理</div>
        <div class="grid">
          <div v-if="hasModule('suppliers')" class="grid-item" @click="$router.push('/supplier')">
            <div class="item-icon orange"><van-icon name="shop-o" /></div>
            <span class="item-label">供应商</span>
          </div>
          <div v-if="hasModule('products')" class="grid-item" @click="$router.push('/brand')">
            <div class="item-icon blue"><van-icon name="flag-o" /></div>
            <span class="item-label">品牌管理</span>
          </div>
          <div v-if="hasModule('customers')" class="grid-item" @click="$router.push('/channel')">
            <div class="item-icon green"><van-icon name="cluster-o" /></div>
            <span class="item-label">渠道管理</span>
          </div>
          <div v-if="hasModule('customers')" class="grid-item" @click="$router.push('/customer-level')">
            <div class="item-icon teal"><van-icon name="user-o" /></div>
            <span class="item-label">客户等级</span>
          </div>
        </div>
      </div>

      <!-- 财务报表 -->
      <div v-if="hasModule('finance')" class="section">
        <div class="section-title">财务报表</div>
        <div class="grid">
          <div class="grid-item" @click="$router.push('/receivables')">
            <div class="item-icon orange"><van-icon name="balance-o" /></div>
            <span class="item-label">应收应付</span>
          </div>
          <div class="grid-item" @click="$router.push('/payments')">
            <div class="item-icon blue"><van-icon name="paid" /></div>
            <span class="item-label">收付款</span>
          </div>
          <div class="grid-item" @click="$router.push('/invoice')">
            <div class="item-icon green"><van-icon name="notes-o" /></div>
            <span class="item-label">发票管理</span>
          </div>
        </div>
      </div>

      <!-- 审核中心 -->
      <div v-if="hasAny(['sales','purchases'])" class="section">
        <div class="section-title">审核</div>
        <div class="grid">
          <div class="grid-item" @click="$router.push('/approve')">
            <div class="item-icon orange"><van-icon name="passed" /></div>
            <span class="item-label">审核中心</span>
          </div>
        </div>
      </div>

      <!-- 系统管理 -->
      <div v-if="hasAny(['employees','roles','reports','promotions','system'])" class="section">
        <div class="section-title">系统管理</div>
        <div class="grid">
          <div v-if="hasModule('employees')" class="grid-item" @click="$router.push('/employee')">
            <div class="item-icon blue"><van-icon name="manager-o" /></div>
            <span class="item-label">员工管理</span>
          </div>
          <div v-if="hasModule('roles')" class="grid-item" @click="$router.push('/roles')">
            <div class="item-icon teal"><van-icon name="shield-o" /></div>
            <span class="item-label">角色权限</span>
          </div>
          <div v-if="hasModule('reports')" class="grid-item" @click="$router.push('/reports')">
            <div class="item-icon green"><van-icon name="description" /></div>
            <span class="item-label">报表中心</span>
          </div>
          <div v-if="hasModule('promotions')" class="grid-item" @click="$router.push('/promotion')">
            <div class="item-icon purple"><van-icon name="coupon-o" /></div>
            <span class="item-label">促销管理</span>
          </div>
          <div v-if="hasModule('system')" class="grid-item" @click="$router.push('/messages')">
            <div class="item-icon orange"><van-icon name="comment-o" /></div>
            <span class="item-label">消息中心</span>
          </div>
        </div>
      </div>

      <!-- 无权限提示 -->
      <van-empty v-if="allSectionsHidden" description="当前账号暂无功能权限" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const hasModule = (key) => authStore.hasModule(key)

const hasAny = (keys) => keys.some(k => authStore.hasModule(k))

const allSectionsHidden = computed(() => {
  const cats = ['sales', 'customers', 'purchases', 'inventory', 'products', 'suppliers', 'finance', 'employees', 'roles', 'reports', 'promotions', 'system']
  return !cats.some(c => authStore.hasModule(c))
})
</script>

<style scoped>
.page { min-height: 100vh; background: #f7f8fa; padding-bottom: 20px; }
.header { background: linear-gradient(135deg, #1989fa, #396bec); padding: 16px; color: #fff; }
.title { font-size: 18px; font-weight: bold; }
.content { padding: 12px; }
.section { margin-bottom: 16px; }
.section-title { font-size: 13px; font-weight: bold; color: #666; margin-bottom: 8px; padding-left: 4px; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.grid-item {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  background: #fff; border-radius: 10px; padding: 16px 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.item-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; color: #fff; }
.item-icon.orange { background: linear-gradient(135deg, #ff6b35, #ff9a56); }
.item-icon.blue { background: linear-gradient(135deg, #1989fa, #396bec); }
.item-icon.green { background: linear-gradient(135deg, #07c160, #4cd964); }
.item-icon.teal { background: linear-gradient(135deg, #00bcd4, #26c6da); }
.item-icon.purple { background: linear-gradient(135deg, #9c27b0, #ba68c8); }
.item-icon.red { background: linear-gradient(135deg, #f44336, #e57373); }
.item-label { font-size: 12px; color: #333; }
</style>