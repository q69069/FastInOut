# FastInOut PC端 + H5端 统一权限 — 实施细化方案 v2.4（开发基线版）

> 📅 编制日期：2026-05-04
> 👤 编制：Hermes小A
> 📖 依据：[PC+H5统一权限方案 v20260502] + [综合方案 v3.0] + [舟谱模块清单 v20260502] + [大纯反馈 v20260503 × 2份] + [大纯v2.2审阅 v20260504] + [大纯v2.3审阅 v20260504]
>
> ⚠️ 版本演进：
> - v2.0: 模块 14→28，对齐舟谱 P0+P1；明确订单≠单据命名
> - v2.1: 新增「车销模式详解」+「财务业务逻辑约束」
> - v2.2: 补采购单据层 + 审计日志 + 防作弊体系 + 退货财务确认 + 数据模型约束 + 实施分期重整
> - v2.3: 模块计数对齐(39入口) + 销售单状态流简化(去delivered) + Phase A过渡说明 + 费用拆单防绕过 + pending跨日锁定
> - **v2.4: 车销退货纳入交账 + 采购退货出库财务确认 + 审计前置Phase0 + 细节补全（最终基线）**

---

## 一、⚠️ 核心概念澄清 — 订单 vs 单据（必读）

在进销存系统中，**订单和单据是两层概念**，混为一谈会导致业务混乱：

```
┌─────────────────────────────────────────────────────────────┐
│                      订单 → 单据 关系（v2.2 完整闭环）        │
│                                                             │
│  销售侧：                                                   │
│    销售订单 ──审核通过──→ 销售单（扣库存，产生应收）          │
│    退货订单 ──审核通过──→ 退货单（加库存，冲应收）            │
│                                                             │
│  采购侧：                                                   │
│    采购订单 ──审核通过──→ 采购入库单（加库存，产生应付）⭐新增 │
│    采购退货单 ──审核通过──→ 采购退货出库单（减库存，冲应付）⭐ │
│                                                             │
│  订单 = 预定/申请   → 不改变库存，可修改可撤销                 │
│  单据 = 执行凭证   → 改变库存和财务，不可撤销（红冲除外）       │
└─────────────────────────────────────────────────────────────┘
```

| 概念层 | 销售侧 | 采购侧 | 特点 |
|--------|--------|--------|------|
| **订单层** | 销售订单 / 退货订单 | 采购订单 / 采购退货单 | 不扣库存，可改可撤 |
| **单据层** | 销售单 / 退货单 | **采购入库单⭐** / **采购退货出库单⭐** | 扣库存，不可撤，记财务账 |

> **FastInOut 当前状态**：只实现了订单层，单据层全部缺失。
> 
> **v2.2 修正**：采购侧已补全入库/出库执行凭证，与销售侧的「订单≠单据」原则完全对齐。

---

## 二、权限架构总览

```
┌──────────────────────────────────────────────────────────────┐
│                     统一权限架构 v2.2                         │
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
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  审计日志层 v2.2 ⭐（强制记录所有敏感操作）        │       │
│  └──────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

**三层权限模型（不变）：**

| 层级 | 检查内容 | 示例 |
|------|---------|------|
| **模块权限** | 能否进入该页面/菜单 | 库管能否看"财务管理" |
| **操作权限** | 能否执行增/删/改/查/审核/导出 | 业务员能否删除销售订单 |
| **数据权限** | 能看到哪些数据 | 业务员只能看自己路线客户 |

---

## 三、核心原则

| # | 原则 | 说明 |
|---|------|------|
| 1 | **PC/H5模块一致** | 后续所有新模块，PC和H5同步开发 |
| 2 | **一账号多角色** | 一个账号可绑定多个角色，权限取**并集** |
| 3 | **后端统一鉴权** | 所有API请求经统一中间件校验 |
| 4 | **前端动态渲染** | PC/H5根据权限动态显示菜单/Tab/按钮 |
| 5 | **路由+仓库双隔离** | 业务员可见数据 = 绑定路线 + 绑定仓库 |
| 6 | **细粒度可配置** | 管理员可逐角色勾选模块/操作权限 |
| 7 | **订单单据分离** | 订单≠单据，订单不扣库存，单据才扣 |
| 8 | **财务审核锁定** | 交账审核后关联单据全部锁定，不可撤回 |
| 9 | **跨日自动锁定** | 以服务器时区 00:00 为准，客户端无权决定 |
| 10 | **强制审计日志 ⭐v2.2** | 所有 CUD/状态变更/权限修改必须记日志，日志不可删除 |

---

## 四、完整模块清单（39个模块入口）

### 4.0 模块分类总览

```
📁 仪表盘(1个)        📁 业务类(11个)       📁 财务类(4个)
└─ 首页               ├─ 销售订单           ├─ 收付款管理
                       ├─ 销售单 ⭐          ├─ 预收/预付款 ⭐
📁 档案类(12个)        ├─ 退货订单           ├─ 费用管理 ⭐
├─ 客户管理            ├─ 退货单 ⭐          └─ 往来账 ⭐
├─ 供应商管理          ├─ 采购订单
├─ 商品管理            ├─ 采购退货           📁 报表类(4个)
├─ 品牌管理 ⭐         ├─ 采购入库单 ⭐v2.2  ├─ 销售报表 ⭐
├─ 单位管理            ├─ 采购退货出库单 ⭐v2├─ 采购报表 ⭐
├─ 渠道管理 ⭐         ├─ 库存管理           ├─ 库存报表
├─ 仓库管理            ├─ 盘点单 ⭐          └─ 财务报表 ⭐
├─ 批次管理            └─ 报损单 ⭐
├─ 员工管理                                    📁 系统类(3个)
├─ 线路管理 ⭐         📁 车销(2个)            ├─ 角色权限
├─ 员工提成 ⭐         ├─ 装车管理             ├─ 公司设置 ⭐
└─ 客户等级 ⭐         └─ 交账管理             └─ 数据备份

                       📁 营销类(1个)          📁 风控 ⭐v2.2
                       └─ 促销管理             └─ 审计日志
```

### 4.1 角色定义

| 角色 | role_key | 说明 | 数据范围 |
|------|:---:|------|----------|
| **老板/管理员** | `admin` | 全部功能+系统设置 | 全部数据 |
| **主管/文员** | `supervisor` | 档案+采购+销售+报表 | 按仓库/路线可限制 |
| **业务员** | `sales` | 销售+客户+自己路线 | 仅自己路线客户 |
| **财务** | `finance` | 财务+报表+对账+费用 | 全部财务数据 |
| **库管** | `warehouse` | 仓库+出入库+盘点+报损 | 绑定仓库 |

### 4.2 完整角色-模块映射表

#### 仪表盘 + 档案类（13个模块入口）

| 模块 | module_key | H5 Tab | admin | supervisor | sales | finance | warehouse |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 首页 | `dashboard` | 首页 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 客户管理 | `customers` | 客户 | ✅ | ✅ | ✅(自己) | ✅(查) | ❌ |
| 供应商管理 | `suppliers` | — | ✅ | ✅ | ❌ | ❌ | ❌ |
| 商品管理 | `products` | — | ✅ | ✅ | ❌ | ❌ | ✅(查) |
| **品牌管理 ⭐** | `brands` | — | ✅ | ✅ | ❌ | ❌ | ❌ |
| 单位管理 | `units` | — | ✅ | ✅ | ❌ | ❌ | ❌ |
| **渠道管理 ⭐** | `channels` | — | ✅ | ✅ | ❌ | ❌ | ❌ |
| **客户等级 ⭐** | `customer_levels` | — | ✅ | ✅ | ❌ | ❌ | ❌ |
| 仓库管理 | `warehouses` | — | ✅ | ✅(查) | ❌ | ❌ | ✅ |
| 批次管理 | `batches` | — | ✅ | ✅(查) | ❌ | ❌ | ✅ |
| 员工管理 | `employees` | — | ✅ | ❌ | ❌ | ❌ | ❌ |
| **线路管理 ⭐** | `routes` | — | ✅ | ✅ | ❌ | ❌ | ❌ |
| **员工提成 ⭐** | `commissions` | — | ✅ | ✅ | ❌ | ❌ | ❌ |

#### 业务类（11个模块）

| 模块 | module_key | H5 Tab | admin | supervisor | sales | finance | warehouse |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 销售订单 | `sales_order` | 销售 | ✅ | ✅ | ✅(自己) | ❌ | ❌ |
| **销售单 ⭐** | `sales_delivery` | 销售 | ✅ | ✅ | ✅(自己) | ❌ | ❌ |
| 退货订单 | `sales_return` | 销售 | ✅ | ✅ | ✅(自己) | ❌ | ❌ |
| **退货单 ⭐** | `sales_return_dlv` | — | ✅ | ✅ | ✅(自己) | ✅(财务确认) | ✅(收货) |
| 采购订单 | `purchase_order` | — | ✅ | ✅ | ❌ | ❌ | ❌ |
| 采购退货 | `purchase_return` | — | ✅ | ✅ | ❌ | ❌ | ❌ |
| **采购入库单 ⭐v2.2** | `purchase_receipt` | — | ✅ | ✅ | ❌ | ❌ | ✅(收货) |
| **采购退货出库单 ⭐v2.2** | `purchase_return_dlv` | — | ✅ | ✅ | ❌ | ❌ | ✅ |
| 库存管理 | `inventory` | 库存 | ✅ | ✅(查) | ✅(查) | ❌ | ✅ |
| **盘点单 ⭐** | `stocktaking` | — | ✅ | ✅ | ❌ | ❌ | ✅ |
| **报损单 ⭐** | `damage_report` | — | ✅ | ✅ | ❌ | ❌ | ✅ |

#### 车销（2个模块）⭐ 角色映射已补全

| 模块 | module_key | H5 Tab | admin | supervisor | sales | finance | warehouse |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **装车管理 ⭐** | `vehicle_load` | — | ✅ | ✅ | ❌ | ❌ | ✅ |
| **交账管理 ⭐** | `settlement` | — | ✅ | ✅(查) | ✅(创建) | ✅(审核) | ❌ |

> 装车由库管或主管操作；交账由业务员创建、财务审核，主管可查看。

#### 财务类（4个模块）

| 模块 | module_key | H5 Tab | admin | supervisor | sales | finance | warehouse |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 收付款管理 | `finance` | — | ✅ | ❌ | ❌ | ✅ | ❌ |
| **预收/预付款 ⭐** | `advance_payment` | — | ✅ | ❌ | ❌ | ✅ | ❌ |
| **费用管理 ⭐** | `expenses` | — | ✅ | ✅(查) | ❌ | ✅ | ❌ |
| **往来账 ⭐** | `account_ledger` | — | ✅ | ❌ | ❌ | ✅ | ❌ |

#### 报表类（4个模块）

| 模块 | module_key | H5 Tab | admin | supervisor | sales | finance | warehouse |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **销售报表 ⭐** | `report_sales` | — | ✅ | ✅(自) | ✅(自) | ❌ | ❌ |
| **采购报表 ⭐** | `report_purchase` | — | ✅ | ✅ | ❌ | ❌ | ❌ |
| 库存报表 | `report_inventory` | — | ✅ | ✅ | ✅(查) | ❌ | ✅ |
| **财务报表 ⭐** | `report_finance` | — | ✅ | ❌ | ❌ | ✅ | ❌ |

#### 营销 + 系统 + 风控（5个模块）

| 模块 | module_key | H5 Tab | admin | supervisor | sales | finance | warehouse |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 促销管理 | `promotions` | — | ✅ | ✅ | ✅(查) | ❌ | ❌ |
| 角色权限 | `roles` | — | ✅ | ❌ | ❌ | ❌ | ❌ |
| **公司设置 ⭐** | `company_config` | — | ✅ | ❌ | ❌ | ❌ | ❌ |
| 数据备份 | `backup` | — | ✅ | ❌ | ❌ | ❌ | ❌ |
| **审计日志 ⭐v2.2** | `audit_log` | — | ✅ | ❌ | ❌ | ❌ | ❌ |

> **H5 Tab 对应（5个Tab → 对应PC模块）：**
>
> | H5 Tab | 对应PC模块 |
> |--------|-----------|
> | 首页 | dashboard |
> | 客户 | customers |
> | 销售 | sales_order + sales_delivery + sales_return |
> | 库存 | inventory |
> | 我的 | 业绩/收款/设置（H5特有聚合页） |

---

## 五、重点新增模块详解

### 5.1 销售单（sales_delivery）— P0 核心新增

```
业务流程：
  模式A — 订单转单：
    销售订单 ──审核──→ 销售单 ──出库──→ 扣库存 + 记应收
  
  模式B — 直接开单（车销/现场）：
    选商品/扫条码 → 直接创建销售单 → 扣库存（车上/仓库）

数据流：
  sales_orders ──┐
                 ├──→ sales_deliveries (可合并多张订单生成一张单据)
  sales_orders ──┘       ├── delivery_items (出库商品明细)
  (或直接开单)            ├── 扣减 inventory / vehicle_inventory 库存
                          └── 生成 finance 应收记录
```

**关键规则：**
- 支持两种开单模式：`from_order`（订单转单）/ `direct`（直接开单，车销专用）
- 销售单一旦创建并确认，进入 `pending` 状态，不可删除（只能作废/红冲）
- 车销开单若车辆库存不足：禁止开单，提示「车上库存不足，请申请补货」
- 财务交账审核后进入 `settled`，彻底锁定
- 跨日自动锁定（以服务器时区00:00为准）

### 5.2 采购入库单（purchase_receipt）— v2.2 P0 核心新增 ⭐

```
业务流程：
  采购订单 ──审核──→ 采购入库单 ──入库──→ 加库存 + 记应付

数据流：
  purchase_orders ─→ purchase_receipts
                         ├── receipt_items (入库商品明细)
                         ├── 增加 inventory 库存
                         └── 生成 finance 应付记录
```

**关键规则：**
- 采购订单审核后生成采购入库单，仓管确认收货后库存才增加
- 支持「部分收货」：一张采购订单可分多次入库
- 入库单金额强制 = Σ(实收数量 × 采购单价)，不允许手动改金额
- 入库确认后不可删除（只能红冲）
- 跨日自动锁定

### 5.3 盘点单（stocktaking）— P0 核心新增

```
类型：
  ├── 整仓盘点单：锁定仓库，全部商品盘点
  └── 部分盘点单：指定商品范围，不锁定仓库

流程：
  创建盘点单 → 录入实盘数量 → 审核 → 自动生成盈亏调整（更新库存）
```

### 5.4 费用管理（expenses）— P0 核心新增

```
费用类型：
  ├── 费用支出（日常费用报销）
  ├── 费用合同（长期费用协议，如房租/物流合同）
  └── 其他收入（非主营收入）
```

### 5.5 往来账（account_ledger）— P0 核心新增

```
查询维度：
  ├── 客户往来账（按客户 + 时间段）
  │   ├── 期初应收 → 本期销售(+) → 本期收款(-) → 期末应收
  ├── 供应商往来账（按供应商）
  └── 应收/应付款汇总
```

### 5.6 P1 新增模块速览

| 模块 | 说明 |
|------|------|
| 预收/预付款 | 客户预存/预付供应商的款项管理 |
| 报损单 | 商品损坏/过期报废处理 |
| 品牌管理 | 商品品牌档案 |
| 渠道管理 | 销售渠道分类（批发/零售/电商等） |
| 线路管理 | 业务员拜访路线规划与分配 |
| 员工提成 | 按销售额/回款计算提成 |
| 销售报表 | 销售明细表 + 5维度汇总 |
| 采购报表 | 采购明细表 + 汇总表 |
| 财务报表 | 资产负债表 + 利润表 + 科目余额表 |
| 公司设置 | 企业基本信息/Logo/打印模板 |

---

## 六、🚚 车销模式详解

> 车销是快消品核心场景：业务员开车带货，到店直接卖，现场开单收钱。
> 区别于"坐销"（客户下单→仓库发货），车销不走订单流程，直接开销售单。

### 6.1 车销完整业务流程

```
┌─────────────────────────────────────────────────────────────┐
│                      车销一日流程                             │
│                                                             │
│  ① 装车出库                                                 │
│     仓库 ──装车单──→ 车辆（车上库存从仓库划拨）               │
│                                                             │
│  ② 现场销售                                                 │
│     到店 → 选客户 → 扫商品/选商品 → 填数量/单价               │
│     → 现场开销售单(source_type=direct) → 扣车上库存          │
│     → (可选)打印小票 → 收钱(现金/扫码/赊账) → 下一家         │
│                                                             │
│  ③ 回公司交账                                               │
│     汇总当日所有销售单 → 创建交账单                           │
│     → 财务核对：现金 + 微信 + 支付宝 + 赊账                  │
│     → 审核通过 → 锁定所有关联单据                            │
│                                                             │
│  ④ 退库                                                     │
│     车上未售完商品 → 退库单 → 回仓库（支持部分退库）          │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 装车（车销准备）

```
装车单 (vehicle_load):
  ├── 从仓库调拨商品到车辆
  ├── 创建车辆库存记录 (vehicle_inventory)
  └── 可选：按历史销量智能推荐装车量

装车流程：
  创建装车单 → 选仓库 → 选商品+数量 → 审核 → 库存从仓库划拨到车辆
```

**装车单状态：**
| 状态 | 说明 |
|------|------|
| `draft` | 草稿，可编辑 |
| `pending` | 待审核 |
| `loaded` | 已装车，商品已在车上 |
| `partial_return` ⭐v2.2 | 部分退库（剩半车货回库，另一半留车上过夜） |
| `returned` | 已全部退库 |

> ⭐v2.2: 新增 `partial_return` 子状态，允许对装车单明细进行分批退库，每次退库记录关联原装车单行。

### 6.3 现场开单（车销核心）

```
业务员移动端(H5/App)操作：

  ① 选择客户（支持从路线快速筛选今日未拜访客户）
  ② 添加商品（扫条码 / 搜索 / 常用商品快捷面板）
  ③ 填写数量和单价（自动带出历史售价/上次售价/价格方案）
  ④ 选择收款方式：
     ├── 现金
     ├── 微信/支付宝（扫码，必须关联支付流水号）
     ├── 赊账（挂应收，计入客户欠款）
     │   └── ⚠️ 单笔赊账>500元需主管实时审批
     └── 混合（部分现金+部分赊账）
  ⑤ 客户电子签名或拍照确认 ⭐v2.2
  ⑥ 确认开单 → 扣车上库存 → 打印蓝牙小票(可选) → 完成
```

**车销开单特性：**
- 开单即扣库存（扣的是车上库存，不是仓库库存）
- 无需审核，现场直接生效
- 单品/整单折扣支持
- 自动计算欠款（赊账部分记客户应收）
- 开错可当场作废（见第七节作废规则）

### 6.4 交账（日结）

> 交账是车销闭环的最后一步，也是财务审核的关键节点。

```
交账单 (settlement) 包含：

  业务员：张三
  日期：2026-05-04
  ┌─────────────────────────────────────────────┐
  │ 📊 销售汇总                                 │
  │   销售单数：15 单    销售总额：¥3,580.00     │
  │                                             │
  │ 收款明细：                                   │
  │   现金：  ¥1,200.00   微信：  ¥850.00        │
  │   支付宝：¥680.00    赊账：  ¥850.00         │
  │                                             │
  │ 🔙 退货汇总 ⭐v2.4                           │
  │   退货单数：2 单     退货总额：¥320.00       │
  │   退款明细：                                 │
  │     现金退款：  ¥200.00                      │
  │     冲赊账：    ¥120.00                      │
  │     电子退款：  ¥0                           │
  │                                             │
  │ 💰 实交现金 = 销售现金¥1,200 - 退货现金¥200   │
  │           = ¥1,000 ⭐v2.4                    │
  │                                             │
  │ 🧾 费用报销：(可选)                          │
  │   油费：¥100  餐费：¥30                      │
  │   ⚠️ ≤200元：交账审核时自动入账               │
  │   ⚠️ >200元：仅生成草稿，等财务单独审          │
  └─────────────────────────────────────────────┘
```

**交账流程：**
```
  ① 业务员：汇总当日所有销售单 + 退货单 → 填写交账单 → 提交
     → 销售单进入 settling，退货单同步关联（暂不锁定）⭐v2.4
  
  ② 财务：核对销售收款 + 退货退款 →
     核心公式：交账现金 = Σ(销售现金收入) - Σ(退货现金退款) ⭐v2.4
     赊账净额 = Σ(销售赊账) - Σ(退货冲赊账)
     ├── 通过：审核 → 锁定所有关联销售单(→settled)
     │   - 退货单同步完成 finance_confirmed → settled ⭐v2.4
     │   - 金额快照写入 settlement_snapshot JSON
     └── 驳回：解绑销售单(→pending)，退货单保持原状态，退回修改
  
  ③ 财务审核通过后：
     - 关联销售单全部锁定（不可作废/修改）
     - 关联退货单完成财务确认并锁定 ⭐v2.4
     - 自动生成收款/退款记录
     - 现金净额入账，赊账净额记客户应收
     - 若含费用报销(≤200元)，自动生成已审核费用记录
     - 若含费用报销(>200元)，生成草稿费用等待财务单独审核
```

### 6.5 车销特殊场景处理

| 场景 | 处理方式 |
|------|---------|
| **开错单** | 当场作废（状态→voided），必须填写作废原因，复制作废单据开新单时标注原单号 |
| **客户退货** | 开退货单，商品回车上库存。退货单关联到当日交账单，纳入资金汇总 ⭐v2.4 |
| **赊账不还** | 交账时标记，记客户应收，后续跟催 |
| **车上商品损坏** | 开报损单，从车上库存扣减 |
| **中途补货** | 回仓库补充装车，创建补充装车单 |
| **跨天未交账** | 当日0点后未交账的销售单自动锁定，次日必须补交 |
| **多家店合并收款** | 支持按客户汇总，也支持单店单结 |
| **部分退库 ⭐v2.2** | 允许装车单明细级分批退库 |

### 6.6 车销数据模型补充

```sql
-- 车辆档案
CREATE TABLE vehicle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_no VARCHAR(10) NOT NULL,
    driver_id INTEGER,
    status VARCHAR(20) DEFAULT 'active'
);

-- 车上库存（车辆维度虚拟库存）
CREATE TABLE vehicle_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    batch_id INTEGER,
    quantity DECIMAL(12,2) NOT NULL,
    UNIQUE(vehicle_id, product_id, batch_id)
);

-- 装车单
CREATE TABLE vehicle_load (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    load_no VARCHAR(30) UNIQUE NOT NULL,
    vehicle_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',     -- draft/pending/loaded/partial_return/returned
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 装车明细
CREATE TABLE vehicle_load_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    load_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    batch_id INTEGER,
    quantity DECIMAL(12,2) NOT NULL,
    returned_quantity DECIMAL(12,2) DEFAULT 0  -- ⭐v2.2: 已退库数量
);

-- 退库记录 ⭐v2.2
CREATE TABLE vehicle_return (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    load_id INTEGER NOT NULL,
    load_item_id INTEGER NOT NULL,              -- 关联装车单明细行
    return_quantity DECIMAL(12,2) NOT NULL,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 交账单
CREATE TABLE settlement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    settlement_no VARCHAR(30) UNIQUE NOT NULL,
    employee_id INTEGER NOT NULL,
    settlement_date DATE NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,        -- 销售总额
    cash_amount DECIMAL(12,2) DEFAULT 0,        -- 销售现金收入
    wechat_amount DECIMAL(12,2) DEFAULT 0,
    alipay_amount DECIMAL(12,2) DEFAULT 0,
    credit_amount DECIMAL(12,2) DEFAULT 0,      -- 销售赊账
    return_total DECIMAL(12,2) DEFAULT 0,       -- ⭐v2.4: 退货总额
    return_cash DECIMAL(12,2) DEFAULT 0,        -- ⭐v2.4: 退货现金退款
    return_credit DECIMAL(12,2) DEFAULT 0,      -- ⭐v2.4: 退货冲赊账
    return_electronic DECIMAL(12,2) DEFAULT 0,  -- ⭐v2.4: 退货电子退款
    expense_amount DECIMAL(12,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    settlement_snapshot TEXT,                    -- 审核时快照 JSON（见§10.1说明）
    auditor_id INTEGER,
    audited_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 交账-销售单关联
CREATE TABLE settlement_delivery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    settlement_id INTEGER NOT NULL,
    delivery_id INTEGER NOT NULL,
    UNIQUE(settlement_id, delivery_id)
);

-- 交账-退货单关联 ⭐v2.4
CREATE TABLE settlement_return (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    settlement_id INTEGER NOT NULL,
    return_delivery_id INTEGER NOT NULL,         -- 关联 sales_return_delivery
    UNIQUE(settlement_id, return_delivery_id)
);
```

---

## 七、🔒 财务业务逻辑约束

> 本节定义所有单据的生命周期、状态流转、撤回/作废/锁定规则。
> **核心原则：财务审核锁定 > 跨日自动锁定 > 创建人可撤回**

### 7.1 销售订单 — 生命周期与约束

```
状态流转：
  draft ──提交──→ pending ──审核──→ audited ──转单──→ converted
    │                │                │
    └── 可编辑/删除   │                └── 已锁定，不可撤回
                     │
                     ├── 创建人当日可撤回 → draft
                     ├── 跨日(0点)自动锁定 → locked
                     └── 审核人驳回 → draft
```

| 操作 | draft | pending(当日) | pending(跨日) | audited | converted |
|------|:---:|:---:|:---:|:---:|:---:|
| 编辑 | ✅ | ✅(创建人) | ❌ | ❌ | ❌ |
| 删除 | ✅ | ✅(创建人) | ❌ | ❌ | ❌ |
| 撤回 | — | ✅(创建人) | ❌ | ❌ | ❌ |
| 审核 | — | ✅(审核人) | ✅(审核人) | — | — |
| 驳回 | — | ✅(审核人) | ✅(审核人) | ❌ | ❌ |
| 转单 | — | — | — | ✅ | — |

**撤回规则详解：**
- 业务员提交后发现错误 → 当天内可撤回，修改后重新提交
- 主管审核中发现错误 → 驳回，业务员修改后重提
- **跨日后（服务器时区 00:00）→ 无论什么状态，自动锁定 ⭐v2.2明确**
- 审核通过后 → 不可撤回，只能通过转退货单来冲销

### 7.2 销售单 — 生命周期与约束

```
⭐v2.3 简化状态流（去掉了多余的 delivered 态）：

状态流转：
  pending(已开单,库存已扣) ──交账提交──→ settling ⭐v2.3 ──财务审核──→ settled
    │                          │                     │
    │                          └── 禁止编辑/作废      └── 彻底锁定
    ├── 开单人当日可作废 → voided（库存回滚）
    │   └── 复制开新单（标注原单号）
    │
    └── 跨日自动锁定 → locked
        └── 不可作废，只能红冲

关键设计意图：
  - pending = 已开单、已扣库存、当日可作废（库存回滚）
  - 车销开单即进入 pending（开单=确认=扣库存），与坐销逻辑完全一致
  - 不再有"确认"动作——开单本身即确认，无需额外步骤
  - 交账提交时才流转到 settling
```

| 操作 | pending(当日) | pending(跨日⭐v2.3) | settling | settled |
|------|:---:|:---:|:---:|:---:|
| 编辑 | ✅(开单人) | ❌ | ❌ | ❌ |
| 作废 | ✅(开单人,须填原因) | ❌ | ❌ | ❌ |
| 红冲 | — | ✅(主管) | ❌ | ✅(admin) |
| 交账提交 | ✅ | ✅(但单据已锁定不可改) | — | — |
| 交账打回 | — | — | ✅(恢复pending) | — |
| 财务审核 | — | ✅ | ✅ | — |

> ⚠️ v2.3: pending跨日也自动锁定（见§7.3），防止单据挂在pending状态过夜不交账。锁定后业务员只能等次日交账，不可作废。

**作废 vs 红冲：**

| | 作废（void） | 红冲（reverse） |
|------|------|------|
| 时机 | 开单当日，未提交交账 | 任何时间（跨日/已审核后） |
| 操作人 | 开单人自己 | 主管/admin |
| 效果 | 单据失效，库存回滚 | 原单保留，生成等额负数冲销单 |
| 痕迹 | 状态标记 voided，不展示 | 原单+冲销单都可见，金额抵消 |
| 可复制 | ✅ 可复制作废单开新单 | ❌ 冲销单不可再冲 |

**⭐v2.2: 作废单复制管控：**
```
  作废单 → 填写作废原因（必填） → 点击"复制开单"
  → 自动填入原商品/数量/客户
  → 新单标注"复制自 XS-xxx(已作废)"
  → 系统记录原单号关联
```

### 7.3 跨日锁定机制

```
⭐v2.3 明确以服务器时区为准，覆盖 pending 状态：

  服务端 UTC → 转换到业务时区 → 每日 00:00 自动检查：
  
  ① 未审核的销售订单 → 状态锁定为 locked（不可撤回/编辑）
  ② 未交账的销售单(pending) → 自动锁定为 locked ⭐v2.3（不可作废，次日只能交账或红冲）
  ③ 已提交交账但未审核的销售单(settling) → 保持 settling，不受跨日影响
  ④ 未审核的退货单/入库单 → 状态锁定
  ⑤ 未审核的盘点单 → 状态锁定

  后端严格校验：
  - 每次修改请求校验服务器当前时间与单据创建日期
  - 若跨日，直接拒绝修改，返回错误码
  - 客户端无权决定锁定，只展示状态
  
  车销离线模式：
  - 上线后先检查所有离线单据的创建日期
  - 与服务器今天日期对比
  - 超出的自动锁定，提示用户
```

### 7.4 交账审核锁定机制

```
⭐v2.3: 提交交账即锁定关联单据

  ① 业务员提交交账单 → settlement.status = pending
     → 关联销售单立即从 pending 进入 settling 状态
     → settling 状态：禁止编辑、禁止作废
     → 若交账被打回 → 解绑销售单 → 恢复 pending → 可编辑

财务点击"审核通过"后，连锁反应：

  ① settlement.status → audited
  ② settlement_snapshot ← 本次审核时刻的快照 JSON
  ③ 关联的所有 sales_deliveries → settled（锁定）
  ④ 自动生成 finance 收款记录
  ⑤ 若含费用报销(≤200元) → 自动生成 expense 已审核记录
     若含费用报销(>200元) → 生成 expense 草稿，需财务单独审核

  ⚠️ v2.3 费用拆单防绕过：
  同一次交账中，同一费用类别出现多笔相似金额时，系统标记提醒：
  "检测到同类别费用多笔(油费: ¥150 + ¥150)，可能为拆单绕过阈值，建议合并审核"
  财务可在系统设置中调整阈值（默认200元，可下调至50元）

审核驳回：
  - settlement.status → rejected
  - 关联单据解绑，恢复 pending，业务员可修改交账单后重新提交
  - 驳回原因必填
```

### 7.5 退货单约束 — ⭐v2.4 明确 settled 触发时机

```
退货单状态 v2.4：
  pending ──仓管收货+拍照──→ warehouse_confirmed ──财务确认──→ finance_confirmed
                                     │                      │
                                     └── 照片存证             └── 确认冲账金额
                                                             │
                                          ┌──────────────────┘
                                          │
                                     交账审核通过时自动 → settled ⭐v2.4

⭐v2.4 明确：
  - finance_confirmed 是退货单的「最终业务确认态」
  - settled 仅在关联交账单审核通过时由系统自动触发
  - 非车销场景（无交账）：finance_confirmed 即为终态
  - 车销场景：退货单关联交账单 → 交账审核通过 → 自动流转到 settled

约束：
  - 退货单必须关联原销售单或指定客户
  - 退货入库必须拍照上传
  - 仓管确认实物入库（第二人质检，非业务员本人）→ warehouse_confirmed
  - 财务审核冲账金额是否正确 → finance_confirmed，然后才能冲应收
  - 单次退货>1000元需主管审批 ⭐v2.2
  - 已交账后不可作废，只能红冲
  - 跨日自动锁定
```

### 7.6 采购退货出库单约束 — ⭐v2.4 增加财务确认

```
采购退货出库单状态 v2.4：
  pending ──仓管确认出库──→ warehouse_confirmed ──财务确认──→ finance_confirmed
                                    │                      │
                                    └── 库存减少             └── 冲减供应商应付

⭐v2.4 设计意图：
  - 参照退货单模式，采购退货也需要财务确认冲应付金额
  - 仓库出了货但财务没冲应付 → 应付虚高，必须由财务审核确认
  - finance_confirmed 后冲减供应商应付，资金流闭环

约束：
  - 采购退货出库单必须关联原采购订单或采购入库单
  - 仓管确认实物出库 → warehouse_confirmed（库存扣减）
  - 财务确认冲账金额 → finance_confirmed（冲减供应商应付）
  - 确认后不可删除，只能红冲
  - 跨日自动锁定
```

### 7.7 报损单约束

```
状态：draft → pending → audited → executed(已执行)

约束：
  - 审核通过后自动扣减库存
  - 审核后不可撤回（库存已变）
  - 报损必须填原因：过期/损坏/丢失/其他
  - 金额超过阈值（如¥500）需主管二级审批
```

### 7.8 盘点单约束

```
状态：draft → pending → auditing(盘点中) → audited → adjusted(已调整)

约束：
  - 整仓盘点期间，该仓库禁止出入库操作
  - 部分盘点期间，只锁定被盘点商品
  - 审核通过后自动生成盈亏调整记录
  - 审核后不可撤回
  - 盘点差异超过阈值（如5%）需主管复核
```

### 7.9 库存扣减时机汇总 — ⭐v2.2 补采购侧

| 操作 | 扣减时机 | 扣减对象 |
|------|---------|---------|
| 车销直接开单 | **开单时** | 车上库存(vehicle_inventory) |
| 订单转销售单 | **转单审核时** | 仓库库存(inventory) |
| 采购入库单确认 ⭐v2.2 | **仓管确认收货时** | 仓库库存(inventory)（加回） |
| 采购退货出库单确认 ⭐v2.2 | **仓管确认出库时** | 仓库库存(inventory)（扣减） |
| 退货单审核 | **仓管确认收货时** | 仓库/车辆库存（加回） |
| 报损单审核 | **审核通过时** | 仓库/车辆库存（扣减） |
| 盘点盈 | **审核通过时** | 仓库库存（调增） |
| 盘点亏 | **审核通过时** | 仓库库存（调减） |
| 装车 | **审核通过时** | 仓库→车辆（划拨） |
| 退库 | **审核通过时** | 车辆→仓库（划拨） |

> ⚠️ 关键：**订单层不扣库存，只有单据层才扣。** 采购侧 v2.2 已补全。

### 7.10 财务对账约束

| 约束 | 说明 |
|------|------|
| 日结对账 | 每日财务必须核对：交账单金额 = 销售单汇总 = 收款记录汇总 |
| 客户对账 | 客户应收 = 赊账销售单 - 还款 - 退货 |
| 供应商对账 | 供应商应付 = 采购入库单 - 付款 - 退货 |
| 库存对账 | 理论库存 = 实际库存 ± 盘点差异 |
| 跨月锁定 | 月末结账后，上月所有单据不可修改 |

### 7.11 权限与操作边界总表

| 操作 | 业务员 | 主管 | 财务 | 库管 | admin |
|------|:---:|:---:|:---:|:---:|:---:|
| 创建销售订单 | ✅ | ✅ | ❌ | ❌ | ✅ |
| 撤回自己订单(当日) | ✅ | — | — | — | — |
| 审核销售订单 | ❌ | ✅ | ❌ | ❌ | ✅ |
| 车销直接开单 | ✅ | ✅ | ❌ | ❌ | ✅ |
| 作废自己销售单(当日) | ✅ | — | — | — | — |
| 红冲销售单 | ❌ | ✅ | ❌ | ❌ | ✅ |
| 创建交账单 | ✅ | ✅ | ❌ | ❌ | ✅ |
| 审核交账单 | ❌ | ❌ | ✅ | ❌ | ✅ |
| 仓管确认退货入库 | ❌ | ✅ | ❌ | ✅ | ✅ |
| 财务确认退货冲账 ⭐v2.2 | ❌ | ❌ | ✅ | ❌ | ✅ |
| 仓管确认采购入库 ⭐v2.2 | ❌ | ❌ | ❌ | ✅ | ✅ |
| 创建盘点单 | ❌ | ✅ | ❌ | ✅ | ✅ |
| 审核盘点单 | ❌ | ✅ | ❌ | ❌ | ✅ |
| 创建报损单 | ❌ | ✅ | ❌ | ✅ | ✅ |
| 审核报损单 | ❌ | ✅ | ❌ | ❌ | ✅ |
| 查看往来账 | ❌ | ✅(查) | ✅ | ❌ | ✅ |
| 查看财务报表 | ❌ | ❌ | ✅ | ❌ | ✅ |
| 查看审计日志 ⭐v2.2 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 公司设置 | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 八、🛡️ 防作弊体系（v2.2 新增整章）

> v2.1 方案本身没有致命设计缺陷，但在财务审计和防作弊角度存在可钻的空子。
> 本章逐项给出堵漏方案。

### 8.1 漏洞清单与修复

#### 漏洞 1：现金收款方式虚报 🔴高风险

**场景**：业务员现场收现金100元，开单写「现金40+赊账60」，交账只交40现金，60变成客户应收，日后可能变坏账。

**堵漏方案**：
| 措施 | 实现方式 |
|------|---------|
| 客户电子签名 | H5开单完成弹窗 → 客户手写签名或确认按钮 → 存为凭证 |
| 微信/支付宝流水关联 | 扫码收款后调用支付平台API获取流水号，财务可核验到账 |
| 大额赊账审批 | 单笔赊账>500元，自动推主管审批（H5实时推送） |
| 财务抽查 | 交账审核时，财务有权要求提供某几单客户签收单/转账截图 |

#### 漏洞 2：作废+复制开单截留现金 🔴高风险

**场景**：卖A客户收现金 → 作废单据（库存回滚） → 复制开新单改为全赊账 → 现金截留。

**堵漏方案**：
| 措施 | 实现方式 |
|------|---------|
| 作废原因必填 | void操作需选择/填写原因，存入 void_reason 字段 |
| 复制关联原单 | 复制开新单时自动标注「复制自 XS-xxx(已作废)」，系统记录原单号 |
| 风控报表 | 「作废单复开分析」报表：作废后短时间内同一客户/商品的新单 |
| 版本控制 | 鼓励修改原单而非作废+复制，技术上实现 delivery_versioning |

#### 漏洞 3：虚假退货套取冲账 🔴高风险

**场景**：业务员与客户合谋开虚构退货单，仓管配合做虚假收货，套取应收冲账。

**堵漏方案**：
| 措施 | 实现方式 |
|------|---------|
| 退货拍照 | 退货入库必须拍照上传商品图片（H5端相机调用） |
| 第二人质检 | 仓管确认收货时，质检人≠业务员本人（系统校验） |
| 财务确认环节 | 仓管确认后需财务再确认冲账金额（见7.5节） |
| 大额审批 | 单次退货>1000元需主管审批 |

#### 漏洞 4：交账窗口期修改单据 🟡中风险

**场景**：业务员提交交账后、财务审核前，去修改关联的销售单收款方式。

**堵漏方案**（见7.4节）：
- 交账提交瞬间 → 关联销售单立即进入 `settling` 状态
- `settling` 状态禁止编辑和作废
- 交账打回后恢复 `pending`，才能修改

#### 漏洞 5：费用重复报销与拆单绕过 🟡中风险

**场景**：交账夹带费用报销，同时在费用模块再提一笔相同的。或者把一笔大额费用拆成多笔小额（如300元拆成2×150元），绕过≤200元自动入账。

**堵漏方案**：
| 措施 | 实现方式 |
|------|---------|
| 重复检测 | 同一日期+同一金额+同一类别，自动标记重复并拒绝 |
| **交账维度拆单检测 ⭐v2.3** | 同一次交账中，同一费用类别出现≥2笔时，系统自动提示「可能为拆单绕过阈值」 |
| 阈值可配置 | 财务可在公司设置中将交账费用阈值从200元下调（如50元） |
| 发票必传 | 所有报销必须上传发票照片/电子发票 |
| 收款人审批 | 费用收款人为内部员工的，需上级审批，不能自报自审 |
| 交账费用阈值 | ≤200元：交账审核时自动入账；>200元：只生成草稿（见7.4节） |

#### 漏洞 6：缺少审计日志 🔴高风险

**场景**：有人通过数据库直接修改库存/应收，后端无感知，出事无法追责。

**堵漏方案**：

```sql
-- ⭐v2.2 核心新增
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,          -- e.g., 'sales_delivery.void', 'settlement.audit'
    entity_type VARCHAR(30) NOT NULL,     -- e.g., 'sales_delivery', 'inventory'
    entity_id INTEGER,                    -- 被操作记录的ID
    old_value TEXT,                       -- JSON: 变更前的值
    new_value TEXT,                       -- JSON: 变更后的值
    ip_address VARCHAR(45),
    user_agent VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 日志策略：
-- 1. 任何数据的 CUD（增删改）必须记日志
-- 2. 任何状态变更必须记日志
-- 3. 任何权限修改必须记日志
-- 4. 日志只能追加（INSERT），不可删除（无DELETE权限）
-- 5. 管理员也无权删除日志（通过数据库权限控制）
-- 6. 定期生成操作审计报告供老板查看
```

**审计日志覆盖范围：**
- 销售订单：创建/编辑/删除/撤回/审核/驳回/转单
- 销售单：开单/编辑/作废/红冲/交账提交/交账审核
- 退货单：创建/仓管确认/财务确认/红冲
- 采购入库单：创建/仓管确认/红冲
- 盘点单：创建/审核/库存调整
- 库存变更：所有库存增减操作
- 权限变更：角色分配、权限修改
- 系统设置：公司配置变更

#### 漏洞 7：跨日锁定绕过 🟢低风险

见7.3节，后端严格校验服务器时区。

### 8.2 防作弊体系总览

| 机制 | 说明 | 实施阶段 |
|------|------|:---:|
| **审计日志** | 所有操作可追溯，日志不可删 | Phase A |
| **异常交易监控** | 自动标记：同日多单退款/作废后复制/超低单价/赊账比例异常 | Phase D |
| **价格管控** | 商品设最低售价，低于此价需主管审批 | Phase C |
| **客户对账确认** | 每月向客户发电子对账单，客户确认应收余额 | Phase D |
| **视频/照片存证** | 车销开单、退货入库强制拍照留存 | Phase B/C |
| **资金流水匹配** | 线上收款必须匹配支付平台流水 | Phase B |
| **轮岗与盘点** | 系统支持定期盘点，他人复核 | Phase C |

---

## 九、权限数据模型设计

### 9.1 角色表（不变）

```sql
CREATE TABLE role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_key VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(20) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    status VARCHAR(10) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO role (role_key, name, is_system) VALUES
('admin',        '老板/管理员', 1),
('supervisor',   '主管/文员',   1),
('sales',        '业务员',      1),
('finance',      '财务',        1),
('warehouse',    '库管',        1);
```

### 9.2 模块表 — v2.2 完整34个模块

```sql
CREATE TABLE module (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_key VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(30) NOT NULL,
    parent_id INTEGER,
    module_type VARCHAR(10) DEFAULT 'page',
    pc_view BOOLEAN DEFAULT 1,
    h5_tab VARCHAR(20),
    sort_order INTEGER DEFAULT 0,
    icon VARCHAR(30),
    path VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO module (module_key, name, module_type, h5_tab, sort_order) VALUES
-- 仪表盘(1)
('dashboard',          '首页',          'page', '首页', 1),
-- 档案类(12)
('customers',          '客户管理',      'page', '客户', 10),
('suppliers',          '供应商管理',    'page', NULL,   11),
('products',           '商品管理',      'page', NULL,   12),
('brands',             '品牌管理',      'page', NULL,   13),
('units',              '单位管理',      'page', NULL,   14),
('channels',           '渠道管理',      'page', NULL,   15),
('customer_levels',    '客户等级',      'page', NULL,   16),
('warehouses',         '仓库管理',      'page', NULL,   17),
('batches',            '批次管理',      'page', NULL,   18),
('employees',          '员工管理',      'page', NULL,   19),
('routes',             '线路管理',      'page', NULL,   20),
('commissions',        '员工提成',      'page', NULL,   21),
-- 业务类(11) ⭐v2.2 +2
('sales_order',        '销售订单',      'page', '销售', 30),
('sales_delivery',     '销售单',        'page', '销售', 31),
('sales_return',       '退货订单',      'page', '销售', 32),
('sales_return_dlv',   '退货单',        'page', NULL,   33),
('purchase_order',     '采购订单',      'page', NULL,   34),
('purchase_return',    '采购退货',      'page', NULL,   35),
('purchase_receipt',   '采购入库单',    'page', NULL,   36),   -- ⭐v2.2
('purchase_return_dlv','采购退货出库单','page', NULL,   37),   -- ⭐v2.2
('inventory',          '库存管理',      'page', '库存', 38),
('stocktaking',        '盘点单',        'page', NULL,   39),
('damage_report',      '报损单',        'page', NULL,   40),
-- 车销(2)
('vehicle_load',       '装车管理',      'page', NULL,   41),
('settlement',         '交账管理',      'page', NULL,   42),
-- 财务类(4)
('finance',            '收付款管理',    'page', NULL,   50),
('advance_payment',    '预收/预付款',   'page', NULL,   51),
('expenses',           '费用管理',      'page', NULL,   52),
('account_ledger',     '往来账',        'page', NULL,   53),
-- 报表类(4)
('report_sales',       '销售报表',      'page', NULL,   60),
('report_purchase',    '采购报表',      'page', NULL,   61),
('report_inventory',   '库存报表',      'page', NULL,   62),
('report_finance',     '财务报表',      'page', NULL,   63),
-- 风控 ⭐v2.2
('audit_log',          '审计日志',      'page', NULL,   64),
-- 营销+系统(4)
('promotions',         '促销管理',      'page', NULL,   70),
('roles',              '角色权限',      'page', NULL,   80),
('company_config',     '公司设置',      'page', NULL,   81),
('backup',             '数据备份',      'page', NULL,   82);
```

### 9.3 角色-模块权限表

```sql
CREATE TABLE role_module_permission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
    can_view BOOLEAN DEFAULT 1,
    can_create BOOLEAN DEFAULT 0,
    can_edit BOOLEAN DEFAULT 0,
    can_delete BOOLEAN DEFAULT 0,
    can_audit BOOLEAN DEFAULT 0,
    can_export BOOLEAN DEFAULT 0,
    data_scope VARCHAR(20) DEFAULT 'all',
    UNIQUE(role_id, module_id)
);
```

### 9.4 操作权限表 — v2.2 完整清单

```sql
CREATE TABLE operation_permission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    operation_key VARCHAR(50) NOT NULL,
    allowed BOOLEAN DEFAULT 0,
    UNIQUE(role_id, operation_key)
);
```

**完整操作权限（按模块分类）：**

##### 档案类

| 模块 | operation_key | 说明 | admin | supervisor | sales | finance | warehouse |
|------|------|------|:---:|:---:|:---:|:---:|:---:|
| 客户 | `customers:create` | 新增 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 客户 | `customers:edit` | 编辑 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 客户 | `customers:delete` | 删除 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 客户 | `customers:export` | 导出 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 商品 | `products:create` | 新增商品 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 商品 | `products:edit` | 编辑 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 品牌 | `brands:manage` | 品牌管理 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 渠道 | `channels:manage` | 渠道管理 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 线路 | `routes:manage` | 线路管理 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 提成 | `commissions:config` | 提成配置 | ✅ | ✅ | ❌ | ❌ | ❌ |

##### 业务类（含采购侧 v2.2）

| 模块 | operation_key | 说明 | admin | supervisor | sales | finance | warehouse |
|------|------|------|:---:|:---:|:---:|:---:|:---:|
| 销售订单 | `sales_order:create` | 创建 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 销售订单 | `sales_order:edit` | 编辑 | ✅ | ✅ | ✅(自己) | ❌ | ❌ |
| 销售订单 | `sales_order:delete` | 删除 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 销售订单 | `sales_order:audit` | 审核 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 销售订单 | `sales_order:withdraw` | 撤回(当日) | ✅ | ✅ | ✅(自己) | ❌ | ❌ |
| **销售单** | `sales_delivery:create` | 开单 | ✅ | ✅ | ✅ | ❌ | ❌ |
| **销售单** | `sales_delivery:void` | 作废(当日) | ✅ | ✅ | ✅(自己) | ❌ | ❌ |
| **销售单** | `sales_delivery:reverse` | 红冲 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 退货订单 | `sales_return:create` | 创建 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 退货订单 | `sales_return:audit` | 审核 | ✅ | ✅ | ❌ | ❌ | ❌ |
| **退货单** | `sales_return_dlv:create` | 入库 | ✅ | ✅ | ❌ | ❌ | ✅ |
| **退货单** | `sales_return_dlv:wh_confirm` | 仓管确认 ⭐v2.2 | ✅ | ✅ | ❌ | ❌ | ✅ |
| **退货单** | `sales_return_dlv:fin_confirm` | 财务确认 ⭐v2.2 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 采购订单 | `purchase_order:create` | 创建 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 采购订单 | `purchase_order:audit` | 审核 | ✅ | ✅ | ❌ | ❌ | ❌ |
| **采购入库单 ⭐v2.2** | `purchase_receipt:create` | 创建 | ✅ | ✅ | ❌ | ❌ | ❌ |
| **采购入库单 ⭐v2.2** | `purchase_receipt:confirm` | 确认收货 | ✅ | ✅ | ❌ | ❌ | ✅ |
| **采购退货出库 ⭐v2.2** | `purchase_return_dlv:create` | 创建 | ✅ | ✅ | ❌ | ❌ | ❌ |
| **采购退货出库 ⭐v2.2** | `purchase_return_dlv:wh_confirm` | 确认出库 | ✅ | ✅ | ❌ | ❌ | ✅ |
| **采购退货出库 ⭐v2.4** | `purchase_return_dlv:fin_confirm` | 财务确认冲应付 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 库存 | `inventory:adjust` | 库存调整 | ✅ | ❌ | ❌ | ❌ | ✅ |
| 库存 | `inventory:transfer` | 调拨 | ✅ | ✅ | ❌ | ❌ | ✅ |
| **盘点** | `stocktaking:create` | 创建盘点 | ✅ | ✅ | ❌ | ❌ | ✅ |
| **盘点** | `stocktaking:audit` | 审核盘点 | ✅ | ✅ | ❌ | ❌ | ❌ |
| **报损** | `damage:create` | 创建报损 | ✅ | ✅ | ❌ | ❌ | ✅ |
| **报损** | `damage:audit` | 审核报损 | ✅ | ✅ | ❌ | ❌ | ❌ |

##### 车销

| 模块 | operation_key | 说明 | admin | supervisor | sales | finance | warehouse |
|------|------|------|:---:|:---:|:---:|:---:|:---:|
| **装车** | `vehicle_load:create` | 创建装车 | ✅ | ✅ | ❌ | ❌ | ✅ |
| **装车** | `vehicle_load:audit` | 审核装车 | ✅ | ✅ | ❌ | ❌ | ❌ |
| **交账** | `settlement:create` | 创建交账 | ✅ | ✅ | ✅ | ❌ | ❌ |
| **交账** | `settlement:audit` | 审核交账 | ✅ | ❌ | ❌ | ✅ | ❌ |

##### 财务类

| 模块 | operation_key | 说明 | admin | supervisor | sales | finance | warehouse |
|------|------|------|:---:|:---:|:---:|:---:|:---:|
| 收付款 | `finance:create` | 创建收/付款 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 收付款 | `finance:audit` | 审核 | ✅ | ❌ | ❌ | ✅ | ❌ |
| **预收付** | `advance:create` | 创建预收/付 | ✅ | ❌ | ❌ | ✅ | ❌ |
| **预收付** | `advance:audit` | 审核 | ✅ | ❌ | ❌ | ✅ | ❌ |
| **费用** | `expense:create` | 创建费用 | ✅ | ✅ | ❌ | ✅ | ❌ |
| **费用** | `expense:audit` | 审核费用 | ✅ | ✅ | ❌ | ✅ | ❌ |
| **费用** | `expense:contract` | 管理合同 | ✅ | ✅ | ❌ | ✅ | ❌ |
| **往来账** | `ledger:view` | 查看往来 | ✅ | ✅(查) | ❌ | ✅ | ❌ |
| **往来账** | `ledger:reconcile` | 对账确认 | ✅ | ❌ | ❌ | ✅ | ❌ |

##### 报表+系统

| 模块 | operation_key | 说明 | admin | supervisor | sales | finance | warehouse |
|------|------|------|:---:|:---:|:---:|:---:|:---:|
| 销售报表 | `report_sales:view` | 查看 | ✅ | ✅(自) | ✅(自) | ❌ | ❌ |
| 采购报表 | `report_purchase:view` | 查看 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 财务报表 | `report_finance:view` | 查看 | ✅ | ❌ | ❌ | ✅ | ❌ |
| **审计日志 ⭐v2.2** | `audit_log:view` | 查看 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 角色 | `role:assign` | 分配权限 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 公司 | `company:config` | 公司设置 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 系统 | `system:config` | 系统设置 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 促销 | `promotion:create` | 创建促销 | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## 十、关键业务数据模型补充

### 10.1 销售单

```sql
CREATE TABLE sales_delivery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_no VARCHAR(30) UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    warehouse_id INTEGER,                         -- 仓库出库（NULL=车销）
    vehicle_id INTEGER,                           -- 车辆出库（NULL=仓库出库）
    total_amount DECIMAL(12,2) NOT NULL,
    cash_amount DECIMAL(12,2) DEFAULT 0,
    wechat_amount DECIMAL(12,2) DEFAULT 0,
    alipay_amount DECIMAL(12,2) DEFAULT 0,
    credit_amount DECIMAL(12,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    -- pending / settling / settled / voided / locked / reversed ⭐v2.3: 去掉delivered
    source_type VARCHAR(20) DEFAULT 'direct',
    void_reason VARCHAR(200),                     -- ⭐v2.2: 作废原因
    originated_from_id INTEGER,                   -- ⭐v2.2: 复制来源单号（作废复开）
    payment_evidence TEXT,                         -- ⭐v2.2: 电子签名/支付流水 JSON
    created_by INTEGER NOT NULL,
    auditor_id INTEGER,
    audited_at DATETIME,
    settled_at DATETIME,
    settlement_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    remark TEXT,
    -- ⭐v2.2 约束
    CHECK (
        (warehouse_id IS NULL AND vehicle_id IS NOT NULL) OR
        (warehouse_id IS NOT NULL AND vehicle_id IS NULL)
    )
);

CREATE TABLE sales_delivery_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    batch_id INTEGER,
    quantity DECIMAL(12,2) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    source_order_item_id INTEGER
);

-- 订单-单据关联
CREATE TABLE order_delivery_link (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sales_order_id INTEGER NOT NULL,
    sales_delivery_id INTEGER NOT NULL,
    UNIQUE(sales_order_id, sales_delivery_id)
);
```

> ⭐v2.4 settlement_snapshot 字段说明：
> 交账审核时写入的 JSON 快照，内容至少包含：
> ```json
> {
>   "sales_deliveries": [{"id": 101, "delivery_no": "XS-001", "amount": 120.00, "cash": 80, "credit": 40}, ...],
>   "return_deliveries": [{"id": 201, "return_no": "RT-001", "amount": 50.00, "refund_cash": 50}, ...],
>   "expenses": [{"id": 301, "category": "油费", "amount": 100}],
>   "summary": {
>     "sales_cash": 1200, "sales_credit": 850, "sales_total": 2050,
>     "return_cash": 200, "return_credit": 120, "return_total": 320,
>     "net_cash": 1000, "net_credit": 730
>   },
>   "audited_at": "2026-05-04T18:30:00+08:00",
>   "auditor_id": 5
> }
> ```
> 用于日后对账追溯：即使关联单据被后续操作修改（如红冲），快照仍保留审核时刻的真实数据。

### 10.2 采购入库单 ⭐v2.2

```sql
-- 采购入库单主表
CREATE TABLE purchase_receipt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_no VARCHAR(30) UNIQUE NOT NULL,       -- 单号：CG-20260504-001
    purchase_order_id INTEGER NOT NULL,            -- 来源采购订单
    supplier_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',          -- pending/confirmed/reversed
    received_by INTEGER NOT NULL,                  -- 收货人（仓管）
    confirmed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    remark TEXT
);

-- 采购入库明细
CREATE TABLE purchase_receipt_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    order_item_id INTEGER,                        -- 来源采购订单明细
    quantity DECIMAL(12,2) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    amount DECIMAL(12,2) NOT NULL
);
```

### 10.3 盘点单

```sql
CREATE TABLE stocktaking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stocktaking_no VARCHAR(30) UNIQUE NOT NULL,
    warehouse_id INTEGER NOT NULL,
    type VARCHAR(20) DEFAULT 'full',
    status VARCHAR(20) DEFAULT 'draft',
    created_by INTEGER NOT NULL,
    auditor_id INTEGER,
    audited_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE stocktaking_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stocktaking_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    book_quantity DECIMAL(12,2) NOT NULL,
    actual_quantity DECIMAL(12,2) NOT NULL,
    diff_quantity DECIMAL(12,2) NOT NULL,
    diff_amount DECIMAL(12,2),
    reason VARCHAR(100)
);
```

### 10.4 费用管理

```sql
CREATE TABLE expense_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30) NOT NULL,
    type VARCHAR(20) DEFAULT 'expense'
);

CREATE TABLE expense (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_no VARCHAR(30) UNIQUE NOT NULL,
    category_id INTEGER NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    payee VARCHAR(50),
    payee_is_employee BOOLEAN DEFAULT 0,          -- ⭐v2.2: 收款人是否内部员工
    status VARCHAR(20) DEFAULT 'pending',
    contract_id INTEGER,
    settlement_id INTEGER,                         -- 可在交账时一并提交
    invoice_url VARCHAR(500),                      -- ⭐v2.2: 发票照片/文件URL
    duplicate_check_hash VARCHAR(64),              -- ⭐v2.2: 重复检测哈希(date+amount+category)
    created_by INTEGER NOT NULL,
    approver_id INTEGER,                           -- 审批人（创建时自动填入直属主管report_to）⭐v2.4
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

> ⭐v2.4: `employee` 表需增加 `report_to` 字段（INTEGER，指向直属主管的 employee_id）。
> 费用创建时，若 `payee_is_employee=TRUE`，自动将 `approver_id` 设为该员工的 `report_to`，由其主管审批。

### 10.5 审计日志

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(30) NOT NULL,
    entity_id INTEGER,
    old_value TEXT,                                -- JSON
    new_value TEXT,                                -- JSON
    ip_address VARCHAR(45),
    user_agent VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 日志只追加，不删除（数据库权限控制）
-- CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
-- CREATE INDEX idx_audit_log_user ON audit_log(user_id, created_at);
-- CREATE INDEX idx_audit_log_action ON audit_log(action, created_at);
```

---

## 十一、现有代码命名迁移对照 — ⭐v2.2 补采购侧

| 层级 | 旧名称 | 新名称 | 说明 |
|------|--------|--------|------|
| DB表 | `sales_orders` | 不变 | 本来就是订单表 |
| 后端Router | `routers/sales.py` | `routers/sales_order.py` + `routers/sales_delivery.py` | 拆分 |
| 后端Router | `routers/purchases.py` | `routers/purchase_order.py` + `routers/purchase_receipt.py` | ⭐v2.2拆分 |
| 后端Schema | `schemas/sales.py` | 同上拆分 | |
| 后端Schema | `schemas/purchases.py` | 同上拆分 | ⭐v2.2 |
| PC路由path | `/sales` | `/sales-orders` | 销售订单页 |
| PC路由path | — | `/sales-deliveries` | 销售单页⭐ |
| PC路由path | `/sales-returns` | 不变 | 退货订单页 |
| PC路由path | — | `/sales-return-deliveries` | 退货单页⭐ |
| PC路由path | `/purchases` | `/purchase-orders` | 采购订单页 |
| PC路由path | — | `/purchase-receipts` | 采购入库单⭐v2.2 |
| PC路由path | — | `/purchase-return-deliveries` | 采购退货出库单⭐v2.2 |
| PC路由path | — | `/vehicle-load` | 装车管理⭐ |
| PC路由path | — | `/settlement` | 交账管理⭐ |
| PC路由path | — | `/audit-log` | 审计日志⭐v2.2 |
| PC组件 | `views/sales/Index.vue` | `views/sales_order/Index.vue` | |
| PC组件 | — | `views/sales_delivery/Index.vue` | ⭐ |
| PC组件 | — | `views/purchase_receipt/Index.vue` | ⭐v2.2 |
| PC组件 | — | `views/vehicle/Index.vue` | ⭐ |
| PC组件 | — | `views/settlement/Index.vue` | ⭐ |
| PC组件 | — | `views/audit_log/Index.vue` | ⭐v2.2 |
| PC菜单 | "销售" | "销售订单" | |
| PC菜单 | — | "销售单" | ⭐ |
| PC菜单 | "采购" | "采购订单" | |
| PC菜单 | — | "采购入库单" | ⭐v2.2 |
| PC菜单 | — | "装车管理" | ⭐ |
| PC菜单 | — | "交账管理" | ⭐ |
| PC菜单 | — | "审计日志" | ⭐v2.2 |
| operation_key | `sales:create` | `sales_order:create` | 订单操作 |
| operation_key | — | `sales_delivery:create` | 单据操作⭐ |
| operation_key | — | `purchase_receipt:create` | 入库操作⭐v2.2 |

---

## 十二、实施建议（分期）— ⭐v2.2 重整

### Phase 0：准备工作（1天）⭐v2.4 审计前置

```
- 数据库 migration（新增表结构，含 audit_log）
- 后端目录重组（sales/purchase 拆分）
- 前端路由重命名、菜单更新

⭐v2.4 审计中间件规范（Day 0 完成，后续开发自动覆盖）：
  ┌─────────────────────────────────────────────────────┐
  │ 1. 在 API 中间件层统一拦截所有 POST/PUT/DELETE 请求  │
  │ 2. 自动提取 user_id、action (method+path)、         │
  │    IP、User-Agent，写入 audit_log 基础字段           │
  │ 3. 敏感状态变更（作废/红冲/审核/交账等）在 Service   │
  │    层显式调用审计服务，记录 old_value/new_value JSON  │
  │ 4. 业务层无需单独写日志代码——中间件层兜底覆盖        │
  │ 5. audit_log 表只有 INSERT 权限，无 UPDATE/DELETE   │
  └─────────────────────────────────────────────────────┘
  
  规范文件：server/middleware/audit.py
  这样 Day 1 开始的所有模块自动被审计覆盖，不存在后期遗漏。
```

### Phase A：P0 核心业务（8-10天）

```
Day 1-2   → 销售单（含直接开单+订单转单+作废/红冲/电子签名/支付流水）
Day 3-4   → 采购入库单 + 采购退货出库单（含财务确认接口）⭐v2.4
Day 5-6   → 盘点单（整仓+部分，含库存锁定）+ 费用管理
Day 7-8   → 财务报表 + 往来账 + 退货单（含仓管确认+财务确认接口）
Day 9-10  → 审计报告（基于 Day 1-8 自动积累的 audit_log 生成操作审计视图）+ 联调 ⭐v2.4
```

> ⭐v2.3 重要：Phase A 暂不引入交账系统（Phase B 才做），销售单的状态机做如下过渡处理：
> - 销售单开单后停留在 `pending`（已扣库存），**不设置 settling/settled 状态**
> - Phase B 引入交账模块时统一升级状态机，并回刷已有单据的状态
> - 或在 Phase A 做「简化交账」功能：手动批量选中销售单 → 一键确认结算，跳过完整交账审核流程
> 
> ⭐v2.3：退货单的仓管确认(`wh_confirm`)和财务确认(`fin_confirm`)接口在 Day 7-8 完成，与往来账/财务模块同步开发。

### Phase B：车销模式 + 交账系统（5-6天）⭐v2.3 明确

```
Day 1-2   → 车辆档案 + 装车管理 + 车上库存（含部分退库）
Day 3-4   → 车销开单 H5端（扫码+快速选品+折扣+电子签名）
Day 5-6   → 交账系统（含 settling 锁定、费用阈值含拆单检测⭐v2.3、金额快照）
           + 状态机升级（Phase A 的 pending 单据统一接入）+ 联调
```

> ⭐v2.3: 交账系统在 Phase B 最后阶段完成，届时：
> - 上线 settling/settled 状态流转
> - 回刷 Phase A 所有未结算的销售单状态
> - 费用拆单检测随交账模块一起上线

### Phase C：P1 完善（5-7天）

```
Day 1-2   → 预收/预付款 + 报损单（含大额审批）
Day 3-4   → 品牌管理 + 渠道管理 + 线路管理 + 客户等级
Day 5     → 销售报表 + 采购报表
Day 6-7   → 员工提成 + 公司设置 + 价格管控 + 联调
```

### Phase D：风控增强（3-4天）⭐v2.2 新增

```
Day 1-2   → 异常交易监控（作废复开分析/单价异常/赊账比例/多单退款）
Day 3     → 客户对账确认（电子对账单）+ 轮岗盘点
Day 4     → 防作弊体系完整联调 + 审计报告
```

---

## 十三、H5 移动端全功能方案（v2.4 补充）

### 13.1 设计原则

**H5 ≠ 仅车销端口。H5 = PC 全功能移动版。**

| 原则 | 说明 |
|------|------|
| 全功能覆盖 | H5 拥有 PC 所有功能模块，非仅车销 |
| 权限驱动展示 | 根据登录用户的角色权限，动态显示/隐藏功能模块 |
| 共用后端 API | H5 和 PC 调用同一套后端接口，零额外后端开发 |
| 一账号多权限 | 一个员工可拥有多个角色（如：业务员+库管），权限取并集 |
| 老板全权限 | `admin` 角色自动拥有所有模块权限 |

### 13.2 技术栈

```
框架：uni-app（Vue3 + Vite）— 支持 H5/微信小程序/App 打包
UI库：Vant 4.x（移动端组件库）
状态管理：Pinia（与 PC 端统一）
路由：uni-app 内置路由 + pages.json 配置
网络：uni.request 封装（拦截器统一处理 token/错误）
```

### 13.3 角色与模块映射

#### 角色定义（与 §4.1 一致）

| 角色 key | 名称 | 说明 |
|----------|------|------|
| `admin` | 老板/管理员 | 全部功能+系统设置 |
| `supervisor` | 主管/文员 | 档案+采购+销售+报表 |
| `sales` | 业务员 | 销售开单、客户拜访、交账 |
| `finance` | 财务 | 收支管理、对账、发票、审核 |
| `warehouse` | 库管 | 库存管理、盘点、出入库确认 |

#### 模块权限映射表

| 模块 module_key | sales | supervisor | warehouse | finance | admin |
|----------------|:-----:|:----------:|:---------:|:-------:|:-----:|
| `home`（首页看板） | ✅ | ✅ | ✅ | ✅ | ✅ |
| `products`（商品管理） | 查 | ✅ | 查 | — | ✅ |
| `customers`（客户管理） | ✅ | ✅ | — | 查 | ✅ |
| `suppliers`（供应商管理） | — | ✅ | — | 查 | ✅ |
| `purchases`（采购管理） | — | ✅ | 确认入库 | ✅ | ✅ |
| `sales`（销售管理） | ✅ | ✅ | — | ✅ | ✅ |
| `inventory`（库存管理） | 查车仓 | ✅ | ✅ | — | ✅ |
| `warehouses`（仓库管理） | — | — | ✅ | — | ✅ |
| `finance`（财务管理） | — | — | — | ✅ | ✅ |
| `reports`（报表中心） | 个人 | ✅ | 库存 | ✅ | ✅ |
| `system`（系统设置） | — | — | — | — | ✅ |

> **说明**：✅ = 完整权限，查 = 只读，— = 不可见。实际权限以 `role_module_permissions` 表为准。

### 13.4 一账号多权限实现

#### 数据模型（已存在）

```
employee_roles 表（多对多）：
  employee_id → role_id
  一个员工可关联多个角色

role_module_permissions 表：
  role_id + module_id → can_view / can_create / can_edit / can_delete
```

#### 权限合并逻辑

```python
# 登录时计算有效权限（取并集）
def get_user_permissions(employee_id, db):
    roles = db.query(EmployeeRole).filter(
        EmployeeRole.employee_id == employee_id
    ).all()

    # admin 角色：直接返回全部权限
    for er in roles:
        if er.role.role_key == 'admin':
            return ALL_PERMISSIONS

    # 非 admin：合并所有角色权限（OR 逻辑）
    permissions = {}
    for er in roles:
        for perm in er.role.module_permissions:
            key = perm.module.module_key
            if key not in permissions:
                permissions[key] = {
                    'can_view': False, 'can_create': False,
                    'can_edit': False, 'can_delete': False
                }
            permissions[key]['can_view'] |= perm.can_view
            permissions[key]['can_create'] |= perm.can_create
            permissions[key]['can_edit'] |= perm.can_edit
            permissions[key]['can_delete'] |= perm.can_delete

    return permissions
```

### 13.5 H5 动态 TabBar 设计

#### 首页 TabBar（底部导航）

根据用户权限动态显示底部 Tab：

```
┌─────────────────────────────────────────────────┐
│                                                 │
│              [页面内容区]                        │
│                                                 │
├──────┬──────┬──────┬──────┬──────┬──────────────┤
│ 首页 │ 销售 │ 仓库 │ 财务 │ 报表 │ 我的（固定）│
│  🏠  │  📋  │  📦  │  💰  │  📊  │    👤       │
└──────┴──────┴──────┴──────┴──────┴──────────────┘
```

#### 各角色默认 Tab 组合

| 角色 | Tab1 | Tab2 | Tab3 | Tab4 | Tab5 |
|------|------|------|------|------|------|
| 业务员 | 首页 | 销售 | 客户 | 业绩 | 我的 |
| 主管/文员 | 首页 | 销售 | 采购 | 库存 | 我的 |
| 库管 | 首页 | 库存 | 盘点 | 装车 | 我的 |
| 财务 | 首页 | 财务 | 对账 | 报表 | 我的 |
| 老板 | 首页 | 销售 | 仓库 | 报表 | 我的 |

> Tab 列表完全由权限动态生成，非硬编码。如果主管同时拥有库存权限，则自动出现"库存"Tab。

### 13.6 H5 实施计划

| 阶段 | 天数 | 内容 |
|------|------|------|
| **H5-0：基础框架** | 1天 | uni-app 项目初始化、Vant 集成、请求封装、权限 store、动态 TabBar |
| **H5-1：核心业务** | 3天 | 首页看板 + 销售开单 + 库存查询 + 客户管理 |
| **H5-2：车销流程** | 2天 | 装车 + 车销开单 + 交账 + 扫码（与 Phase B 联动） |
| **H5-3：仓库+采购** | 2天 | 采购入库确认 + 盘点 + 报损 + 调拨 |
| **H5-4：财务+报表** | 2天 | 费用报销 + 对账确认 + 报表查看 |
| **H5-5：系统+优化** | 1天 | 系统设置（admin）+ 我的 + 消息通知 + 性能优化 |

**总计：约 11 天**（可与 Phase B/C/D 并行开发）

### 13.7 H5 特色功能

| 功能 | 说明 |
|------|------|
| 扫码开单 | 扫商品条码快速添加商品 |
| 电子签名 | 客户签收确认（canvas 签名） |
| 拍照上传 | 退货拍照、报损拍照、凭证拍照 |
| GPS 定位 | 客户拜访签到定位 |
| 离线缓存 | 弱网环境基础数据缓存 |
| 消息推送 | 交账提醒、审批通知 |
| 手势操作 | 左滑删除、下拉刷新、上拉加载 |

> 详细页面清单和目录结构见 `FASTINOUT_DEVELOPMENT_PLAN.md` 第十四章。

---

## 附录A：模块统计

| 分类 | 原有 | v2.1新增 | v2.2新增 | 合计 |
|------|:--:|:--:|:--:|:--:|
| 仪表盘 | 1 | 0 | 0 | 1 |
| 档案类 | 8 | 4 | 0 | **12** |
| 业务类 | 5 | 4 | **+2** | 11 |
| 车销 | 0 | 2 | 0 | 2 |
| 财务类 | 1 | 3 | 0 | 4 |
| 报表类 | 1 | 3 | 0 | 4 |
| 风控 | 0 | 0 | **+1** | 1 |
| 营销类 | 1 | 0 | 0 | 1 |
| 系统类 | 2 | 1 | 0 | 3 |
| **合计** | **19** | **17** | **+3** | **39** |

> 模块表中 DB 注册 **39** 个页面入口（39条 INSERT），与 §9.2 一致 ⭐v2.3 对齐。
> 仪表盘1 + 档案12 + 业务11 + 车销2 + 财务4 + 报表4 + 风控1 + 营销1 + 系统3 = **39**。
> 对比舟谱120项，本次(P0+P1+车销+风控)完成后覆盖约 **60项核心业务**，覆盖率从18%提升至 **50%**。

## 附录B：状态流转速查卡

```
【销售订单】draft → pending → audited → converted
                    ↓跨日      
                  locked

【销售单⭐v2.3】pending(已扣库存,当日可作废) ──交账提交──→ settling ──审核──→ settled
               ↓当日                  ↓锁定  ↙驳回⭐v2.4  ↓锁定
             voided(须填原因,库存回滚)      pending(解绑恢复)
               ↓复制
             新pending(标注原单号)
               ↓跨日⭐v2.3
             locked → 只能红冲(reversed)


【采购入库单】pending → confirmed(仓管收货+库存增加)
                      → reversed(红冲)

【采购退货出库单⭐v2.4】pending → warehouse_confirmed(仓管出库)
                               → finance_confirmed(财务确认冲应付)
                               → settled

【退货单⭐v2.4】pending → warehouse_confirmed(仓管+拍照)
                       → finance_confirmed(财务确认冲账,非车销终态)
                       → settled(交账审核通过时自动触发)

【盘点单】  draft → pending → auditing → audited → adjusted

【报损单】  draft → pending → audited → executed

【交账单⭐v2.4】pending → audited (锁关联销售单+退货单,写快照,费用拆单检测)
                    ↘ rejected (退回修改,解绑恢复pending)

【装车单】  draft → pending → loaded → partial_return → returned

【审计日志】Phase 0 中间件拦截所有 POST/PUT/DELETE → INSERT audit_log（只追加不可删）
```
