# FastInOut 代码审计与后续开发方案

> 📅 编制：2026-05-04 | 👤 Hermes小A | 基于 v2.4 方案 + 代码实际状态

---

## 一、代码现状审计

### 1.1 已有模块 vs v2.4 对照

| v2.4 模块 | 当前代码 | 状态 | 差距 |
|-----------|---------|:---:|------|
| 销售订单 | `sales_orders` (SalesOrder) | ⚠️ | 名称对，但 status=INT(0草稿/1确认/2出库/3关闭)，缺少 audited/converted/locked 字符串枚举 |
| 销售单 | `sales_stockouts` (SalesStockout) | ❌ | **名不对**（应该叫 SalesDelivery）；缺少收款方式拆分、settling/settled 状态、作废原因、电子签名等 |
| 退货订单 | 无独立表 | ❌ | **缺失**。目前 sales_returns 直接关联 stockout（跳过了订单层） |
| 退货单 | `sales_returns` (SalesReturn) | ⚠️ | 名称接近但缺少仓管确认/财务确认状态、拍照存证 |
| 采购订单 | `purchase_orders` (PurchaseOrder) | ⚠️ | status=INT 枚举需改字符串 |
| 采购入库单 | `purchase_stockins` (PurchaseStockin) | ❌ | **名不对**（应该叫 PurchaseReceipt）；缺少财务确认 |
| 采购退货 | `purchase_returns` (PurchaseReturn) | ⚠️ | 目前是订单层；缺少采购退货出库单(PurchaseReturnDelivery) |
| 盘点单 | `inventory_checks` (InventoryCheck) | ⚠️ | 缺整仓锁定、差异审核流 |
| 库存管理 | `inventory` + `inventory_transfers` | ✅ | 基础功能可用 |
| 收付款 | `finance` | ✅ | 基础功能可用 |
| 角色权限 | `roles` + permissions_json | ❌ | **严重不足**：JSON字符串权限，无 module_key/operation_key 三级模型 |
| 员工管理 | `employees` (Employee) | ⚠️ | **缺 report_to 字段** |
| 商品管理 | `products` (Product) | ⚠️ | **缺 min_price 字段** |
| 审计日志 | 无 | ❌ | **完全缺失** |
| 车销系统 | 无 | ❌ | 装车/交账/车上库存全部缺失 |
| 费用管理 | 无 | ❌ | expense/expense_category/expense_contract 全部缺失 |
| 往来账 | 无 | ❌ | 全部缺失 |
| 预收/预付款 | 无 | ❌ | 全部缺失 |
| 报损单 | 无 | ❌ | 全部缺失 |
| 品牌/渠道/线路/客户等级/员工提成 | 无 | ❌ | 全部缺失 |
| 销售/采购/财务报表 | `reports/` 部分 | ❌ | 仅利润/库存/排行，缺少完整报表体系 |

### 1.2 关键架构缺陷

```
⚠️ 角色权限：permissions_json = '["sales","customers","*"]'
   → 无 module_key + operation_key 精细控制
   → 无数据权限（只能看自己路线客户/仓库）

⚠️ 状态机：全部用 INT 枚举（status=0/1/2/3）
   → 无法区分 audited vs converted vs locked vs voided
   → 无法支持 v2.4 的 8 态流转

⚠️ 命名混乱：
   sales_stockouts → 应改为 sales_deliveries
   purchase_stockins → 应改为 purchase_receipts
   sales_returns 直接关联 stockout_id → 缺少独立退货订单层

⚠️ 缺少中间件：
   - 无审计日志中间件
   - 无跨日锁定检查
   - 无 settling 状态保护
```

### 1.3 可保留利用的部分

| 组件 | 处理方式 |
|------|---------|
| `inventory` + `inventory_transfers` | **保留**，接口基本对齐 |
| `finance` 基础收付款 | **保留**，扩展对接应收/应付自动生成 |
| `customers/suppliers/products` CRUD | **保留**，后续扩展字段 |
| `InventoryCheck` | **重命名**为 Stocktaking + 扩展审核流 |
| PC 端 Layout + Dashboard | **保留**，菜单动态渲染 |
| 路由守卫 (token check) | **保留**，需加权限检查 |

---

## 二、开发分期总览

```
Phase 0: 基础设施（1天）          ← 立即开始
Phase A: P0 核心业务（8-10天）     ← 销售单/采购入库/盘点/费用/财报/往来账/退货单/审计
Phase B: 车销 + 交账（5-6天）      ← 装车/车上库存/车销开单/交账系统
Phase C: P1 完善（5-7天）          ← 档案扩充/报损/预收付/报表/价格管控
Phase D: 风控增强（3-4天）         ← 异常监控/对账确认/轮岗盘点
```

---

## 三、Phase 0：基础设施（1天）🔴 最高优先级

### 3.0 目标
完成数据模型升级、审计中间件、权限模型重构——**不改业务逻辑**，确保现有功能不受影响。

### 3.0.1 数据库 Migration

#### A. 新增/修改表

```sql
-- ═══ 权限模型升级 ═══

-- 1. role 表扩展（保留兼容旧 permissions_json，新增细粒度字段）
ALTER TABLE roles ADD COLUMN role_key VARCHAR(20);
ALTER TABLE roles ADD COLUMN is_system BOOLEAN DEFAULT 0;
ALTER TABLE roles ADD COLUMN sort_order INTEGER DEFAULT 0;
ALTER TABLE roles ADD COLUMN status VARCHAR(10) DEFAULT 'active';

UPDATE roles SET role_key = 'admin', is_system = 1, sort_order = 1 WHERE name = '管理员';
UPDATE roles SET role_key = 'sales', is_system = 1, sort_order = 3 WHERE name = '业务员';
UPDATE roles SET role_key = 'warehouse', is_system = 1, sort_order = 5 WHERE name = '仓管';
UPDATE roles SET role_key = 'finance', is_system = 1, sort_order = 4 WHERE name = '财务';
-- supervisor 不存在则插入
INSERT OR IGNORE INTO roles (name, role_key, is_system, sort_order, description) 
VALUES ('主管/文员', 'supervisor', 1, 2, '档案+采购+销售+报表');

-- 2. module 表（新增）
CREATE TABLE IF NOT EXISTS module (
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
-- 预置 39 个模块（见 v2.4 §9.2 INSERT 语句）

-- 3. role_module_permission 表（新增）
CREATE TABLE IF NOT EXISTS role_module_permission (
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

-- 4. operation_permission 表（新增）
CREATE TABLE IF NOT EXISTS operation_permission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    operation_key VARCHAR(50) NOT NULL,
    allowed BOOLEAN DEFAULT 0,
    UNIQUE(role_id, operation_key)
);

-- ═══ 审计日志 ═══

-- 5. audit_log 表（新增）
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(30) NOT NULL,
    entity_id INTEGER,
    old_value TEXT,      -- JSON
    new_value TEXT,      -- JSON
    ip_address VARCHAR(45),
    user_agent VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ═══ employee 扩展 ═══

-- 6. employee 加 report_to
ALTER TABLE employees ADD COLUMN report_to INTEGER REFERENCES employees(id);

-- ═══ product 扩展 ═══

-- 7. product 加 min_price
ALTER TABLE products ADD COLUMN min_price FLOAT DEFAULT 0;
```

#### B. 已有表改名（向后兼容迁移）

```sql
-- 这些改名是破坏性的，需要配合后端代码一起改
-- 建议：先创建新表 + 数据迁移 + 改代码 + 删旧表

-- sales_stockouts → sales_deliveries
CREATE TABLE sales_deliveries (
    -- 复制结构 + 新增字段
);
INSERT INTO sales_deliveries SELECT ... FROM sales_stockouts;

-- purchase_stockins → purchase_receipts
CREATE TABLE purchase_receipts (
    -- 复制结构 + 新增字段
);
INSERT INTO purchase_receipts SELECT ... FROM purchase_stockins;
```

> ⚠️ **Phase 0 建议只建新表不改旧表**：现有 API 继续用旧表跑，新模块用新表。Phase A 逐步迁移，降低风险。

### 3.0.2 审计中间件（Day 0 完成）

**文件：`server/middleware/audit.py`**

```python
from fastapi import Request
from database import SessionLocal
from models.audit_log import AuditLog
import json

async def audit_middleware(request: Request, call_next):
    """拦截所有 POST/PUT/DELETE，自动记录 audit_log"""
    response = await call_next(request)
    
    if request.method in ("POST", "PUT", "DELETE"):
        db = SessionLocal()
        try:
            user_id = getattr(request.state, 'user_id', None)
            if user_id:
                log = AuditLog(
                    user_id=user_id,
                    action=f"{request.method}:{request.url.path}",
                    entity_type=request.url.path.split('/')[2] if len(request.url.path.split('/')) > 2 else 'unknown',
                    ip_address=request.client.host if request.client else '',
                    user_agent=request.headers.get('user-agent', '')
                )
                db.add(log)
                db.commit()
        except:
            pass
        finally:
            db.close()
    
    return response
```

**在 `main.py` 中注册：**
```python
from middleware.audit import audit_middleware
app.middleware("http")(audit_middleware)
```

### 3.0.3 状态枚举标准化

**文件：`server/utils/status.py`**

```python
class SalesOrderStatus:
    DRAFT = "draft"
    PENDING = "pending"
    AUDITED = "audited"
    CONVERTED = "converted"
    LOCKED = "locked"

class SalesDeliveryStatus:
    PENDING = "pending"       # 已开单,库存已扣,当日可作废
    SETTLING = "settling"     # 已提交交账,禁止编辑
    SETTLED = "settled"       # 交账审核通过,彻底锁定
    VOIDED = "voided"         # 当日作废,库存回滚
    LOCKED = "locked"         # 跨日锁定
    REVERSED = "reversed"     # 红冲

class PurchaseReceiptStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REVERSED = "reversed"

class ReturnDeliveryStatus:
    PENDING = "pending"
    WAREHOUSE_CONFIRMED = "warehouse_confirmed"
    FINANCE_CONFIRMED = "finance_confirmed"
    SETTLED = "settled"
```

### 3.0.4 目录重组

```
server/
├── routers/
│   ├── sales_order.py      ← 从 sales.py 拆出（销售订单）
│   ├── sales_delivery.py   ← 新增（销售单）
│   ├── sales_return.py     ← 退货订单（新增，独立于退货单）
│   ├── sales_return_dlv.py ← 新增（退货单）
│   ├── purchase_order.py   ← 从 purchases.py 拆出
│   ├── purchase_receipt.py ← 新增（采购入库单）
│   ├── purchase_return_dlv.py ← 新增（采购退货出库单）
│   └── ...                 ← 保留其余
├── middleware/
│   ├── __init__.py
│   └── audit.py            ← 新增
├── utils/
│   └── status.py           ← 新增（状态枚举）
└── main.py                 ← 注册新路由 + 中间件
```

---

## 四、Phase A：P0 核心业务（8-10天）

### Day 1-2：销售单 ⭐ 最核心模块

**当前状态**：`sales_stockouts` 表存在，但功能简陋

**修改清单**：

| 文件 | 修改 |
|------|------|
| `models/sales.py` | 新增 `SalesDelivery` (替换 SalesStockout)；加字段 cash_amount/wechat_amount/alipay_amount/credit_amount/void_reason/originated_from_id/payment_evidence；CHECK(warehouse_id XOR vehicle_id) |
| `schemas/sales.py` | 拆出 `sales_delivery.py`，Pydantic 模型 |
| `routers/sales_delivery.py` | **重写**：开单/作废/红冲/列表/详情/复制开单 |
| `routers/sales_order.py` | 从 `sales.py` 拆出，API prefix → `/api/sales-orders` |
| `pc/src/router/index.js` | `/sales` → `/sales-orders`；新增 `/sales-deliveries` |
| `pc/src/views/sales/Index.vue` | 重命名为 `sales_order/Index.vue` |
| `pc/src/views/sales_delivery/Index.vue` | **新建**：销售单管理页 |

**关键业务逻辑**：

```
开单流程：
  1. 选择客户 → 选择商品 → 填写数量/单价
  2. 选择收款方式（现金/微信/支付宝/赊账，可混合）
  3. 确认开单 → status='pending' → 扣库存(inventory/vehicle_inventory)
  4. 开单即确认，无需额外"确认"动作（v2.3）

作废（当日）：
  1. 必须填 void_reason
  2. status → 'voided'
  3. 库存回滚（inventory.quantity += delivery_item.quantity）

红冲（跨日/已交账）：
  1. status → 'reversed'
  2. 生成等额负数冲销单
  3. 库存回滚

复制开单（从作废单）：
  1. 自动填入原商品/数量/客户
  2. 新单 originated_from_id = 原作废单 ID
  3. 前端显示 "复制自 XS-xxx(已作废)"
```

**库存扣减时机**：
- 车销直接开单 → 扣车上库存（Phase B 实现）
- 仓库出库 → 扣仓库库存（Day 1-2 实现）
- 库存不足 → 拒绝开单，提示具体缺货商品

### Day 3-4：采购入库单 + 采购退货出库单

**当前状态**：`purchase_stockins` 存在，`purchase_returns` 是订单层

**修改清单**：

| 文件 | 修改 |
|------|------|
| `models/purchase.py` | 重命名 PurchaseStockin → PurchaseReceipt；新增 PurchaseReturnDelivery |
| `routers/purchase_receipt.py` | 确认收货、列表、详情 |
| `routers/purchase_return_dlv.py` | 确认出库、财务确认、红冲 |
| `pc/src/views/purchase_receipt/Index.vue` | 采购入库单管理 |

**关键逻辑**：
- 采购入库单：`pending → confirmed`（仓管确认，库存增加，应付生成）
- 采购退货出库单：`pending → warehouse_confirmed → finance_confirmed`（仓管出库→财务确认冲应付）

### Day 5-6：盘点单 + 费用管理

**盘点单**：基于现有 `inventory_checks` 扩展
- 新增整仓锁定逻辑（盘点期间禁止出入库）
- 差异超过5%需主管复核
- 审核通过后自动更新库存

**费用管理**：全新模块
- 费用支出/费用合同/其他收入
- 员工自报需上级审批（approver_id = report_to）
- 发票必传

### Day 7-8：财务报表 + 往来账 + 退货单

**退货单**：扩展 `sales_returns`
- 新增 `warehouse_confirmed → finance_confirmed` 状态
- 退货拍照上传
- 第二人质检（!= 业务员本人）
- 单次>1000元需主管审批

**财务报表**：资产负债表 + 利润表 + 科目余额表

**往来账**：客户/供应商应收应付明细

### Day 9-10：审计报告 + 联调

- 基于 Phase 0 中间件自动积累的 audit_log 生成操作审计视图
- 全模块联调测试

---

## 五、Phase B：车销 + 交账（5-6天）

### Day 1-2：车辆档案 + 装车管理 + 车上库存

新建表：
- `vehicle` — 车辆档案
- `vehicle_inventory` — 车上库存（虚拟库存）
- `vehicle_load` — 装车单（draft→pending→loaded→partial_return→returned）
- `vehicle_return` — 退库记录（支持明细级分批退库）

装车逻辑：
```
仓库库存 → 装车单审核 → 车上库存增加、仓库库存扣减
```

### Day 3-4：车销开单 H5端

- H5 端扫条码/快速选品/折扣
- 客户电子签名确认
- 扣车上库存

### Day 5-6：交账系统

- 销售单 settling 锁定 + 费用阈值 + 拆单检测
- 退货纳入交账（实交现金 = 销售现金 - 退货现金）
- 金额快照 settlement_snapshot
- **状态机升级脚本**：将 Phase A 中 pending 的单据接入新状态机

> ⚠️ **Phase B Day 1 就写状态迁移脚本并在测试环境跑**，不要等到 Day 5-6。

---

## 六、Phase C：P1 完善（5-7天）

| 模块 | 说明 |
|------|------|
| 预收/预付款 | advance_payment 表 |
| 报损单 | damage_report，审核后扣库存 |
| 品牌/渠道/线路/客户等级 | 档案扩充，纯 CRUD |
| 销售报表 | 销售明细 + 5维度汇总 |
| 采购报表 | 采购明细 + 汇总 |
| 员工提成 | 按销售额/回款计算 |
| 公司设置 | 企业信息 + 打印模板 + settlement_expense_auto_approve_limit |
| 价格管控 | 商品最低售价，低于需主管审批 |

---

## 七、Phase D：风控增强（3-4天）

| 机制 | 说明 |
|------|------|
| 异常交易监控 | 作废复开分析/单价异常/赊账比例/多单退款 |
| 客户对账确认 | 电子对账单 |
| 轮岗盘点 | 他人复核 |

---

## 八、立即需要修改的代码（Phase 0 范围）

### 8.1 数据库（执行 migration 脚本）

⬜ 1. `employees` 加 `report_to` 字段
⬜ 2. `products` 加 `min_price` 字段
⬜ 3. `roles` 加 `role_key/is_system/sort_order/status` 字段
⬜ 4. 新建 `module` 表 + 预置 39 条数据
⬜ 5. 新建 `role_module_permission` 表
⬜ 6. 新建 `operation_permission` 表
⬜ 7. 新建 `audit_log` 表
⬜ 8. 新建 `sales_deliveries` 表（替代 sales_stockouts，带新字段）
⬜ 9. 新建 `purchase_receipts` 表（替代 purchase_stockins）

### 8.2 后端

⬜ 10. 创建 `server/middleware/__init__.py`
⬜ 11. 创建 `server/middleware/audit.py`（审计中间件）
⬜ 12. 创建 `server/utils/status.py`（状态枚举）
⬜ 13. `main.py` 注册审计中间件
⬜ 14. `routers/sales.py` → 拆分为 `sales_order.py` + 创建 `sales_delivery.py`
⬜ 15. `routers/purchases.py` → 拆分为 `purchase_order.py` + 创建 `purchase_receipt.py` + `purchase_return_dlv.py`
⬜ 16. `schemas/` 对应拆分
⬜ 17. `models/sales.py` 新增 SalesDelivery model
⬜ 18. `models/purchase.py` 新增 PurchaseReceipt + PurchaseReturnDelivery model
⬜ 19. `models/employee.py` 加 report_to 字段
⬜ 20. `models/product.py` 加 min_price 字段
⬜ 21. `models/role.py` 加新字段

### 8.3 前端

⬜ 22. `pc/src/router/index.js`：`/sales` → `/sales-orders`（meta title → "销售订单"）
⬜ 23. `pc/src/router/index.js`：新增 `/sales-deliveries`（meta title → "销售单"）
⬜ 24. `pc/src/router/index.js`：`/purchases` → `/purchase-orders`（meta title → "采购订单"）
⬜ 25. `pc/src/views/sales/Index.vue` → 重命名目录为 `sales_order/`
⬜ 26. 新建 `pc/src/views/sales_delivery/Index.vue`（销售单管理页）

---

## 九、风险与建议

| 风险 | 缓解措施 |
|------|---------|
| 表改名导致现有功能崩溃 | Phase 0 只建新表不改旧表，旧 API 照常跑 |
| 状态迁移脚本有 bug | Phase B Day 1 就写并在测试环境跑 |
| 审计日志中间件性能 | 异步写入，不阻塞请求 |
| 前端菜单重命名导致链接失效 | 保留旧路由重定向 |

**最关键的三件事（不做后面都白做）**：
1. Phase 0 立即把 audit_log 中间件架好
2. Phase A Day 1-2 把销售单状态机做对（pending→settling→settled 不含 delivered）
3. Phase B Day 1 就写状态迁移脚本
