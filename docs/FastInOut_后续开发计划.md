# FastInOut 后续开发计划

> 📅 编制日期：2026-05-04
> 📖 依据：v2.4开发基线版 + 当前代码实现对比
> 📊 当前完成度：30/39模块（77%），后端51个router，PC前端44条路由，H5端24个页面

---

## 一、整体进度概览

| Phase | 内容 | 模块数 | 预估天数 | 状态 |
|-------|------|:---:|:---:|:---:|
| Phase 0 | 基础设施（审计中间件+状态枚举+新表） | 5项 | 1天 | ✅ 已完成 |
| Phase A | P0核心业务（销售单/入库单/费用/盘点/退货/审计/往来账） | 26项 | 8-10天 | ✅ 已完成 |
| **Phase A+** | **Phase A 补全** | 5项 | **1-2天** | 🔴 待做 |
| **Phase B** | **车销H5端 + 交账完善** | 6项 | **3-4天** | 🔴 待做 |
| **Phase C** | **P1档案 + 报表** | 8项 | **4-5天** | 🔴 待做 |
| **Phase D** | **风控增强 + 联调** | 4项 | **2-3天** | 🔴 待做 |
| **合计** | | | **10-14天** | |

---

## 二、已完成功能清单

### Phase 0（已完成）
- [x] 审计中间件（server/middleware/audit.py）
- [x] HTTP审计日志表（http_audit_log）
- [x] 状态枚举定义
- [x] 新增数据模型（vehicle_load, settlement, advance_payment, damage_report, commission, company_config, reconciliation）
- [x] 数据库自动迁移

### Phase A（已完成）
- [x] 销售单（sales_delivery）— 开单/列表/详情/作废/红冲
- [x] 采购入库单（purchase_receipt）— 创建/列表/详情/确认入库
- [x] 费用管理（expense）— 类别管理/创建费用/审批/驳回
- [x] 盘点管理（stocktaking）— 列表/详情/审核/调整库存/作废
- [x] 退货单（sales_return_dlv）— 列表/详情/仓管确认/财务确认
- [x] 审计日志（audit_log）— HTTP请求记录查看
- [x] 往来账（account_ledger）— 客户应收/供应商应付汇总+明细
- [x] PC前端 — 7个新页面 + API + 路由 + 侧边栏菜单

### 已有模块（Phase A之前）
- [x] 首页仪表盘
- [x] 客户管理 / 供应商管理 / 商品管理 / 单位管理
- [x] 仓库管理 / 批次管理 / 员工管理 / 线路管理
- [x] 销售订单 / 退货订单 / 采购订单 / 采购退货
- [x] 库存管理 / 财务管理 / 促销管理
- [x] 角色权限 / 公司设置 / 数据备份
- [x] 装车管理 / 交账管理 / 预收付款 / 报损单
- [x] 异常监控 / 客户对账

---

## 三、Phase A+ 补全（1-2天）

> 目标：补齐 Phase A 遗漏项，确保 P0 功能完整可用

### Day 1：采购退货出库单独立模块

**任务清单：**
- [ ] 后端：从 `routers/purchases.py` 拆出 `routers/purchase_return_dlv.py`
- [ ] 创建 `models/purchase_return_dlv.py` 独立模型（如尚未独立）
- [ ] 实现状态机：`pending → warehouse_confirmed → finance_confirmed`
- [ ] 新增财务确认接口 `POST /purchase-return-deliveries/{id}/finance-confirm`
- [ ] 仓管确认出库时扣减库存
- [ ] 财务确认时冲减供应商应付
- [ ] 注册到 `main.py`
- [ ] PC前端：创建 `views/purchase_return_dlv/Index.vue`
- [ ] PC路由：添加 `/purchase-return-deliveries` 路由
- [ ] PC API：添加采购退货出库单相关 API 函数

**验收标准：**
- 采购退货出库单可独立创建、查看、仓管确认、财务确认
- 仓管确认后库存扣减，财务确认后供应商应付冲减

### Day 2：遗留问题修复

**任务清单：**
- [ ] `customer_contacts` 模块注册到 `main.py`（routers+models 已存在，仅缺注册）
- [ ] 验证三层权限模型是否在 API 层生效
  - 检查各 router 是否调用了权限校验中间件
  - 检查 `role_module_permission` 和 `operation_permission` 表是否被使用
- [ ] 验证跨日自动锁定机制
  - 确认是否有定时任务或请求中间件检查单据创建日期
  - 确认 `locked` 状态是否在实际业务中生效
- [ ] 验证订单→单据转换流程
  - 销售订单审核后能否正确生成销售单
  - 采购订单审核后能否正确生成采购入库单
- [ ] 验证退货单完整状态机
  - `pending → warehouse_confirmed → finance_confirmed → settled`
  - settled 仅在交账审核通过时自动触发

---

## 四、Phase B：车销H5端 + 交账完善（3-4天）

> 目标：业务员可在手机端完成车销全流程（装车→开单→交账）

### Day 1-2：H5 车销开单

**任务清单：**
- [ ] H5 新页面：`views/DirectOrder.vue`（车销直接开销售单）
  - 选择客户（从路线快速筛选）
  - 添加商品（扫条码 / 搜索 / 常用快捷面板）
  - 填写数量和单价（自动带出历史售价）
  - 选择收款方式：现金/微信/支付宝/赊账/混合
  - 开单即扣车上库存（vehicle_inventory）
- [ ] H5 API：对接 `POST /sales-deliveries`（source_type=direct）
- [ ] 车上库存校验：库存不足时禁止开单，提示补货
- [ ] H5 路由：`/direct-order`，moduleKey=sales

**验收标准：**
- 业务员可在H5端直接开销售单（非订单转单）
- 开单后车上库存实时扣减
- 库存不足时有明确提示

### Day 3：H5 交账 + 退货

**任务清单：**
- [ ] H5 新页面：`views/Settlement.vue`（交账管理）
  - 汇总当日所有销售单 + 退货单
  - 填写收款明细（现金/微信/支付宝/赊账）
  - 关联退货退款
  - 夹带费用报销（≤200元自动入账，>200元生成草稿）
  - 提交交账单
- [ ] H5 新页面：`views/ReturnDelivery.vue`（退货单操作）
  - 创建退货单（关联原销售单）
  - 仓管确认收货 + 拍照上传
- [ ] H5 API：对接 settlement 和 sales_return_dlv 相关接口
- [ ] H5 路由：`/settlement`、`/return-delivery`

**验收标准：**
- 业务员可在H5端创建交账单并提交
- 退货单可在H5端创建和确认

### Day 4：H5 补充 + 联调

**任务清单：**
- [ ] H5 新页面：`views/VehicleLoad.vue`（装车/退库）
  - 查看装车单列表
  - 退库操作（支持部分退库）
- [ ] H5 新页面：`views/ExpenseClaim.vue`（费用报销）
  - 上传发票照片
  - 填写金额和类别
- [ ] 客户电子签名组件（H5端手写签名或确认按钮）
- [ ] H5 Tab 栏更新：新增「交账」入口
- [ ] 全流程联调：装车→开单→退货→交账→财务审核

---

## 五、Phase C：P1 档案 + 报表（4-5天）

> 目标：补齐 v2.4 方案中的档案扩充和四大报表

### Day 1：P1 档案模块

**任务清单：**
- [ ] 品牌管理（brands）
  - 后端：在 products 相关 router 中增加品牌 CRUD（或独立 router）
  - PC前端：`views/brands/Index.vue`（品牌列表+新增/编辑/删除）
  - 商品管理增加品牌下拉选择
- [ ] 渠道管理（channels）
  - 后端：`routers/channels.py` + `models/channel.py`
  - PC前端：`views/channels/Index.vue`
  - 客户档案增加渠道字段
- [ ] 客户等级（customer_levels）
  - 后端：`routers/customer_levels.py` + `models/customer_level.py`
  - PC前端：`views/customer_levels/Index.vue`
  - 客户档案增加等级字段
- [ ] 注册到 main.py + router + Layout 侧边栏菜单

### Day 2：员工提成

**任务清单：**
- [ ] 后端：完善 `routers/commission.py` 的提成规则配置接口
  - 按销售额提成
  - 按回款提成
  - 按商品分类提成
  - 阶梯提成规则
- [ ] PC前端：`views/commission/Index.vue`
  - 提成规则配置页面
  - 提成计算结果查看
  - 提成明细导出
- [ ] 路由：`/commissions`，moduleKey=commissions

### Day 3-4：四大报表

**任务清单：**
- [ ] 销售报表（report_sales）
  - PC前端：`views/reports/SalesReport.vue`
  - 销售明细表（按日期/客户/商品/业务员/区域 5维度筛选）
  - 销售汇总表（按维度聚合）
  - 支持导出 Excel
- [ ] 采购报表（report_purchase）
  - PC前端：`views/reports/PurchaseReport.vue`
  - 采购明细表 + 汇总表
- [ ] 库存报表（report_inventory）
  - PC前端：`views/reports/InventoryReport.vue`
  - 库存汇总表（按仓库/商品）
  - 库龄分析（30天/60天/90天以上）
  - 库存预警（低于安全库存）
- [ ] 财务报表（report_finance）
  - PC前端：`views/reports/FinanceReport.vue`
  - 利润表（收入-成本-费用=利润）
  - 应收/应付账龄分析
  - 科目余额表

### Day 5：联调 + H5适配

**任务清单：**
- [ ] H5端品牌/渠道/等级选择器适配（在商品/客户页面中集成）
- [ ] 报表数据准确性验证（与手工台账对比）
- [ ] PC侧边栏菜单更新：新增「品牌管理」「渠道管理」「客户等级」「员工提成」入口
- [ ] 报表菜单分组：销售报表/采购报表/库存报表/财务报表

---

## 六、Phase D：风控增强 + 联调（2-3天）

> 目标：完成 v2.4 防作弊体系，确保系统安全可靠

### Day 1：异常交易监控完善

**任务清单：**
- [ ] 完善 `routers/monitor.py` 异常检测规则
  - 作废后短时间内同客户/商品的新单（漏洞2堵漏）
  - 单价低于商品最低售价的销售单（价格管控）
  - 赊账比例异常（单日赊账占比>80%）
  - 同日多单退款（虚假退货检测）
  - 费用拆单检测（同次交账同类别≥2笔）
- [ ] PC前端：`views/monitor/Index.vue` 完善异常列表+处理
- [ ] 异常告警通知（站内消息推送）

### Day 2：客户对账 + 轮岗盘点

**任务清单：**
- [ ] 客户对账确认（电子对账单）
  - 生成月度对账单（PDF/图片）
  - 客户确认应收余额
  - 对账差异标记
- [ ] 轮岗盘点支持
  - 盘点单增加 `checker_id`（盘点人）字段（已迁移）
  - 支持指定非库管人员参与盘点
  - 盘点结果复核机制

### Day 3：全流程联调

**任务清单：**
- [ ] 完整业务流程穿透测试
  - 坐销流程：销售订单→审核→转销售单→出库→收款→交账
  - 车销流程：装车→开单→退货→交账→财务审核
  - 采购流程：采购订单→审核→采购入库单→仓管确认→付款
  - 采购退货：采购退货→仓管出库→财务确认冲应付
- [ ] 权限穿透测试
  - 5种角色分别登录，验证模块权限/操作权限/数据权限
  - 验证跨日锁定在各模块的生效
- [ ] 审计日志完整性验证
  - 所有CUD操作是否被记录
  - 状态变更是否记录 old_value/new_value
- [ ] 性能测试（大数据量下列表/报表响应速度）

---

## 七、各 Phase 交付物清单

| Phase | 交付物 |
|-------|--------|
| Phase A+ | 采购退货出库单模块 + customer_contacts注册 + 权限/锁定验证报告 |
| Phase B | H5车销开单 + H5交账 + H5退货 + H5费用报销 + 客户签名组件 |
| Phase C | 品牌/渠道/客户等级/员工提成 4个档案模块 + 4大报表页面 |
| Phase D | 异常监控规则 + 客户对账 + 轮岗盘点 + 全流程联调报告 |

---

## 八、风险与依赖

| 风险 | 影响 | 应对 |
|------|------|------|
| 权限中间件未实现 | Phase B/C 的角色权限无法生效 | Phase A+ Day 2 优先验证，如缺失需1天补齐 |
| 跨日锁定未实现 | 财务约束无法执行 | Phase A+ Day 2 优先验证 |
| H5端扫码功能 | 车销开单体验差 | Phase B Day 1 评估是否需要引入扫码SDK |
| 报表数据量大 | 查询慢 | Phase C 引入分页+缓存+索引优化 |
| 交账快照JSON | 对账追溯依赖快照 | Phase B 交账审核时必须写入 settlement_snapshot |

---

## 九、优先级排序（如时间紧迫）

```
必须做（影响核心业务）：
  1. Phase A+ Day 1：采购退货出库单（财务闭环必须）
  2. Phase A+ Day 2：权限验证 + 跨日锁定验证
  3. Phase B Day 1-2：H5车销开单（业务员日常使用）

应该做（影响效率）：
  4. Phase B Day 3：H5交账（车销闭环）
  5. Phase C Day 1：品牌/渠道/客户等级（档案完整性）
  6. Phase C Day 3-4：四大报表（管理层需求）

可以后做（锦上添花）：
  7. Phase B Day 4：客户签名 + 费用报销
  8. Phase C Day 2：员工提成
  9. Phase D：风控增强 + 轮岗盘点
```
