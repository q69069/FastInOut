# FastInOut 手机H5业务员端 开发计划

> 📅 日期：2026-05-02
> 👤 开发：小A (Hermes小A)
> 🎯 目标：8大窗口 + 登录 + 工作台，Vue3 + Vant UI

---

## 项目信息

- **路径：** `E:\FastInOut\mobile\`
- **技术栈：** Vue3 + Vite + Vant UI + Pinia + axios
- **端口：** 5175
- **后端API：** http://127.0.0.1:8000/api

---

## 已完成页面（10个）

| 页面 | 路由 | 功能 |
|------|------|------|
| 🔐 Login | `/login` | 手机号+密码登录，JWT认证 |
| 🏠 Home | `/` | 工作台，8大窗口入口，欢迎卡片 |
| 📋 PendingOrders | `/pending-orders` | 待办订单，超时/待处理Tab，一键导航 |
| 🗺️ VisitPlan | `/visit-plan` | 拜访计划，按路线排列，距离排序 |
| 📸 StoreCheckin | `/store-checkin` | 门店打卡，GPS+拍照+拜访目的 |
| 🛒 QuickOrder | `/quick-order` | 快速下单，搜索客户→搜索商品→购物车→提交 |
| 🖨️ PrintReceipt | `/print-receipt` | 蓝牙打印，58/80mm纸张，ESC/POS |
| 📊 Performance | `/performance` | 业绩查看，今日/本周/本月，提成预估 |
| 📦 StockCheck | `/stock-check` | 查库存，多仓分布，等级价显示 |
| 💰 Receivables | `/receivables` | 应收查询，账龄颜色，催款按钮 |

---

## 核心特性

- ✅ 路由守卫（未登录→跳登录）
- ✅ JWT自动携带+401自动退出
- ✅ API代理配置（开发环境）
- ✅ 路线权限过滤（auth store 保存 route_ids）
- ✅ 响应式设计（Vant UI 移动端组件）
- ✅ 构建验证通过（1.46s，12个 chunk）

---

## 待完善项

| 项目 | 说明 | 优先级 |
|------|------|:---:|
| 后端API对接 | 部分页面使用mock数据，需要对接真实API | P0 |
| 路线权限过滤 | 后端API需支持 route_ids 参数过滤 | P0 |
| 蓝牙打印完整实现 | ESC/POS指令生成+蓝牙发送 | P1 |
| GPS打卡后端API | /visits/checkin 端点 | P1 |
| 图片上传 | 打卡照片上传到服务器 | P1 |
| 离线支持 | Service Worker + 本地缓存 | P2 |
| 推送通知 | Web Push / 微信消息 | P2 |

---

## 启动方式

```bash
cd E:\FastInOut\mobile
npm run dev    # 开发模式，端口5175
npm run build  # 生产构建
```
