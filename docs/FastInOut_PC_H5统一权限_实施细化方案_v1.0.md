# FastInOut PC端 + H5端 统一权限 — 实施细化方案

> 📅 编制日期：2026-05-03
> 👤 编制：Hermes小A
> 📖 依据：[PC+H5统一权限方案 v20260502] + [综合方案 v3.0] 合并分析

---

## 一、权限架构总览

```
┌──────────────────────────────────────────────────────────────┐
│                     统一权限架构                              │
│                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐   │
│  │ PC端    │    │ H5管理员 │    │ H5业务员 │    │ 微信H5  │   │
│  │ Electron│    │ Vue3    │    │ Vant极简 │    │ Vant    │   │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘   │
│       └──────────────┼──────────────┼──────────────┘        │
│                      │  JWT Token                            │
│              ┌───────▼────────┐                              │
│              │  Auth Middleware│  ← 统一鉴权入口              │
│              │  提取：user_id │                              │
│              │  + role_ids     │                              │
│              │  + warehouse_ids│                              │
│              │  + route_ids    │                              │
│              └───────┬────────┘                              │
│                      │                                       │
│        ┌─────────────┼─────────────┐                        │
│        ▼             ▼             ▼                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                    │
│  │模块权限  │ │操作权限  │ │数据权限  │                    │
│  │能进哪个   │ │能做什么   │ │能看什么   │                    │
│  │菜单/页面  │ │增删改查   │ │谁的数据   │                    │
│  └──────────┘ └──────────┘ └──────────┘                    │
└──────────────────────────────────────────────────────────────┘
```

**三层权限模型：**

| 层级 | 检查内容 | 示例 |
|------|---------|------|
| **模块权限** | 能否进入该页面/菜单 | 库管能否看"财务管理" |
| **操作权限** | 能否执行增/删/改/查/审核/导出 | 业务员能否删除销售订单 |
| **数据权限** | 能看到哪些数据 | 业务员只能看自己路线客户 |

---

## 二、核心原则（对齐两份文档）

| # | 原则 | 说明 |
|---|------|------|
| 1 | **PC/H5模块一致** | 后续所有新模块，PC和H5同步开发 |
| 2 | **一账号多角色** | 一个账号可绑定多个角色，权限取**并集** |
| 3 | **后端统一鉴权** | 所有API请求经统一中间件校验 |
| 4 | **前端动态渲染** | PC/H5根据权限动态显示菜单/Tab/按钮 |
| 5 | **路由+仓库双隔离** | 业务员可见数据 = 绑定路线 + 绑定仓库 |
| 6 | **细粒度可配置** | 管理员可逐角色勾选模块/操作权限 |

---

## 三、权限数据模型设计

### 3.1 角色定义（对齐综合方案v3.0）

| 角色 | role_key | 说明 | 数据范围 |
|------|:---:|------|----------|
| **老板/管理员** | `admin` | 全部功能+系统设置 | 全部数据 |
| **主管/文员** | `supervisor` | 档案+采购+销售+报表 | 按仓库/路线可限制 |
| **业务员** | `sales` | 8窗口+自己路线 | 仅自己路线客户 |
| **财务** | `finance` | 财务+报表+对账 | 全部财务数据 |
| **库管** | `warehouse` | 仓库+出入库+盘点 | 绑定仓库 |

### 3.2 角色-模块映射表（PC端14个views / H5端5个Tab）

| 模块(PC views) | H5 Tab | admin | supervisor | sales | finance | warehouse |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 首页(看板+快捷入口) | 首页 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 客户(列表/详情/联系人/价格/拜访) | 客户 | ✅ | ✅ | ✅(自己) | ✅(查) | ❌ |
| 销售(订单/退货) | 销售 | ✅ | ✅ | ✅(自己) | ❌ | ❌ |
| 库存(查询/入库/出库/调拨/盘点/报损) | 库存 | ✅ | ✅(查) | ✅(查) | ❌ | ✅ |
| 采购(订单) | — | ✅ | ✅ | ❌ | ❌ | ❌ |
| 供应商(管理) | — | ✅ | ✅ | ❌ | ❌ | ❌ |
| 财务(收/付款/对账) | — | ✅ | ❌ | ❌ | ✅ | ❌ |
| 员工(管理) | — | ✅ | ❌ | ❌ | ❌ | ❌ |
| 角色(权限) | — | ✅ | ❌ | ❌ | ❌ | ❌ |
| 商品(管理/分类/单位) | — | ✅ | ✅ | ❌ | ❌ | ✅(查) |
| 仓库(管理) | — | ✅ | ✅(查) | ❌ | ❌ | ✅ |
| 批次(管理) | — | ✅ | ✅(查) | ❌ | ❌ | ✅ |
| 促销(营销活动) | — | ✅ | ✅ | ✅(查) | ❌ | ❌ |
| 报表(统计) | — | ✅ | ✅(自) | ✅(自) | ✅ | ❌ |
| 系统(公司设置) | — | ✅ | ❌ | ❌ | ❌ | ❌ |
| — | 我的(业绩/收款/工具) | — | — | ✅ | — | — |

> **H5 Tab 说明：** 5个Tab对应核心模块，其中"我的"Tab是H5特有聚合页（业绩统计+收款付款+设置退出）。

### 3.3 数据库设计

#### 3.3.1 角色表 (roles) — 新建

```sql
CREATE TABLE role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_key VARCHAR(20) UNIQUE NOT NULL,   -- admin / supervisor / sales / finance / warehouse
    name VARCHAR(20) NOT NULL,               -- 老板/主管/业务员/财务/库管
    description TEXT,
    is_system BOOLEAN DEFAULT 1,             -- 系统角色不可删除
    sort_order INTEGER DEFAULT 0,
    status VARCHAR(10) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 预置5个系统角色
INSERT INTO role (role_key, name, is_system) VALUES
('admin',        '老板/管理员', 1),
('supervisor',   '主管/文员',   1),
('sales',        '业务员',      1),
('finance',      '财务',        1),
('warehouse',    '库管',        1);
```

#### 3.3.2 模块表 (modules) — 新建（统一PC/H5模块清单）

```sql
CREATE TABLE module (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_key VARCHAR(30) UNIQUE NOT NULL,  -- customers / sales / inventory / finance ...
    name VARCHAR(30) NOT NULL,               -- 客户管理 / 销售订单 / ...
    parent_id INTEGER,                        -- 上级模块ID（支持二级）
    module_type VARCHAR(10) DEFAULT 'page',  -- page(菜单页面) / action(操作) / api(接口)
    pc_view BOOLEAN DEFAULT 1,               -- PC端是否显示
    h5_tab VARCHAR(20),                       -- 对应H5 Tab
    sort_order INTEGER DEFAULT 0,
    icon VARCHAR(30),
    path VARCHAR(100),                        -- 前端路由路径
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.3.3 角色-模块权限表 (role_module_permissions)

```sql
CREATE TABLE role_module_permission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
    can_view BOOLEAN DEFAULT 1,              -- 可见
    can_create BOOLEAN DEFAULT 0,            -- 新增
    can_edit BOOLEAN DEFAULT 0,              -- 编辑
    can_delete BOOLEAN DEFAULT 0,            -- 删除
    can_audit BOOLEAN DEFAULT 0,             -- 审核
    can_export BOOLEAN DEFAULT 0,            -- 导出
    data_scope VARCHAR(20) DEFAULT 'all',    -- all / self / route / warehouse / none
    UNIQUE(role_id, module_id)
);
```

**data_scope 说明：**

| data_scope | 含义 | 适用角色 |
|:---|------|------|
| `all` | 全部数据 | admin |
| `route` | 绑定路线数据 | sales |
| `warehouse` | 绑定仓库数据 | warehouse |
| `self` | 仅自己创建的 | employee |
| `none` | 不可查看 | 无权限角色 |

#### 3.3.4 操作权限表 (operation_permissions) — 细粒度操作

```sql
CREATE TABLE operation_permission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    operation_key VARCHAR(50) NOT NULL,      -- customers:delete / sales_order:audit / product:export
    allowed BOOLEAN DEFAULT 0,
    UNIQUE(role_id, operation_key)
);
```

**预置操作清单（按模块）：**

| 模块 | 操作key | 说明 | admin | supervisor | sales | finance | warehouse |
|------|------|------|:---:|:---:|:---:|:---:|:---:|
| 客户 | `customers:create` | 新增客户 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 客户 | `customers:edit` | 编辑客户 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 客户 | `customers:delete` | 删除客户 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 客户 | `customers:export` | 导出客户 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 销售 | `sales:create` | 创建订单 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 销售 | `sales:edit` | 编辑订单 | ✅ | ✅ | ✅(自己) | ❌ | ❌ |
| 销售 | `sales:delete` | 删除订单 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 销售 | `sales:audit` | 审核订单 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 库存 | `inventory:adjust` | 库存调整 | ✅ | ❌ | ❌ | ❌ | ✅ |
| 库存 | `inventory:transfer` | 调拨 | ✅ | ✅ | ❌ | ❌ | ✅ |
| 仓库 | `warehouse:manage` | 仓库管理 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 财务 | `finance:view_all` | 查看全部财务 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 员工 | `employee:manage` | 员工管理 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 角色 | `role:assign` | 分配权限 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 系统 | `system:config` | 系统设置 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 促销 | `promotion:create` | 创建促销 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 报表 | `report:view_all` | 看全部报表 | ✅ | ✅ | ❌ | ✅ | ❌ |

#### 3.3.5 员工-角色关联表

```sql
-- 已有 employee 表增加角色字段（综合方案v3.0已设计）
-- employee.role → 单角色（保留兼容）
-- 新增多对多关联表

CREATE TABLE employee_role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    UNIQUE(employee_id, role_id)
);
```

#### 3.3.6 路线权限表（综合方案v3.0已有）

```sql
-- route 表 — 已有
-- employee_route — 已有
-- warehouse_route — 已有
-- employee_warehouse — 已有
-- customer.route_id / salesman_ids / default_warehouse_id — 已有
```

---

## 四、后端权限服务设计

### 4.1 JWT Token 结构

```python
# 登录成功后颁发 Token
token_payload = {
    "sub": employee_id,
    "name": "张三",
    "phone": "138xxxx",
    "roles": ["sales", "warehouse"],          # 多角色
    "warehouse_ids": [1, 2],                   # 绑定仓库
    "route_ids": [1, 3, 5],                    # 绑定路线
    "bypass_audit": {"so": False, "po": False}, # 免审核权限
    "exp": 1735689600,                         # 过期时间
    "iat": 1735603200                           # 签发时间
}
```

### 4.2 权限中间件 (FastAPI Dependency)

```python
# auth/permissions.py

from fastapi import Depends, HTTPException
from functools import wraps

class PermissionChecker:
    """统一权限检查器"""
    
    def __init__(self, module_key: str = None, operation: str = None):
        self.module_key = module_key
        self.operation = operation
    
    async def __call__(self, request: Request, current_user = Depends(get_current_user)):
        # 1. 模块权限检查
        if self.module_key:
            allowed_modules = get_user_modules(current_user.role_ids)
            if self.module_key not in allowed_modules:
                raise HTTPException(403, "无权访问此模块")
        
        # 2. 操作权限检查
        if self.operation:
            if not check_operation(current_user.role_ids, self.operation):
                raise HTTPException(403, "无权执行此操作")
        
        # 3. 返回用户上下文（含数据范围）
        return UserContext(
            employee_id=current_user.id,
            roles=current_user.role_ids,
            data_scope=get_data_scope(current_user.role_ids, self.module_key),
            warehouse_ids=current_user.warehouse_ids,
            route_ids=current_user.route_ids
        )

# 使用示例（路由装饰器）
@router.get("/api/sales/orders", dependencies=[Depends(PermissionChecker("sales"))])
async def list_orders(user_ctx: UserContext = Depends()):
    # user_ctx.data_scope 在查询时过滤数据
    pass

@router.post("/api/sales/orders", dependencies=[Depends(PermissionChecker("sales", "sales:create"))])
async def create_order(data: OrderCreate, user_ctx: UserContext = Depends()):
    pass
```

### 4.3 权限查询服务

```python
# services/permission_service.py

class PermissionService:
    """权限查询服务（含缓存）"""
    
    @staticmethod
    def get_user_modules(role_ids: list[int]) -> set[str]:
        """获取用户所有可见模块（多角色取并集）"""
        modules = set()
        for role_id in role_ids:
            perms = cache.get(f"role:{role_id}:modules")
            if not perms:
                perms = db.query(RoleModulePermission).filter_by(
                    role_id=role_id, can_view=True
                ).all()
                cache.set(f"role:{role_id}:modules", perms, ttl=300)
            modules.update(p.module_key for p in perms)
        return modules
    
    @staticmethod
    def get_data_scope(role_ids: list[int], module_key: str) -> str:
        """获取数据范围（取最宽松）"""
        # all > route > warehouse > self > none
        priority = {"all": 5, "route": 4, "warehouse": 3, "self": 2, "none": 1}
        scopes = []
        for role_id in role_ids:
            perm = db.query(RoleModulePermission).filter_by(
                role_id=role_id, module_id=get_module_id(module_key)
            ).first()
            if perm:
                scopes.append(perm.data_scope)
        return max(scopes, key=lambda s: priority.get(s, 0)) if scopes else "none"
```

### 4.4 登录API

```
POST /api/auth/login
 Body: { "phone": "138xxxx", "password": "xxx" }

Response:
{
  "token": "eyJ...",
  "user": {
    "id": 1,
    "name": "张三",
    "roles": [
      {"role_key": "sales", "name": "业务员"},
      {"role_key": "warehouse", "name": "库管"}
    ],
    "modules": ["customers", "sales", "inventory", "warehouse", "batches", ...],
    "permissions": {
      "customers": {"view": true, "create": false, "edit": false, "delete": false},
      "sales":     {"view": true, "create": true, "edit": true,  "delete": false},
      "inventory": {"view": true, "create": false, ...},
      ...
    },
    "operations": ["sales:create", "sales:edit", "inventory:transfer", ...],
    "warehouse_ids": [1, 2],
    "route_ids": [1, 3, 5]
  }
}
```

### 4.5 权限查询API

```
GET /api/auth/permissions
返回：当前用户的完整权限信息（模块+操作+数据范围）
  前端登录后调用一次，存入 Pinia Store
```

```
GET /api/auth/roles
返回：所有角色列表 + 每个角色的模块/操作权限（仅admin可用）

PUT /api/auth/roles/{role_id}/permissions
 Body: { "modules": [...], "operations": [...] }
  管理员配置角色权限
```

---

## 五、PC端权限改造实施

### 5.1 登录流程

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ 登录页   │────→│ 调API   │────→│ 存Store  │────→│ 渲染UI   │
│ 手机号   │     │ /auth/  │     │ Pinia   │     │ 动态菜单  │
│ +密码    │     │ login   │     │ authStore│     │ +动态路由 │
└─────────┘     └─────────┘     └─────────┘     └─────────┘

authStore 存储：
  - user (基本信息)
  - roles (角色列表)
  - modules (可见模块列表)
  - permissions (模块→操作权限映射)
  - operations (可执行操作集合)
  - warehouse_ids / route_ids (数据范围)
```

### 5.2 动态菜单渲染

```typescript
// stores/auth.ts
export const useAuthStore = defineStore('auth', {
  state: () => ({
    modules: [] as string[],        // ['customers', 'sales', 'inventory', ...]
    permissions: {} as Record<string, ModulePermissions>,
  }),
  getters: {
    // 根据权限过滤菜单
    visibleMenuItems: (state) => {
      return allMenuItems.filter(item => 
        state.modules.includes(item.moduleKey)
      )
    }
  }
})
```

**侧边栏菜单渲染逻辑：**

```vue
<!-- Sidebar.vue -->
<template>
  <div class="sidebar" @mouseenter="expandMenu" @mouseleave="collapseMenu">
    <!-- 只渲染有权限的菜单项 -->
    <div v-for="item in visibleMenuItems" :key="item.key" class="menu-icon">
      <el-tooltip :content="item.label">
        <el-icon><component :is="item.icon" /></el-icon>
      </el-tooltip>
    </div>
  </div>
  
  <!-- 悬停弹出子菜单 -->
  <div v-if="expanded" class="submenu-panel">
    <div v-for="sub in currentSubItems" :key="sub.key">
      {{ sub.label }}
    </div>
  </div>
</template>
```

**菜单配置（14个views全覆盖）：**

```typescript
// config/menu.config.ts
export const menuConfig = [
  { key: 'home',      label: '首页',   icon: HomeIcon,      moduleKey: 'home',      h5Tab: '首页' },
  { key: 'customers', label: '客户',   icon: UserIcon,      moduleKey: 'customers', h5Tab: '客户' },
  { key: 'sales',     label: '销售',   icon: ShoppingIcon,  moduleKey: 'sales',     h5Tab: '销售' },
  { key: 'inventory', label: '库存',   icon: BoxIcon,       moduleKey: 'inventory', h5Tab: '库存' },
  { key: 'purchases', label: '采购',   icon: TruckIcon,     moduleKey: 'purchases', h5Tab: null },
  { key: 'suppliers', label: '供应商', icon: StoreIcon,      moduleKey: 'suppliers', h5Tab: null },
  { key: 'finance',   label: '财务',   icon: MoneyIcon,     moduleKey: 'finance',   h5Tab: null },
  { key: 'employees', label: '员工',   icon: PeopleIcon,    moduleKey: 'employees', h5Tab: null },
  { key: 'roles',     label: '角色',   icon: ShieldIcon,    moduleKey: 'roles',     h5Tab: null },
  { key: 'products',  label: '商品',   icon: GoodsIcon,     moduleKey: 'products',  h5Tab: null },
  { key: 'warehouses',label: '仓库',   icon: BuildingIcon,  moduleKey: 'warehouses',h5Tab: null },
  { key: 'batches',   label: '批次',   icon: BarcodeIcon,   moduleKey: 'batches',   h5Tab: null },
  { key: 'promotions',label: '促销',   icon: GiftIcon,      moduleKey: 'promotions',h5Tab: null },
  { key: 'reports',   label: '报表',   icon: ChartIcon,     moduleKey: 'reports',   h5Tab: null },
  { key: 'system',    label: '系统',   icon: SettingIcon,   moduleKey: 'system',    h5Tab: null },
]
```

### 5.3 动态路由守卫

```typescript
// router/index.ts
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 不需要权限的页面（登录页、404）
  if (to.meta.public) return next()
  
  // 检查模块权限
  const moduleKey = to.meta.moduleKey as string
  if (moduleKey && !authStore.modules.includes(moduleKey)) {
    return next('/403')  // 无权限页面
  }
  
  next()
})
```

### 5.4 页面内操作按钮权限

```vue
<!-- 销售订单列表页 -->
<template>
  <!-- 新增按钮：检查 sales:create -->
  <el-button v-if="can('sales:create')" @click="createOrder">新增订单</el-button>
  
  <!-- 删除按钮：检查 sales:delete -->
  <el-button v-if="can('sales:delete')" @click="deleteOrder(row)">删除</el-button>
  
  <!-- 审核按钮：检查 sales:audit（结合数据权限） -->
  <el-button v-if="can('sales:audit')" @click="auditOrder(row)">审核</el-button>
  
  <!-- 导出按钮 -->
  <el-button v-if="can('customers:export')">导出</el-button>
</template>

<script setup>
// 全局权限检查函数
const can = (operation: string): boolean => {
  return authStore.operations.includes(operation)
}
</script>
```

### 5.5 标签页权限

```typescript
// 打开标签页时检查权限
function openTab(menuItem) {
  if (!authStore.modules.includes(menuItem.moduleKey)) {
    ElMessage.warning('无权访问此模块')
    return
  }
  tabStore.addTab(menuItem)
}
```

---

## 六、H5端权限改造实施

### 6.1 H5端架构差异

| 维度 | PC端 | H5端 |
|------|------|------|
| 导航 | 侧边栏悬停展开 | 底部Tab（5个） |
| 布局 | 多标签页 | 单页+返回 |
| 菜单 | 14个views全展示 | 5个Tab + 子页面 |
| 权限 | 菜单显隐+路由守卫 | Tab显隐+页面内按钮 |

### 6.2 底部Tab动态渲染

```typescript
// H5 Tab配置（5个Tab）
const h5TabConfig = [
  { key: 'home',      label: '首页', icon: 'home',    moduleKey: 'home' },
  { key: 'customers', label: '客户', icon: 'user',    moduleKey: 'customers' },
  { key: 'sales',     label: '销售', icon: 'cart',    moduleKey: 'sales' },
  { key: 'inventory', label: '库存', icon: 'box',     moduleKey: 'inventory' },
  { key: 'profile',   label: '我的', icon: 'profile', moduleKey: 'profile' },
]

// 根据权限过滤Tab
const visibleTabs = computed(() => {
  return h5TabConfig.filter(tab => {
    // '我的' Tab：只要有任意非admin模块可见就显示
    if (tab.key === 'profile') {
      return authStore.modules.length > 0
    }
    return authStore.modules.includes(tab.moduleKey)
  })
})
```

```vue
<!-- H5底部导航 -->
<van-tabbar v-model="activeTab">
  <van-tabbar-item 
    v-for="tab in visibleTabs" 
    :key="tab.key"
    :icon="tab.icon"
  >
    {{ tab.label }}
  </van-tabbar-item>
</van-tabbar>
```

### 6.3 业务员手机端（8窗口适配）

> 业务员只有 `sales` 角色 → 进H5只看到自己路线的客户+订单。

| 窗口 | H5实现 | 权限过滤 |
|------|--------|----------|
| 📋 待办订单 | Tab: 首页 → 待办卡片 | 只看自己路线的待处理订单 |
| 🗺️ 拜访计划 | Tab: 客户 → 拜访计划 | 只看自己路线客户 |
| 📸 门店打卡 | Tab: 客户 → 打卡页 | GPS+定位检测 |
| 🛒 快速下单 | Tab: 销售 → 下单页 | 自动带入绑定路线客户 |
| 🖨️ 打印小票 | 下单成功 → 打印按钮 | Web Bluetooth API |
| 📊 业绩查看 | Tab: 我的 → 业绩 | 仅看自己 |
| 📦 查库存 | Tab: 库存 → 查询 | 仅看绑定仓库 |
| 💰 应收查询 | Tab: 我的 → 应收 | 仅看自己客户 |

### 6.4 微信H5终端下单

**权限特点：** 无账号体系，手机号+验证码认证。

| 阶段 | 权限处理 |
|------|----------|
| 首次访问 | 手机号验证 → 自动创建客户（若有匹配手机号则关联） |
| 下单 | 自动关联客户绑定的路线+业务员+默认仓库 |
| 查看商品 | 只看启用状态商品 + 客户等级价 |
| 查看价格 | 仅看售价，不看进价 |
| 订单追踪 | 只看自己手机号对应的订单 |

### 6.5 H5路由守卫

```typescript
// H5 router
router.beforeEach((to, from, next) => {
  // 微信H5入口：手机号验证后放行
  if (to.meta.wechatEntry) return next()
  
  // 内部H5：检查模块权限
  const moduleKey = to.meta.moduleKey as string
  if (!authStore.modules.includes(moduleKey)) {
    // 重定向到首页 + Toast提示
    showToast('无权访问')
    return next('/home')
  }
  
  next()
})
```

---

## 七、数据权限隔离实现

### 7.1 数据范围过滤

```python
# services/data_filter.py

class DataFilter:
    """数据权限过滤器"""
    
    @staticmethod
    def apply_scope(query, model, user_ctx: UserContext, scope_field: str = None):
        """根据 data_scope 自动添加 WHERE 条件"""
        
        scope = user_ctx.data_scope
        
        if scope == 'all':
            return query  # 老板：无过滤
        
        elif scope == 'route':
            # 业务员：只看自己路线的数据
            return query.filter(
                model.route_id.in_(user_ctx.route_ids)
            )
        
        elif scope == 'warehouse':
            # 库管：只看绑定仓库的数据
            return query.filter(
                model.warehouse_id.in_(user_ctx.warehouse_ids)
            )
        
        elif scope == 'self':
            # 普通员工：只看自己创建的
            return query.filter(
                model.created_by == user_ctx.employee_id
            )
        
        elif scope == 'none':
            return query.filter(False)  # 返回空
        
        return query
```

### 7.2 各模块数据过滤规则

| 模块 | 过滤字段 | data_scope | 示例SQL |
|------|---------|:---:|------|
| 客户 | `route_id` | `route` | `WHERE route_id IN (1, 3, 5)` |
| 销售订单 | `route_id` + `created_by` | `route` | `WHERE route_id IN (...) OR created_by = :uid` |
| 销售出库 | `route_id` | `route` | `WHERE route_id IN (...)` |
| 收款单 | `customer_id` (JOIN) | `route` | `JOIN customer WHERE route_id IN (...)` |
| 库存 | `warehouse_id` | `warehouse` | `WHERE warehouse_id IN (1, 2)` |
| 采购 | — | `all/none` | 业务员不可见 |
| 报表 | 聚合查询 | 按角色 | 业务员看自己路线统计 |
| 拜访记录 | `employee_id` | `self` | `WHERE employee_id = :uid` |
| 仓库调拨 | `from_wh` / `to_wh` | `warehouse` | `WHERE (from OR to) IN (...)` |

### 7.3 同路线业务员互看规则

> 销售订单：同路线业务员可**查看**，不可**编辑**（综合方案v3.0）

```python
# 查询时：自己路线的所有订单
orders = query.filter(
    or_(
        SalesOrder.created_by == user_ctx.employee_id,   # 自己创建的
        SalesOrder.route_id.in_(user_ctx.route_ids)       # 同路线的
    )
)

# 编辑时：只能编辑自己创建的
if order.created_by != user_ctx.employee_id:
    raise HTTPException(403, "只能编辑自己的订单")
```

---

## 八、审核权限 + 免审核

### 8.1 审核状态机

```
[待审核] ──审核通过──→ [已审核] → 可执行后续操作
    │
    ├──驳回──→ [已驳回] → 作废（不可恢复，提供[复制单据]按钮）
    │
    └──(免审角色)──→ 自动[已审核]
```

### 8.2 免审核判断逻辑

```python
def should_bypass_audit(employee, doc_type: str) -> bool:
    """判断是否需要审核"""
    # 管理员：全部免审
    if 'admin' in employee.roles:
        return True
    
    # 角色勾选了对应免审项
    if doc_type == 'sales_order' and employee.bypass_audit.get('so'):
        return True
    if doc_type == 'purchase_order' and employee.bypass_audit.get('po'):
        return True
    if doc_type == 'transfer' and employee.bypass_audit.get('tf'):
        return True
    
    return False

# 创建单据时
if should_bypass_audit(creator, 'sales_order'):
    order.audit_status = 'approved'  # 自动审核
    order.auditor_id = creator.id
    order.audit_time = now()
else:
    order.audit_status = 'pending'   # 进入待审核
```

---

## 九、实施路线图

### Phase 1：后端权限基础设施（Week 1） 🔴 P0

| 任务 | 负责人 | 预估 | 产出 |
|------|:---:|:---:|------|
| 1.1 创建权限相关表 | 小C | 1天 | roles / modules / role_module_permission / operation_permission / employee_role |
| 1.2 预制5角色+14模块+操作权限数据 | 小C | 0.5天 | SQL seed脚本 |
| 1.3 JWT Token 改造（多角色+多仓库+多路线） | 小C | 1天 | auth.py |
| 1.4 权限中间件开发 | 小C | 1天 | PermissionChecker Dependency |
| 1.5 数据过滤服务 | 小C | 1天 | DataFilter.apply_scope() |
| 1.6 登录API改造（返回完整权限信息） | 小C | 0.5天 | /api/auth/login 升级 |
| 1.7 权限查询API | 小C | 0.5天 | /api/auth/permissions + /api/auth/roles CRUD |

### Phase 2：PC端权限改造（Week 2） 🔴 P0

| 任务 | 负责人 | 预估 | 产出 |
|------|:---:|:---:|------|
| 2.1 authStore 改造（接收多角色+权限信息） | 小C | 0.5天 | Pinia authStore |
| 2.2 动态菜单渲染（14个views） | 小C | 1天 | Sidebar.vue + 菜单配置 |
| 2.3 动态路由守卫 | 小C | 0.5天 | router beforeEach |
| 2.4 页面操作按钮权限（v-if指令） | 小C | 1天 | 全页面改造 |
| 2.5 数据权限过滤（API自动加scope） | 小C | 0.5天 | 后端自动过滤 |
| 2.6 PC端免审核UI | 小C | 0.5天 | 审核按钮 + 自动跳过 |
| 2.7 角色权限管理页面 | 小C | 1天 | 角色列表+模块勾选+操作勾选 |

### Phase 3：H5端权限改造（Week 2-3） 🔴 P0

| 任务 | 负责人 | 预估 | 产出 |
|------|:---:|:---:|------|
| 3.1 H5 authStore（复用PC逻辑，Vant适配） | 小A | 0.5天 | Pinia store |
| 3.2 底部Tab动态渲染（5个Tab） | 小A | 0.5天 | TabBar组件 |
| 3.3 H5路由守卫 | 小A | 0.5天 | router beforeEach |
| 3.4 页面内按钮权限 | 小A | 0.5天 | v-if指令 |
| 3.5 业务员8窗口数据过滤 | 小A | 1天 | 路线+仓库过滤 |
| 3.6 微信H5下单权限（手机号认证） | 小A | 1天 | 微信入口+权限 |
| 3.7 H5端免审核UI | 小A | 0.5天 | 审核状态展示 |

### Phase 4：联调测试（Week 3） 🟡 P1

| 任务 | 负责人 | 预估 | 产出 |
|------|:---:|:---:|------|
| 4.1 多角色切换测试 | 小Q | 0.5天 | 测试用例 |
| 4.2 PC端14个views权限全覆盖测试 | 小Q | 0.5天 | 测试报告 |
| 4.3 H5端5个Tab权限全覆盖测试 | 小Q | 0.5天 | 测试报告 |
| 4.4 业务员路线隔离测试 | 小Q | 0.5天 | 用户A看不到用户B数据的验证 |
| 4.5 同路线互看测试 | 小Q | 0.5天 | 可看不可改 |
| 4.6 免审核流程测试 | 小Q | 0.5天 | 自动跳过+审核 |
| 4.7 窜货检测测试 | 小Q | 0.5天 | 跨路线报警 |

---

## 十、验收标准

### 模块权限（能进不能进）

| # | 验收项 | 验证方法 |
|---|--------|----------|
| 1 | 业务员登录 → PC/H5看不到"财务管理"菜单 | 角色=sales，菜单不显示 |
| 2 | 库管登录 → PC/H5看不到"客户管理"菜单 | 角色=warehouse |
| 3 | 老板登录 → PC/H5看到全部14个views / 5个Tab | 角色=admin |
| 4 | 多角色账号 → 权限取并集 | sales+warehouse → 同时看到销售+库存 |

### 操作权限（能做什么）

| # | 验收项 | 验证方法 |
|---|--------|----------|
| 5 | 业务员能创建销售订单，不能删除 | 有"新增"按钮，无"删除"按钮 |
| 6 | 库管不能创建采购订单 | 无"新增采购"按钮 |
| 7 | 非admin不能管理员工 | 无"员工管理"入口 |

### 数据权限（能看到什么）

| # | 验收项 | 验证方法 |
|---|--------|----------|
| 8 | 业务员A（武昌A线）看不到汉口线的客户 | 客户列表过滤 |
| 9 | 业务员A能看到同路线业务员B的订单（只读） | 可见但不可编辑 |
| 10 | 业务员A不能编辑业务员B的订单 | 编辑按钮置灰/隐藏 |
| 11 | 老板看到所有数据 | admin无过滤 |
| 12 | 库管只看绑定仓库的库存 | 库存列表过滤 |

### 免审核

| # | 验收项 | 验证方法 |
|---|--------|----------|
| 13 | 管理员创建订单→自动审核 | audit_status=approved |
| 14 | 业务员（未勾选免审）创建→待审核 | audit_status=pending |
| 15 | 角色勾选免审后→自动审核 | bypass_audit生效 |

---

## 十一、关键注意事项

1. **多角色并集**：一个账号有 sales+warehouse 两个角色 → 权限 = sales权限 ∪ warehouse权限
2. **数据范围取最宽**：多角色时，data_scope 取最宽松（all > route > warehouse > self）
3. **路由守卫前置于API**：前端路由先拦截（体验好），后端API必须兜底（安全）
4. **操作权限缓存在Store**：避免每次渲染都调API
5. **同路线互看**：查询放开，编辑收紧
6. **H5微信入口无登录**：手机号验证后走客户关联逻辑，不经过RBAC
7. **权限配置页面**：管理员可视化管理角色权限，修改后实时生效（刷新缓存）

---

## 十二、新权限方案 vs 综合方案 对比整合

| 维度 | 新权限方案 v20260502 | 综合方案 v3.0 | 本方案整合 |
|------|:---:|:---:|:---:|
| 角色数 | 6个（老板/销售/财务/库管/采购/员工） | 5个（admin/supervisor/sales/finance/warehouse） | 采用综合方案5角色，补"员工"作为data_scope=self |
| 模块数 | 24个API routers | 10大模块 | 15个views（PC端14+H5的"我的"） |
| H5 Tab | 5个 | 业务员8窗口 | 合并为5个Tab+子页面 |
| 数据隔离 | 基础（老板全看/员工只看自己） | 细粒度（路线+仓库+自我） | 采用综合方案三维过滤 |
| 审核 | 未详述 | 完整状态机+免审 | 采用综合方案 |
| 数据库 | 未涉及 | 完整DDL | 补充权限相关表 |

---

> 📝 方案版本：v1.1
> 📅 编制日期：2026-05-03
> 👤 编制：Hermes小A
> 📖 下发给：小C（后端+PC端）+ 小A（H5端）+ 小Q（测试）+ 银月（消息推送权限）→ 多啦A梦审核

---

## 十三、PC端 UI/UX 优化（公子明确需求）

### 13.1 多标签窗口

**功能说明：**
- 打开新模块 → 顶部出现新标签页
- 可切换、可关闭、可右键"关闭其他"
- 底部加"历史记录"快速回退
- 右键可"固定"标签页

**实现方案：**

```typescript
// stores/tabs.ts - 标签页管理
export const useTabStore = defineStore('tabs', {
  state: () => ({
    tabs: [{ path: '/dashboard', title: '首页', closable: false, fixed: true }],
    activeTab: '/dashboard',
    history: []
  }),
  actions: {
    addTab(route) {
      if (this.tabs.find(t => t.path === route.path)) {
        this.activeTab = route.path
        return
      }
      this.tabs.push({ ...route, closable: true })
      this.activeTab = route.path
      this.history.push(route.path)
    },
    closeTab(path) {
      const idx = this.tabs.findIndex(t => t.path === path)
      if (idx !== -1) this.tabs.splice(idx, 1)
    },
    closeOther(path) {
      this.tabs = this.tabs.filter(t => t.path === path || t.fixed)
    },
    pinTab(path) {
      const tab = this.tabs.find(t => t.path === path)
      if (tab) tab.fixed = true
    }
  }
})
```

**右键菜单配置：**

| 选项 | 功能 |
|------|------|
| 关闭 | 关闭当前标签 |
| 关闭其他 | 关闭除固定和当前外的所有标签 |
| 关闭全部 | 关闭所有可关闭标签 |
| 固定 | 固定/取消固定标签（固定标签不可关闭） |

**历史记录功能：**
- 底部固定"历史"按钮，点击展开最近访问的10个页面
- 支持快速回退到上一个页面

---

### 13.2 侧边栏 Hover 展开

**功能说明：**
- 鼠标移入 → 右侧滑出子模块面板
- 鼠标移出 → 0.3秒延迟后自动收回
- 子模块平铺展示，不挤占主内容区
- 支持键盘快捷键（Alt+数字）

**实现方案：**

```vue
<!-- SidebarHover.vue -->
<template>
  <div class="sidebar-container" 
       @mouseenter="handleMouseEnter"
       @mouseleave="handleMouseLeave">
    
    <!-- 收缩态：只显示图标 -->
    <div class="sidebar-icons" :class="{ expanded: isExpanded }">
      <div v-for="(item, idx) in menuItems" 
           :key="item.key"
           class="menu-item"
           :class="{ active: activeMenu === item.key }"
           @click="handleClick(item)"
           @mouseenter="showSubmenu(item)">
        <el-tooltip :content="item.label" placement="right">
          <el-icon><component :is="item.icon" /></el-icon>
        </el-tooltip>
        <span v-if="isExpanded" class="menu-label">{{ item.label }}</span>
      </div>
    </div>

    <!-- 悬停展开子面板 -->
    <transition name="slide">
      <div v-if="showPanel" class="submenu-panel">
        <div class="submenu-header">{{ currentMenu.label }}</div>
        <div class="submenu-items">
          <div v-for="sub in currentMenu.children" 
               :key="sub.path"
               class="submenu-item"
               @click="navigateTo(sub)">
            {{ sub.label }}
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
const isExpanded = ref(false)
const showPanel = ref(false)
const activeMenu = ref('')
const currentMenu = ref(null)
let hideTimer = null

function handleMouseEnter() {
  clearTimeout(hideTimer)
  isExpanded.value = true
}

function handleMouseLeave() {
  hideTimer = setTimeout(() => {
    isExpanded.value = false
    showPanel.value = false
  }, 300)
}

function showSubmenu(item) {
  if (item.children?.length) {
    currentMenu.value = item
    showPanel.value = true
    activeMenu.value = item.key
  } else {
    navigateTo(item)
  }
}
</script>

<style scoped>
.sidebar-container {
  display: flex;
  position: relative;
}

.sidebar-icons {
  width: 60px;
  transition: width 0.3s ease;
  background: #304156;
}

.sidebar-icons.expanded {
  width: 200px;
}

.submenu-panel {
  position: absolute;
  left: 60px;
  top: 0;
  width: 200px;
  height: 100%;
  background: #304156;
  box-shadow: 2px 0 10px rgba(0,0,0,0.2);
  z-index: 100;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}
</style>
```

**键盘快捷键支持：**

| 快捷键 | 功能 |
|--------|------|
| Alt + 1-9 | 快速切换到第1-9个菜单 |
| Alt + D | 回到首页/仪表盘 |
| Alt + B | 后退到上一个页面 |

---

### 13.3 标签页+侧边栏联动

```typescript
// 标签页点击 → 侧边栏高亮
function onTabClick(tab) {
  const menuItem = menuConfig.find(m => m.path === tab.path)
  if (menuItem) {
    activeMenu.value = menuItem.key
    router.push(tab.path)
  }
}

// 侧边栏点击 → 新增标签
function onSidebarClick(item) {
  tabStore.addTab({ path: item.path, title: item.label })
  router.push(item.path)
}
```

---

### 13.4 实施优先级

| 任务 | 预估 | 说明 |
|------|------|------|
| 多标签窗口 | 2天 | 标签页管理+右键菜单+历史记录 |
| 侧边栏Hover展开 | 1.5天 | 动画+子面板+快捷键 |
| 标签页+侧边栏联动 | 0.5天 | 状态同步 |

**预计总工时：4天**

---

## 十四、侧边栏交互修改（2026-05-03更新）

### 14.1 修改需求

**侧边栏状态：**
- 始终保持 220px 展开宽度，不收缩
- 主模块纵向排列在侧边栏里

**Hover 浮层小窗口：**
- 鼠标悬停在主模块上 → 在该主模块右侧弹出浮层（约 200px 宽）
- 显示该主模块下的所有子模块列表
- 浮层有背景色和边框，像个下拉菜单

**交互细节：**
- 鼠标离开主模块 → 浮层延迟 200ms 消失
- 鼠标进到浮层 → 浮层继续保持显示
- 子模块可点击跳转

**UI 优化（好看协调）：**
- 侧边栏背景色和整体设计风格协调
- 主模块和子模块的字体大小、间距协调
- 浮层有圆角、轻微阴影
- hover 的时候主模块有高亮背景色
- 子模块 hover 也有背景色变化

### 14.2 实现方案

**Layout.vue 核心逻辑：**

```vue
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
  </el-container>
</template>

<script setup>
// 主模块定义
const mainModules = [
  {
    key: 'home',
    label: '首页',
    icon: 'DataBoard',
    submodules: [{ path: '/dashboard', label: '首页' }]
  },
  {
    key: 'archives',
    label: '档案',
    icon: 'Folder',
    submodules: [
      { path: '/products', label: '商品管理', module: 'products' },
      { path: '/customers', label: '客户管理', module: 'customers' },
      // ... 更多子模块
    ]
  },
  // ... 更多主模块
]

// 弹窗相关状态
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
</script>

<style scoped>
/* 侧边栏基础样式 */
.sidebar-wrapper {
  display: flex;
  flex-shrink: 0;
  z-index: 100;
  position: relative;
}

.sidebar {
  background: #1f2d3d;
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
  padding: 8px 0;
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
</style>
```

### 14.3 与旧版对比

| 特性 | 旧版（hover收缩） | 新版（hover浮层） |
|------|------------------|-------------------|
| 侧边栏宽度 | 60px收缩 / 220px展开 | 始终220px固定 |
| 子模块显示 | el-sub-menu展开 | 浮层popup显示 |
| 交互方式 | 点击展开菜单 | hover显示浮层 |
| 动画效果 | width过渡 | opacity+transform过渡 |

### 14.4 实施状态

| 任务 | 状态 | 说明 |
|------|------|------|
| Layout.vue 改造 | ✅ 已完成 | 实现hover浮层交互 |
| 权限过滤 | ✅ 已完成 | visibleMainModules 根据 hasModule 过滤 |
| UI美化 | ✅ 已完成 | 圆角8px + 阴影 + hover高亮 |
| 文档更新 | ✅ 已完成 | 本章节记录修改内容 |

---

> 📝 方案版本：v1.1.1
> 📅 编制日期：2026-05-03
> 👤 编制：Hermes小A
> 📖 下发给：小C（后端+PC端）+ 小A（H5端）+ 小Q（测试）+ 银月（消息推送权限）→ 多啦A梦审核
