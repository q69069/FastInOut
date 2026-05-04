# FastInOut 完整后续开发计划

> 📅 编制：2026-05-04 | 👤 Hermes小A | 版本：v1.1（小C审查修订）
>
> **v1.1 修订内容**（基于代码实际状态审查）：
> 1. Phase 0 从1天缩减为0.5天 — 三级权限表/模块表/角色扩展字段已全部建好
> 2. `audit_log` → `http_audit_log` — 避免与现有审批记录表 `audit_logs` 命名冲突
> 3. 车销模块标注现有模型 — VehicleSalesOut/Return/Loss 已有简化CRUD，Phase B需重建完整体系
> 4. 新增「前端同步改动清单」— 目录重组需同步修改PC+H5两端API路径
> 5. 数据过滤/权限缓存/预收付冲抵标注为已完成
> 
> **本文档是 FastInOut 项目的唯一开发入口。**
> 包含：完整架构、分期计划、逐模块实现细节、状态机定义、数据库迁移脚本、前后端改动清单、测试策略。
>
> 配套文档：`FastInOut_PC_H5统一权限_实施细化方案_v2.4.md`（产品方案基线）

---

## 目录

- [一、架构总览](#一架构总览)
- [二、当前代码审计](#二当前代码审计)
- [三、分期开发总览](#三分期开发总览)
- [四、Phase 0：基础设施](#四phase-0基础设施-day-1)
- [五、Phase A：P0 核心业务](#五phase-ap0-核心业务-8-10天)
- [六、Phase B：车销 + 交账](#六phase-b车销--交账-5-6天)
- [七、Phase C：P1 完善](#七phase-cp1-完善-5-7天)
- [八、Phase D：风控增强](#八phase-d风控增强-3-4天)
- [九、状态机完整定义](#九状态机完整定义)
- [十、数据库迁移完整脚本](#十数据库迁移完整脚本)
- [十一、前后端改动清单](#十一前后端改动清单)
- [十二、测试策略](#十二测试策略)
- [十三、风险与缓解](#十三风险与缓解)

---

## 一、架构总览

### 1.1 命名规范（最高优先级，所有开发人员必须遵守）

```
订单层（不扣库存，可改可撤）：
  销售订单          sales_order        ← 原代码"sales"、DB表 sales_orders
  退货订单          sales_return       ← 退货申请（订单层）
  采购订单          purchase_order     ← 原代码"purchases"、DB表 purchase_orders
  采购退货单        purchase_return    ← 向供应商退货申请（订单层）

单据层（扣库存，不可撤，记财务账）：
  销售单            sales_delivery     ← 实际出库凭证，DB表 sales_deliveries ⭐
  退货单            sales_return_dlv   ← 实际退货入库凭证 ⭐
  采购入库单        purchase_receipt   ← 采购入库凭证 ⭐
  采购退货出库单    purchase_return_dlv ← 采购退货执行凭证 ⭐
```

**操作权限命名规范**：`module_key:action`（如 `sales_delivery:create`）

### 1.2 技术栈

```
后端：Python FastAPI + SQLAlchemy + SQLite
前端(PC)：Vue3 + Element Plus + Vite
前端(H5)：Vue3 + Vant（Phase B 车销）
小程序：微信原生（后续）
```

### 1.3 目录结构（目标）

```
FastInOut/
├── server/
│   ├── main.py                     ← 应用入口
│   ├── database.py                 ← 数据库配置
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── audit.py               ← 审计中间件 ⭐
│   ├── models/                     ← SQLAlchemy 模型
│   │   ├── sales_order.py         ← 销售订单
│   │   ├── sales_delivery.py      ← 销售单 ⭐
│   │   ├── sales_return.py        ← 退货订单
│   │   ├── sales_return_dlv.py    ← 退货单 ⭐
│   │   ├── purchase_order.py      ← 采购订单
│   │   ├── purchase_receipt.py    ← 采购入库单 ⭐
│   │   ├── purchase_return_dlv.py ← 采购退货出库单 ⭐
│   │   ├── vehicle.py             ← 车辆/装车/交账 ⭐Phase B
│   │   ├── expense.py             ← 费用管理 ⭐
│   │   ├── stocktaking.py         ← 盘点单 ⭐
│   │   ├── damage_report.py       ← 报损单 ⭐Phase C
│   │   ├── audit_log.py           ← 审计日志 ⭐
│   │   ├── role.py / module.py / permission.py ← 权限 ⭐
│   │   └── ... (保留其余)
│   ├── routers/                    ← API 路由（与 models 一一对应）
│   ├── schemas/                    ← Pydantic 数据模型
│   ├── services/                   ← 业务逻辑层 ⭐
│   │   ├── inventory_service.py   ← 库存扣减/回滚
│   │   ├── audit_service.py       ← 审计日志记录
│   │   └── settlement_service.py  ← 交账逻辑 Phase B
│   └── utils/
│       └── status.py               ← 状态枚举 ⭐
├── pc/                             ← PC 管理端
│   └── src/
│       ├── views/
│       │   ├── sales_order/        ← 销售订单管理 ⭐改名
│       │   ├── sales_delivery/     ← 销售单管理 ⭐新建
│       │   ├── purchase_order/     ← 采购订单管理 ⭐改名
│       │   ├── purchase_receipt/   ← 采购入库单 ⭐新建
│       │   ├── settlement/         ← 交账管理 ⭐Phase B
│       │   ├── audit_log/          ← 审计日志 ⭐
│       │   └── ... (保留其余)
│       └── router/index.js         ← 路由 + 守卫
├── docs/                           ← 本文档 + 方案文档
└── data/                           ← SQLite 数据库文件
```

---

## 二、当前代码审计

### 2.1 已有模块 vs v2.4 目标对照

| v2.4 模块 | 当前代码 | 状态 | 差距 |
|-----------|---------|:---:|------|
| 销售订单 | `sales_orders` (SalesOrder) | ⚠️ | status 用 INT 枚举，缺 audited/converted/locked |
| **销售单** | `sales_stockouts` (SalesStockout) | ❌ | **名不对**（应叫 SalesDelivery）；缺收款拆分/状态/作废原因 |
| 退货订单 | 无 | ❌ | 缺失（当前 sales_returns 直接关联出库单，跳过了订单层） |
| **退货单** | `sales_returns` (SalesReturn) | ⚠️ | 缺仓管确认/财务确认状态、拍照 |
| 采购订单 | `purchase_orders` (PurchaseOrder) | ⚠️ | status INT 枚举 |
| **采购入库单** | `purchase_stockins` (PurchaseStockin) | ❌ | **名不对**（应叫 PurchaseReceipt） |
| 采购退货 | `purchase_returns` (PurchaseReturn) | ⚠️ | 订单层；缺执行凭证层 |
| **盘点单** | `inventory_checks` (InventoryCheck) | ⚠️ | 缺整仓锁定、差异审核 |
| **费用管理** | 无 | ❌ | 完全缺失 |
| **往来账** | 无 | ❌ | 完全缺失（但客户/供应商对账端点已有） |
| **车销系统** | `vehicle_sales_outs`/`vehicle_returns`/`vehicle_losses` | ⚠️ | 已有简化CRUD，缺Vehicle主档/VehicleInventory/VehicleLoad/Settlement |
| **审计日志** | `operation_logs`表已有 | ⚠️ | 缺 old_value/new_value diff 跟踪和 HTTP 自动拦截中间件 |
| 角色权限 | 三级模型已建好 | ✅ | module/role_module_permission/operation_permission 表+服务层已就位，**仅 auth 中间件还在用旧 JSON** |
| 员工 | `employees` | ⚠️ | 缺 `report_to` |
| 商品 | `products` | ⚠️ | 缺 `min_price` |
| 数据过滤 | `DataFilter.apply_scope()` | ✅ | 已实现，已在多个 router 使用 |
| 权限缓存 | `utils/cache.py` SimpleCache | ✅ | 5分钟TTL，登录/角色变更时自动失效 |
| 预收/预付冲抵 | `finance.py` | ✅ | `/pre-receipt`、`/pre-payment`、`/pre-to-receivable`、`/pre-to-payable` 已实现 |

### 2.2 架构硬伤（v1.1 修订）

| # | 硬伤 | 后果 | 当前状态 |
|---|------|------|---------|
| 1 | auth 中间件仍用 `permissions_json` | 三级权限模型已建但未接入中间件 | **半完成** — 表+服务层就位，需迁移中间件 |
| 2 | 状态全是 INT(0/1/2/3) | 8 态流转(pending/settling/settled/voided/locked...)无法表达 | **未开始** |
| 3 | 无 HTTP 审计中间件 | 防作弊体系第一块砖就没铺 | **未开始** — `operation_logs` 表有但无自动拦截 |

> ⚠️ **Phase 0 需解决硬伤 #2 和 #3，硬伤 #1 已半完成（中间件迁移可在 Phase A 逐步推进）。**

---

## 三、分期开发总览

```
Phase 0: 基础设施（0.5天）        ← 立即开始（v1.1修订：权限表已建好，工作量减半）
  ├── 数据库 Migration（新表+字段，跳过权限表/模块表）
  ├── HTTP 审计中间件 + http_audit_log 表
  ├── 状态枚举定义
  ├── services 层（inventory_service）
  └── 目录重组（改名不改逻辑）+ 前端同步

Phase A: P0 核心业务（8-10天）
  Day 1-2: 销售单（最核心，状态最复杂）
  Day 3-4: 采购入库单 + 采购退货出库单
  Day 5-6: 盘点单 + 费用管理
  Day 7-8: 财务报表 + 往来账 + 退货单
  Day 9-10: 审计报告 + 全模块联调

Phase B: 车销 + 交账（5-6天）
  Day 1-2: 车辆档案 + 装车管理 + 车上库存
  Day 3-4: 车销开单 H5端
  Day 5-6: 交账系统 + 状态机升级

Phase C: P1 完善（5-7天）
  预收付 + 报损 + 档案扩充 + 报表 + 提成 + 公司设置 + 价格管控

Phase D: 风控增强（3-4天）
  异常监控 + 对账确认 + 轮岗盘点
```

---

## 四、Phase 0：基础设施（0.5天）

### 目标
建好地基，不改业务逻辑，确保现有功能不受影响。

### 4.0 已完成项（v1.1 标注）

> 以下在前期开发中已实现，Phase 0 **跳过**：
> - ✅ roles 扩展字段（role_key/is_system/sort_order/status）— 模型已加，auto_migrate 自动处理
> - ✅ module 表 — 模型 `models/module.py` 已建，19个模块种子数据已初始化
> - ✅ role_module_permission 表 — 模型 `models/role_module_permission.py` 已建
> - ✅ operation_permission 表 — 模型 `models/operation_permission.py` 已建
> - ✅ employee_roles 多对多表 — 模型 `models/employee_role.py` 已建
> - ✅ PermissionService 服务层 — `auth/permission_service.py` 已实现
> - ✅ PermissionChecker + DataFilter — `auth/permissions.py` 已实现
> - ✅ 权限缓存 — `utils/cache.py` SimpleCache 5分钟TTL
> - ✅ 预收/预付冲抵 — `finance.py` 4个端点已实现
> - ✅ 客户/供应商对账 — `sales.py`/`purchases.py` statement 端点已有

### 4.1 数据库 Migration

**文件：`server/migrations/001_phase0_baseline.sql`**

```sql
-- ═══════════════════════════════════════════
-- Phase 0 Migration v1.1：仅新建表+扩展字段
-- 权限表/模块表/角色扩展 已在 auto_migrate 中处理，此处跳过
-- ═══════════════════════════════════════════

-- 1. http_audit_log 表（HTTP请求审计，区别于现有 audit_logs 审批记录表）
CREATE TABLE IF NOT EXISTS http_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    method VARCHAR(10) NOT NULL,
    path VARCHAR(200) NOT NULL,
    entity_type VARCHAR(30),
    entity_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. employee 扩展
ALTER TABLE employees ADD COLUMN report_to INTEGER REFERENCES employees(id);

-- 3. product 扩展
ALTER TABLE products ADD COLUMN min_price FLOAT DEFAULT 0;

-- 4. 新建 sales_deliveries（替代 sales_stockouts）
CREATE TABLE IF NOT EXISTS sales_deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_no VARCHAR(30) UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    warehouse_id INTEGER,
    vehicle_id INTEGER,
    total_amount FLOAT DEFAULT 0,
    cash_amount FLOAT DEFAULT 0,
    wechat_amount FLOAT DEFAULT 0,
    alipay_amount FLOAT DEFAULT 0,
    credit_amount FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    source_type VARCHAR(20) DEFAULT 'direct',
    void_reason VARCHAR(200),
    originated_from_id INTEGER,
    payment_evidence TEXT,
    created_by INTEGER NOT NULL,
    auditor_id INTEGER,
    audited_at DATETIME,
    settled_at DATETIME,
    settlement_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    remark TEXT,
    CHECK ((warehouse_id IS NULL AND vehicle_id IS NOT NULL) OR
           (warehouse_id IS NOT NULL AND vehicle_id IS NULL))
);

-- 5. 新建 purchase_receipts（替代 purchase_stockins）
CREATE TABLE IF NOT EXISTS purchase_receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_no VARCHAR(30) UNIQUE NOT NULL,
    purchase_order_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    total_amount FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    received_by INTEGER NOT NULL,
    confirmed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    remark TEXT
);

-- 6. employee.report_to 初始化
UPDATE employees SET report_to = 1 WHERE report_to IS NULL AND id != 1;
```

### 4.2 审计中间件

**文件：`server/middleware/__init__.py`**（已存在，空文件）

**文件：`server/middleware/audit.py`**

```python
from fastapi import Request
from database import SessionLocal
from models.http_audit_log import HttpAuditLog
import json
import logging

logger = logging.getLogger(__name__)

async def audit_middleware(request: Request, call_next):
    """拦截所有 POST/PUT/DELETE，自动记录 http_audit_log。

    基础字段（user_id, method, path, entity_type, IP）在中间件层自动填写。
    敏感状态变更的 old_value/new_value 在 Service 层显式调用 audit_service.log_change()。

    注意：不与现有 audit_logs（审批记录表）混淆。
    """
    response = await call_next(request)

    if request.method in ("POST", "PUT", "DELETE"):
        db = SessionLocal()
        try:
            user_id = getattr(request.state, 'user_id', None)
            if user_id:
                # 从 path 提取 entity_type（如 /api/sales-deliveries/123 → sales-deliveries）
                path_parts = request.url.path.strip('/').split('/')
                entity_type = path_parts[1] if len(path_parts) > 1 else 'unknown'

                log = HttpAuditLog(
                    user_id=user_id,
                    method=request.method,
                    path=request.url.path,
                    entity_type=entity_type,
                    ip_address=request.client.host if request.client else '',
                    user_agent=request.headers.get('user-agent', '')
                )
                db.add(log)
                db.commit()
        except Exception as e:
            logger.error(f"Audit middleware error: {e}")
        finally:
            db.close()

    return response
```

**在 `main.py` 中注册：**
```python
from middleware.audit import audit_middleware

# 在 CORS 之后、路由之前注册
app.middleware("http")(audit_middleware)
```

> ⚠️ **命名说明**：现有 `models/audit.py` → `audit_logs` 表是**审批记录**（approve/reject），新表命名为 `http_audit_log` 避免冲突。

### 4.3 状态枚举

**文件：`server/utils/status.py`**

```python
"""FastInOut 全局状态枚举 — 所有模块统一使用"""

class SalesOrderStatus:
    DRAFT = "draft"
    PENDING = "pending"
    AUDITED = "audited"
    CONVERTED = "converted"
    LOCKED = "locked"

class SalesDeliveryStatus:
    """销售单状态（v2.3 简化：去掉了 delivered）"""
    PENDING = "pending"       # 已开单,库存已扣,当日可作废
    SETTLING = "settling"     # 已提交交账,禁止编辑/作废
    SETTLED = "settled"       # 交账审核通过,彻底锁定
    VOIDED = "voided"         # 当日作废,库存已回滚
    LOCKED = "locked"         # 跨日自动锁定
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

class SettlementStatus:
    PENDING = "pending"
    AUDITED = "audited"
    REJECTED = "rejected"

class StocktakingStatus:
    DRAFT = "draft"
    PENDING = "pending"
    AUDITING = "auditing"
    AUDITED = "audited"
    ADJUSTED = "adjusted"

class VehicleLoadStatus:
    DRAFT = "draft"
    PENDING = "pending"
    LOADED = "loaded"
    PARTIAL_RETURN = "partial_return"
    RETURNED = "returned"
```

### 4.4 目录重组（改名不改逻辑）

```
操作（按顺序执行）：

1. mkdir server/services
2. 创建 server/services/__init__.py, server/services/inventory_service.py
3. 创建 server/utils/status.py
4. 创建 server/models/http_audit_log.py
5. 复制 routers/sales.py → routers/sales_order.py（不改内容）
6. 复制 routers/purchases.py → routers/purchase_order.py（不改内容）
7. main.py: 注册 audit 中间件
8. main.py: 将 'sales' 导入改为 'sales_order'（路由不变）
9. main.py: 将 'purchases' 导入改为 'purchase_order'（路由不变）

⚠️ 不删旧文件，确保现有 API 正常运行。
```

### 4.4.1 前端同步改动（v1.1 新增）

> 目录重组会改变后端路由前缀，前端 API 路径必须同步修改，否则功能断裂。

| 改动 | PC 端 (`pc/src/`) | H5 端 (`h5/src/`) |
|------|-------------------|-------------------|
| API 路径 | `api/index.js` 中 `/api/sales` → `/api/sales-orders` | `api/index.js` 同步修改 |
| 路由 | `router/index.js` 路由 path 和 component 路径 | `router/index.js` 同步修改 |
| 视图目录 | `views/sales/` → `views/sales_order/` | 对应页面路径修改 |
| Layout 菜单 | `Layout.vue` 子模块 path 更新 | `Layout.vue` Tabbar path 更新 |

**关键原则**：后端改名和前端改名必须在同一个 commit 中完成，不允许中间状态。

### 4.5 models 拆分

```
1. models/sales.py → 保留 SalesOrder/SalesOrderItem（不变）
   → 新增 SalesDelivery/SalesDeliveryItem（新表）
   → SalesStockout 保留但标记 @deprecated

2. models/purchase.py → 保留 PurchaseOrder/PurchaseOrderItem（不变）
   → 新增 PurchaseReceipt/PurchaseReceiptItem（新表）
   → PurchaseStockin 保留但标记 @deprecated
   → 新增 PurchaseReturnDelivery（采购退货出库单）

3. models/http_audit_log.py → 新建（HTTP请求审计，非审批记录）
4. models/role.py → 已有 role_key/is_system/sort_order/status，无需改动
5. models/employee.py → 加 report_to
6. models/product.py → 加 min_price
```

---

## 五、Phase A：P0 核心业务（8-10天）

### Day 1-2：销售单 ⭐ 最核心模块

**这是全系统状态最复杂、影响面最大的模块。做对了后面都顺。**

#### 5.1.1 后端 Model

```python
# models/sales.py 新增

class SalesDelivery(Base):
    __tablename__ = "sales_deliveries"
    
    id = Column(Integer, primary_key=True)
    delivery_no = Column(String(30), unique=True, nullable=False)  # XS-20260504-001
    customer_id = Column(Integer, ForeignKey("customers.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    vehicle_id = Column(Integer, nullable=True)
    
    total_amount = Column(Float, default=0)
    cash_amount = Column(Float, default=0)       # 现金收款
    wechat_amount = Column(Float, default=0)    # 微信
    alipay_amount = Column(Float, default=0)    # 支付宝
    credit_amount = Column(Float, default=0)    # 赊账
    
    status = Column(String(20), default="pending")
    # pending / settling / settled / voided / locked / reversed
    
    source_type = Column(String(20), default="direct")  # direct / from_order
    void_reason = Column(String(200))
    originated_from_id = Column(Integer)  # 复制作废单来源
    payment_evidence = Column(Text)       # 电子签名/支付流水 JSON
    
    created_by = Column(Integer, ForeignKey("employees.id"))
    auditor_id = Column(Integer, ForeignKey("employees.id"))
    audited_at = Column(DateTime)
    settled_at = Column(DateTime)
    settlement_id = Column(Integer)
    
    created_at = Column(DateTime, server_default=func.now())
    remark = Column(Text)
    
    # CHECK 约束在 SQL 层保证（见 Phase 0 migration）
```

#### 5.1.2 后端 Router API

**文件：`routers/sales_delivery.py`**

| 端点 | 方法 | 说明 | 关键逻辑 |
|------|------|------|---------|
| `/api/sales-deliveries` | POST | 开单 | ①生成 delivery_no ②扣库存 ③status='pending' |
| `/api/sales-deliveries` | GET | 列表 | 分页+筛选（状态/客户/日期/业务员） |
| `/api/sales-deliveries/{id}` | GET | 详情 | 含明细行 |
| `/api/sales-deliveries/{id}/void` | POST | **作废（当日）** | ①校验当日 ②填 void_reason ③status→voided ④库存回滚 |
| `/api/sales-deliveries/{id}/reverse` | POST | **红冲** | ①生成负金额冲销单 ②status→reversed ③库存回滚 |
| `/api/sales-deliveries/{id}/copy` | POST | 复制开单 | ①从 voided 单复制 ②新单 originated_from_id=原单 |

**开单流程（伪代码）**：
```python
def create_sales_delivery(data: SalesDeliveryCreate, db: Session, current_user):
    # 1. 生成单号
    delivery_no = generate_no("XS", db)
    
    # 2. 创建销售单
    delivery = SalesDelivery(
        delivery_no=delivery_no,
        customer_id=data.customer_id,
        warehouse_id=data.warehouse_id,
        total_amount=data.total_amount,
        cash_amount=data.cash_amount,
        wechat_amount=data.wechat_amount,
        alipay_amount=data.alipay_amount,
        credit_amount=data.credit_amount,
        status=SalesDeliveryStatus.PENDING,
        created_by=current_user.id
    )
    db.add(delivery)
    
    # 3. 创建明细 + 扣库存
    for item in data.items:
        # 扣库存（仓库或车辆）
        inventory_service.deduct(
            db, item.product_id, 
            data.warehouse_id or data.vehicle_id,
            item.quantity
        )
        db.add(SalesDeliveryItem(delivery_id=delivery.id, ...))
    
    db.commit()
    return delivery
```

#### 5.1.3 库存服务

**文件：`server/services/inventory_service.py`**

```python
class InventoryService:
    """库存扣减/回滚统一入口"""
    
    @staticmethod
    def deduct(db, product_id, warehouse_id, quantity):
        """扣库存，库存不足抛出异常"""
        inv = db.query(Inventory).filter(
            Inventory.product_id == product_id,
            Inventory.warehouse_id == warehouse_id
        ).first()
        if not inv or inv.quantity < quantity:
            raise HTTPException(400, f"库存不足：{product_id} 仓库{warehouse_id}")
        inv.quantity -= quantity
    
    @staticmethod
    def restore(db, product_id, warehouse_id, quantity):
        """回滚库存（作废/红冲时调用）"""
        inv = db.query(Inventory).filter(
            Inventory.product_id == product_id,
            Inventory.warehouse_id == warehouse_id
        ).first()
        if inv:
            inv.quantity += quantity
```

#### 5.1.4 前端

**文件：`pc/src/router/index.js`** — 路由修改：
```javascript
// 旧
{ path: 'sales', name: 'Sales', meta: { title: '销售订单' } }
{ path: 'sales-returns', name: 'SalesReturns', meta: { title: '销售退货' } }

// 新
{ path: 'sales-orders', name: 'SalesOrders', meta: { title: '销售订单' } }  // 改名
{ path: 'sales-deliveries', name: 'SalesDeliveries', meta: { title: '销售单' } }  // 新增
{ path: 'sales-returns', name: 'SalesReturns', meta: { title: '退货订单' } }  // 改标题
{ path: 'sales-return-deliveries', ... meta: { title: '退货单' } }  // Phase A Day7-8
```

**文件：`pc/src/views/sales_order/Index.vue`** — 从 `sales/Index.vue` 重命名目录
**文件：`pc/src/views/sales_delivery/Index.vue`** — 新建销售单管理页

**关键 UI 要素**：
- 开单表单：客户选择 + 商品选择 + 数量/单价 + 收款方式（现金/微信/支付宝/赊账四个输入框）
- 作废按钮：弹出原因输入框（必填），确认后调用 POST void
- 复制开单：从 voided 单复制，显示"复制自 XS-xxx(已作废)"
- 状态标签：用不同颜色标识 pending（蓝）/ settling（橙）/ settled（绿）/ voided（灰）/ locked（红）

#### 5.1.5 命名迁移对照（Phase A 立即执行）

| 旧路径/名称 | 新路径/名称 | 操作 |
|-----------|-----------|------|
| `/api/sales` | `/api/sales-orders` | Router prefix 改名 |
| `views/sales/Index.vue` | `views/sales_order/Index.vue` | 目录+文件重命名 |
| `views/sales/Returns.vue` | `views/sales_return/Index.vue` | 改名 |

### Day 3-4：采购入库单 + 采购退货出库单

**文件：`routers/purchase_receipt.py`**

| 端点 | 说明 |
|------|------|
| POST `/api/purchase-receipts` | 基于采购订单创建入库单 |
| POST `/api/purchase-receipts/{id}/confirm` | 仓管确认收货 -> 库存增加 + 应付生成 |

**文件：`routers/purchase_return_dlv.py`**

| 端点 | 说明 |
|------|------|
| POST `/api/purchase-return-deliveries` | 创建退货出库单 |
| POST `.../{id}/wh-confirm` | 仓管确认出库 -> 库存减少 |
| POST `.../{id}/fin-confirm` | 财务确认 -> 冲减供应商应付 |

### Day 5-6：盘点单 + 费用管理

**盘点单**（基于现有 `inventory_checks` 扩展）：

| 新增逻辑 |
|---------|
| 整仓盘点→该仓库禁止出入库 |
| 差异超过5%→主管复核 |
| 审核通过→自动更新 inventory |

**费用管理**（全新模块）：

| 表 | 说明 |
|----|------|
| `expense_category` | 费用类别 |
| `expense` | 费用记录（含 approver_id/report_to/发票URL/重复检测哈希） |
| `expense_contract` | 费用合同 |

### Day 7-8：财务报表 + 往来账 + 退货单

**退货单**（扩展 `sales_returns` 改名 `sales_return_dlv`）：

| 新增状态 | 触发 |
|---------|------|
| `warehouse_confirmed` | 仓管确认+拍照+第二人质检 |
| `finance_confirmed` | 财务确认冲账金额 |
| `settled` | 交账审核通过自动触发（Phase B 实现） |

### Day 9-10：审计报告 + 联调

基于 Phase 0 自动积累的 `http_audit_log`，实现：
- 按时间/用户/实体类型筛选
- 操作审计视图（PC 端 `views/audit_log/Index.vue`）
- 全模块联调：销售→采购→盘点→费用→报表→审计 端到端测试

---

## 六、Phase B：车销 + 交账（5-6天）

### ⚠️ 前置条件
- Phase A 销售单/退货单已完成
- Phase A 审计日志已运行

### ⚠️ 现有车销模型说明（v1.1 补充）

> 当前已有简化版车销模型（`models/vehicle.py`）：
> - `VehicleSalesOut` — 车销出库（String status="draft"，已有 CRUD）
> - `VehicleReturn` — 车销退货（String status="draft"，已有 CRUD）
> - `VehicleLoss` — 车销报损（String status="draft"，已有 CRUD）
> - `vehicle.py` router — 已有完整 CRUD 端点
>
> **这些是简化模型**，不满足 v2.4 完整车销需求（无 Vehicle 主档、无 VehicleInventory 车上库存、无 VehicleLoad 装车单、无 Settlement 交账）。
>
> **策略**：保留旧模型和 API 不动（H5 端可能已在使用），Phase B 新建完整体系，旧模型标记 @deprecated。

### Day 1-2：车辆 + 装车

**新建 models/vehicle_v2.py**（避免与现有 vehicle.py 冲突）：
```python
class Vehicle(Base):       # 车辆档案（新增）
class VehicleInventory(Base):  # 车上库存（新增）
class VehicleLoad(Base):   # 装车单 (draft→pending→loaded→partial_return→returned)
class VehicleLoadItem(Base):   # 装车明细 (含 returned_quantity)
class VehicleReturn(Base): # 退库记录（新建，与旧 VehicleReturn 不同）
```

**装车逻辑**：装车单审核→仓库库存扣减→车上库存增加

### Day 3-4：车销开单 H5

- H5 端扫条码/快速选品
- 客户电子签名
- 扣车上库存

### Day 5-6：交账系统

**新建 models/vehicle.py 补充**：
```python
class Settlement(Base):
    # 销售汇总 + 退货汇总 + 费用
    # settlement_snapshot JSON
    # return_cash / return_credit / return_electronic

class SettlementDelivery(Base):  # 交账-销售单关联
class SettlementReturn(Base):    # 交账-退货单关联 ⭐v2.4
```

**交账流程**：
1. 业务员提交 → 销售单进入 settling
2. 财务核对公式：**实交现金 = 销售现金 - 退货现金**
3. 审核通过 → 销售单→settled + 退货单→settled（自动触发 finance_confirmed）
4. 驳回 → 销售单恢复 pending

**状态机升级脚本**（Phase B Day 1 就写）：
```python
# 将 Phase A 期间积累的 pending 状态销售单接入新状态机
# 1. 扫描所有 status='pending' 的 sales_deliveries
# 2. 按业务员+日期分组，准备待交账数据
# 3. 验证数据完整性后标记为「Phase A 遗留」
```

---

## 七、Phase C：P1 完善（5-7天）

| Day | 模块 | 实现要点 |
|-----|------|---------|
| 1-2 | 预收/预付款 + 报损单 | advance_payment 表；damage_report 审核后扣库存 |
| 3-4 | 品牌/渠道/线路/客户等级 | 纯 CRUD，档案扩充 |
| 5 | 销售报表 + 采购报表 | 销售明细/5维度汇总；采购明细/汇总 |
| 6-7 | 员工提成 + 公司设置 + 价格管控 | commissions 表；company_config 含 settlement_expense_auto_approve_limit；product.min_price 校验 |

---

## 八、Phase D：风控增强（3-4天）

| Day | 模块 | 实现要点 |
|-----|------|---------|
| 1-2 | 异常交易监控 | 作废复开分析/单价异常/赊账比例/多单退款 |
| 3 | 客户对账确认 | 电子对账单 |
| 4 | 轮岗盘点 + 联调 | 他人复核机制 |

---

## 九、状态机完整定义

### 9.1 销售单（全系统最复杂）

```
                    ┌── 开单 ──→ pending ──→ [跨日] → locked → 红冲 → reversed
                    │               │
                    │               ├── [当日作废] → voided → 复制 → 新pending(标注原单号)
                    │               │
                    │               └── [交账提交] → settling ──→ [审核通过] → settled
                    │                                   │
                    │                                   └── [驳回] → pending(解绑恢复)
                    │
                    └── 订单转单 ──→ 来自 sales_order 的 audited 状态
```

**状态转换矩阵**：

| 当前状态 → 目标状态 | 触发条件 | 操作人 |
|-------------------|---------|:---:|
| (新建) → pending | 开单 | 业务员/主管 |
| pending → voided | 当日作废（须填原因） | 开单人 |
| pending → locked | 跨日（服务器时区00:00） | 系统 |
| pending → settling | 提交交账 | 业务员 |
| settling → settled | 交账审核通过 | 财务 |
| settling → pending | 交账驳回 | 财务 |
| locked → reversed | 红冲 | 主管/admin |
| settled → reversed | 红冲 | admin |

### 9.2 退货单

```
pending → warehouse_confirmed(仓管+拍照+第二人质检) → finance_confirmed(财务确认冲账)
                                                           │
                                          ┌────────────────┘
                                          │
                                     [车销交账审核] → settled（自动触发）
                                     [非车销] → finance_confirmed 即终态
```

### 9.3 采购退货出库单

```
pending → warehouse_confirmed(仓管出库) → finance_confirmed(财务确认冲应付)
```

### 9.4 装车单

```
draft → pending → loaded → partial_return → returned
```

---

## 十、数据库迁移完整脚本

### 10.1 核心新表（按 Phase 执行）

**Phase 0**：见 §4.1（v1.1修订：跳过权限表/模块表，仅新建 http_audit_log + 扩展字段 + 新业务表）

**Phase A Day 1-2**：
```sql
-- sales_delivery_items（已在 Phase 0 建好 sales_deliveries，补充明细表）
CREATE TABLE IF NOT EXISTS sales_delivery_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    batch_id INTEGER,
    quantity FLOAT DEFAULT 0,
    unit_price FLOAT DEFAULT 0,
    amount FLOAT DEFAULT 0,
    source_order_item_id INTEGER
);

-- order_delivery_link
CREATE TABLE IF NOT EXISTS order_delivery_link (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sales_order_id INTEGER NOT NULL,
    sales_delivery_id INTEGER NOT NULL,
    UNIQUE(sales_order_id, sales_delivery_id)
);
```

**Phase A Day 3-4**：
```sql
-- purchase_receipt_items
CREATE TABLE IF NOT EXISTS purchase_receipt_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    order_item_id INTEGER,
    quantity FLOAT DEFAULT 0,
    unit_price FLOAT DEFAULT 0,
    amount FLOAT DEFAULT 0
);

-- purchase_return_deliveries
CREATE TABLE IF NOT EXISTS purchase_return_deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    return_no VARCHAR(30) UNIQUE NOT NULL,
    purchase_order_id INTEGER,
    purchase_receipt_id INTEGER,
    supplier_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    total_amount FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    created_by INTEGER NOT NULL,
    wh_confirmed_by INTEGER,
    wh_confirmed_at DATETIME,
    fin_confirmed_by INTEGER,
    fin_confirmed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Phase A Day 5-6**：
```sql
-- expense_category / expense / expense_contract
CREATE TABLE IF NOT EXISTS expense_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30) NOT NULL,
    type VARCHAR(20) DEFAULT 'expense'
);

CREATE TABLE IF NOT EXISTS expense (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_no VARCHAR(30) UNIQUE NOT NULL,
    category_id INTEGER NOT NULL,
    amount FLOAT DEFAULT 0,
    payee VARCHAR(50),
    payee_is_employee BOOLEAN DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    contract_id INTEGER,
    settlement_id INTEGER,
    invoice_url VARCHAR(500),
    duplicate_check_hash VARCHAR(64),
    created_by INTEGER NOT NULL,
    approver_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Phase B**：
```sql
-- vehicle / vehicle_inventory / vehicle_load / vehicle_load_item / vehicle_return
-- settlement / settlement_delivery / settlement_return
-- 完整 SQL 见 v2.4 §6.6
```

### 10.2 employee.report_to 初始化

```sql
-- 如果已有主管数据，手动设置
-- 否则开发环境中将所有员工的 report_to 设为 admin（id=1）
UPDATE employees SET report_to = 1 WHERE report_to IS NULL AND id != 1;
```

### 10.3 module 表预置数据

```sql
-- 完整 39 条 INSERT，见 v2.4 §9.2
-- Phase 0 migration 执行
```

---

## 十一、前后端改动清单

### 11.1 后端（按实施顺序）

| # | 文件 | 操作 | Phase |
|---|------|------|:---:|
| 1 | `server/middleware/audit.py` | 新建（middleware/__init__.py 已存在） | 0 |
| 2 | `server/utils/status.py` | 新建 | 0 |
| 3 | `server/services/__init__.py` | 新建 | 0 |
| 4 | `server/services/inventory_service.py` | 新建 | 0 |
| 5 | `server/models/http_audit_log.py` | 新建 | 0 |
| 6 | `server/migrations/001_phase0_baseline.sql` | 新建（v1.1修订版） | 0 |
| 7 | `server/main.py` | 修改（注册中间件+路由） | 0 |
| 9 | `server/models/sales.py` | 修改（新增 SalesDelivery） | A1-2 |
| 10 | `server/routers/sales_order.py` | 从 sales.py 复制改名 | A1-2 |
| 11 | `server/routers/sales_delivery.py` | 新建 | A1-2 |
| 12 | `server/schemas/sales_delivery.py` | 新建 | A1-2 |
| 13 | `server/models/purchase.py` | 修改（新增 PurchaseReceipt 等） | A3-4 |
| 14 | `server/routers/purchase_order.py` | 从 purchases.py 复制改名 | A3-4 |
| 15 | `server/routers/purchase_receipt.py` | 新建 | A3-4 |
| 16 | `server/routers/purchase_return_dlv.py` | 新建 | A3-4 |
| 17 | `server/models/expense.py` | 新建 | A5-6 |
| 18 | `server/routers/expense.py` | 新建 | A5-6 |
| 19 | `server/routers/stocktaking.py` | 新建（扩展 inventory_checks） | A5-6 |
| 20 | `server/routers/sales_return.py` | 新建（订单层） | A7-8 |
| 21 | `server/routers/sales_return_dlv.py` | 新建（单据层） | A7-8 |
| 22 | `server/routers/report_finance.py` | 新建 | A7-8 |
| 23 | `server/routers/account_ledger.py` | 新建 | A7-8 |
| 24 | `server/routers/audit_log.py` | 新建 | A9-10 |
| 25 | `server/models/vehicle.py` | 新建 | B1-2 |
| 26 | `server/routers/vehicle_load.py` | 新建 | B1-2 |
| 27 | `server/routers/settlement.py` | 新建 | B5-6 |
| 28 | `server/services/settlement_service.py` | 新建 | B5-6 |

### 11.2 前端（按实施顺序）

| # | 文件 | 操作 | Phase |
|---|------|------|:---:|
| 1 | `pc/src/router/index.js` | 修改路由名 | 0/A1-2 |
| 2 | `pc/src/views/sales_order/Index.vue` | 从 sales/Index.vue 改名 | A1-2 |
| 3 | `pc/src/views/sales_delivery/Index.vue` | 新建 | A1-2 |
| 4 | `pc/src/views/purchase_order/Index.vue` | 从 purchases/Index.vue 改名 | A3-4 |
| 5 | `pc/src/views/purchase_receipt/Index.vue` | 新建 | A3-4 |
| 6 | `pc/src/views/expense/Index.vue` | 新建 | A5-6 |
| 7 | `pc/src/views/stocktaking/Index.vue` | 新建 | A5-6 |
| 8 | `pc/src/views/sales_return/Index.vue` | 新建（退货订单） | A7-8 |
| 9 | `pc/src/views/sales_return_dlv/Index.vue` | 新建（退货单） | A7-8 |
| 10 | `pc/src/views/report_finance/Index.vue` | 新建 | A7-8 |
| 11 | `pc/src/views/account_ledger/Index.vue` | 新建 | A7-8 |
| 12 | `pc/src/views/audit_log/Index.vue` | 新建 | A9-10 |
| 13 | `pc/src/views/vehicle_load/Index.vue` | 新建 | B1-2 |
| 14 | `pc/src/views/settlement/Index.vue` | 新建 | B5-6 |
| 15 | H5 端 | 新建（车销开单） | B3-4 |

> ⚠️ **前端同步原则**（v1.1 新增）：后端路由改名时，PC 端和 H5 端的 API 路径、路由配置、Layout 菜单必须在同一个 commit 中同步修改。

---

## 十二、测试策略

### 12.1 每 Phase 测试清单

| Phase | 关键测试点 |
|-------|-----------|
| 0 | http_audit_log 是否自动记录所有 POST/PUT/DELETE；旧 API 是否正常运行 |
| A1-2 | 开单→扣库存✓；当日作废→库存回滚✓；跨日作废被拒绝✓；红冲→负金额冲销单✓ |
| A3-4 | 采购入库→库存增加✓；采购退货出库→仓管确认→财务确认✓ |
| A5-6 | 整仓盘点锁定✓；费用报销→上级审批✓ |
| A7-8 | 退货拍照→仓管确认→财务确认✓；财务报表数据正确✓ |
| A9-10 | 审计日志可查✓；全链路端到端✓ |
| B1-2 | 装车→仓库库存减少+车上库存增加✓ |
| B3-4 | 车销开单→扣车上库存✓ |
| B5-6 | 交账审核→销售单settled+退货单settled✓；费用拆单检测✓ |
| C | 各 P1 模块功能✓；价格管控✓ |
| D | 异常监控告警✓；对账单生成✓ |

### 12.2 回归测试

每次 Phase 完成后，运行全回归：
1. Phase 0 之后：确保所有旧 API 正常
2. Phase A 之后：销售→采购→盘点→费用→退货→报表 全链路
3. Phase B 之后：车销全流程（装车→开单→交账→退库）
4. Phase D 之后：最终全量回归

---

## 十三、风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|:---:|------|------|
| SalesStockout→SalesDelivery 旧数据丢失 | 高 | 高 | 保留旧表，写数据迁移脚本，双表并行运行过渡期 |
| 状态迁移脚本有 bug | 中 | 高 | Phase B Day 1 就写并测试，不等到 Day 5 |
| 审计中间件性能问题 | 低 | 中 | 异步写入，不阻塞请求响应 |
| 目录重组后前端404 | 中 | 中 | PC+H5 的 api/index.js 必须同步改路径，改完立即测试 |
| Phase A 销售单状态机理解偏差 | 中 | 高 | Day 1-2 优先完成状态机单测 |
| auth 中间件迁移失败 | 中 | 中 | 表+服务层已就位，Phase A 逐步迁移，旧JSON作为 fallback |

---

## 附录：关键决策记录

| 决策 | 理由 | 版本 |
|------|------|:---:|
| 去掉 delivered 态 | 车销开单=确认=扣库存，无需额外步骤 | v2.3 |
| 交账系统整体移到 Phase B | 重度依赖车销的装车/车辆库存 | v2.2 |
| 审计中间件前置到 Phase 0 | 横切关注点，后期补成本太高 | v2.4 |
| 退货 settled 仅在交账审核时触发 | 非车销 finance_confirmed 即终态 | v2.4 |
| 费用阈值可配置 | 防止拆单绕过，财务可下调至 50 元 | v2.3 |
| http_audit_log 命名 | 避免与现有 audit_logs（审批记录）命名冲突 | v1.1 |
| 车销旧模型保留 | VehicleSalesOut/Return/Loss 已有CRUD，H5可能在用，Phase B 新建完整体系 | v1.1 |
| Phase 0 缩减至0.5天 | 权限表/模块表/角色扩展已在前期完成，无需重复建设 | v1.1 |
| 旧车销模型保留 | H5端可能已在使用，新体系并行建 | v1.1 |
| Phase 0 缩减至0.5天 | 权限表/模块表/角色扩展已建好 | v1.1 |

---

*本文档与 `FastInOut_PC_H5统一权限_实施细化方案_v2.4.md` 配套使用。方案定义「做什么」，本文档定义「怎么做」。*
