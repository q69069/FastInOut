# FastInOut 调整和优化方案

**制定日期**: 2026-05-24
**基于**: 安全审计报告 + 全量路由扫描

---

## 一、剩余安全加固（P2 优先级）

### 1.1 完全无认证的路由（11个文件）

| 优先级 | 文件 | 风险 | 建议依赖 |
|--------|------|------|----------|
| **高** | `data_import.py` | 可导入任意数据 | `require_admin_dep` |
| **高** | `company.py` | 可修改公司信息 | GET: `get_current_user`, PUT: `require_admin_dep` |
| **高** | `supplier_recon.py` | 供应商对账 | `require_finance_module` |
| **高** | `bank.py` | 银行流水 | `require_finance_module` |
| 中 | `crm.py` | 客户联系人/拜访 | `require_customers_module` |
| 中 | `customer_prices.py` | 客户价格 | `require_customers_module` |
| 中 | `salesmen.py` | 业务员管理 | `require_sales_module` |
| 中 | `promotions.py` | 促销管理 | `require_sales_module` |
| 中 | `batches.py` | 批次管理 | `require_inventory_module` |
| 低 | `print_templates.py` | 打印模板 | `get_current_user` |
| 低 | `export_excel.py` | 导出 | `get_current_user` |

### 1.2 部分端点缺失认证（5个文件）

| 文件 | 缺失端点 | 修复 |
|------|----------|------|
| `categories.py` | GET 列表 + 2个 PUT 更新 | GET 可保持公开，PUT 加 `get_current_user` |
| `units.py` | 5个读取/工具端点 | GET 可保持公开，POST /convert 加 `get_current_user` |
| `invoices.py` | GET 列表 | 加 `require_finance_module` |
| `system.py` | POST /upload/image, POST /backup/restore | 加 `require_admin_dep` |
| `products.py` | GET /{id}/available-units | 加 `require_products_module`（或保持公开，只读） |

### 1.3 旧版认证统一（6个文件）

将 `from routers.auth import get_current_user` 改为 `from deps import get_current_user`：

- `advance_deduction.py`
- `audit.py`
- `message.py`
- `price_change.py`
- `route.py`
- `todos.py`

同时删除 `routers/auth.py` 中重复的 `get_current_user` 定义（保留 `auth.py` 自用的版本，其他文件统一指向 `deps.py`）。

---

## 二、API 返回格式统一（6个文件）

当前这些文件返回裸 list/dict 而非 `{code, message, data}`：

| 文件 | 当前格式 | 目标格式 |
|------|----------|----------|
| `advance_deduction.py` | `list[AdvanceDeductionResponse]` | `ResponseModel(data=...)` |
| `audit.py` | `list[AuditLogResponse]` | `PaginatedResponse(data=...)` |
| `message.py` | `list[MessageResponse]` + `{"success": True}` | `ResponseModel(data=...)` |
| `price_change.py` | `list[PriceChangeLogResponse]` | `ResponseModel(data=...)` |
| `route.py` | `list[RouteResponse]` + `{"success": True}` | `ResponseModel(data=...)` |
| `todos.py` | `List[TodoItem]` | `ResponseModel(data=...)` |

**注意**：返回格式变更会影响前端，需要同步更新前端调用代码。建议先改后端，再逐个适配前端。

---

## 三、其他优化项

### 3.1 数据修复（H-11）

客户/供应商余额不一致，需要执行修复脚本。

**当前问题**：
- 客户1（测试客户）：系统余额 5.00，预期不一致
- 供应商2（API测试供应商）：系统余额 46.00，预期不一致
- 供应商3（蒙牛公司）：系统余额 53000.00，预期不一致

**修复方式**：根据实际业务单据重新计算余额，或编写 SQL 脚本批量修正。

### 3.2 审计日志增强（M-02/M-03）

- 敏感接口（员工、财务、报表）记录 GET 请求
- POST/PUT 请求记录请求体（脱敏处理，不记录密码等敏感字段）

**涉及文件**：
- `server/middleware/audit.py` — 修改 `SKIP_METHODS` 逻辑
- 敏感接口白名单配置

### 3.3 Token 黑名单持久化（S-06）

当前黑名单仅存内存（`routers/auth.py` 中的 `set()`），重启后失效。

**建议方案**：
- 创建 `token_blacklist` 表（已有 `models/token_blacklist.py`）
- `routers/auth.py` 中登出时写入数据库
- `deps.py` 中验证时查询数据库

---

## 四、建议执行顺序

| 阶段 | 内容 | 涉及文件数 | 风险 | 依赖 |
|------|------|-----------|------|------|
| **Phase 1** | 11个无认证路由添加 auth | 11 | 低 | 无 |
| **Phase 2** | 5个部分缺失端点补全 | 5 | 低 | 无 |
| **Phase 3** | 6个旧版认证统一到 deps.py | 6 | 低 | 无 |
| **Phase 4** | 6个返回格式统一 | 6+前端 | 中 | 需前端配合 |
| **Phase 5** | 余额数据修复 | SQL脚本 | 中 | 需确认业务数据 |
| **Phase 6** | 审计日志增强 + Token持久化 | 2-3 | 低 | 无 |

**Phase 1-3** 是纯后端改动，不影响前端，可以立即执行。
**Phase 4** 需要前端同步改动，建议分模块逐个推进。

---

## 五、涉及文件完整清单

### 后端路由文件（server/routers/）

```
Phase 1: 无认证路由
├── batches.py          → require_inventory_module
├── bank.py             → require_finance_module
├── company.py          → get_current_user + require_admin_dep
├── crm.py              → require_customers_module
├── customer_prices.py  → require_customers_module
├── data_import.py      → require_admin_dep
├── export_excel.py     → get_current_user
├── print_templates.py  → get_current_user
├── promotions.py       → require_sales_module
├── salesmen.py         → require_sales_module
└── supplier_recon.py   → require_finance_module

Phase 2: 部分缺失
├── categories.py       → PUT 端点加 get_current_user
├── units.py            → POST /convert 加 get_current_user
├── invoices.py         → GET 加 require_finance_module
├── system.py           → POST 端点加 require_admin_dep
└── products.py         → GET /{id}/available-units 加 require_products_module

Phase 3: 旧版认证统一
├── advance_deduction.py → import 改为 deps
├── audit.py             → import 改为 deps
├── message.py           → import 改为 deps
├── price_change.py      → import 改为 deps
├── route.py             → import 改为 deps
└── todos.py             → import 改为 deps

Phase 4: 返回格式统一
├── advance_deduction.py → ResponseModel
├── audit.py             → PaginatedResponse
├── message.py           → ResponseModel
├── price_change.py      → ResponseModel
├── route.py             → ResponseModel
└── todos.py             → ResponseModel
```

### 核心认证文件

```
server/deps.py              — 统一认证依赖（不动）
server/auth/permissions.py  — 权限检查（不动）
server/routers/auth.py      — 登录/登出 + get_current_user 副本（Phase 3 清理）
server/middleware/audit.py   — 审计中间件（Phase 6 修改）
```

---

**方案版本**: v1.0
**制定人**: Claude Code
