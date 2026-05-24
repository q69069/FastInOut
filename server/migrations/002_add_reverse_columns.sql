-- 002_add_reverse_columns.sql
-- 为所有单据表添加冲红相关字段

-- 销售订单
ALTER TABLE sales_orders ADD COLUMN reverse_reason VARCHAR(200);
ALTER TABLE sales_orders ADD COLUMN reversed_by INTEGER REFERENCES employees(id);
ALTER TABLE sales_orders ADD COLUMN reversed_at DATETIME;

-- 销售出库单
ALTER TABLE sales_stockouts ADD COLUMN reverse_reason VARCHAR(200);
ALTER TABLE sales_stockouts ADD COLUMN reversed_by INTEGER REFERENCES employees(id);
ALTER TABLE sales_stockouts ADD COLUMN reversed_at DATETIME;

-- 销售退货单
ALTER TABLE sales_returns ADD COLUMN reverse_reason VARCHAR(200);
ALTER TABLE sales_returns ADD COLUMN reversed_by INTEGER REFERENCES employees(id);
ALTER TABLE sales_returns ADD COLUMN reversed_at DATETIME;

-- 采购订单
ALTER TABLE purchase_orders ADD COLUMN reverse_reason VARCHAR(200);
ALTER TABLE purchase_orders ADD COLUMN reversed_by INTEGER REFERENCES employees(id);
ALTER TABLE purchase_orders ADD COLUMN reversed_at DATETIME;

-- 采购入库单
ALTER TABLE purchase_stockins ADD COLUMN reverse_reason VARCHAR(200);
ALTER TABLE purchase_stockins ADD COLUMN reversed_by INTEGER REFERENCES employees(id);
ALTER TABLE purchase_stockins ADD COLUMN reversed_at DATETIME;

-- 采购退货单
ALTER TABLE purchase_returns ADD COLUMN reverse_reason VARCHAR(200);
ALTER TABLE purchase_returns ADD COLUMN reversed_by INTEGER REFERENCES employees(id);
ALTER TABLE purchase_returns ADD COLUMN reversed_at DATETIME;

-- 采购入库单（Phase A）
ALTER TABLE purchase_receipts ADD COLUMN reverse_reason VARCHAR(200);
ALTER TABLE purchase_receipts ADD COLUMN reversed_by INTEGER REFERENCES employees(id);
ALTER TABLE purchase_receipts ADD COLUMN reversed_at DATETIME;

-- 采购退货出库单
ALTER TABLE purchase_return_deliveries ADD COLUMN reverse_reason VARCHAR(200);
ALTER TABLE purchase_return_deliveries ADD COLUMN reversed_by INTEGER REFERENCES employees(id);
ALTER TABLE purchase_return_deliveries ADD COLUMN reversed_at DATETIME;

-- 销售单（Phase A）
ALTER TABLE sales_deliveries ADD COLUMN reverse_reason VARCHAR(200);
ALTER TABLE sales_deliveries ADD COLUMN reversed_by INTEGER REFERENCES employees(id);
ALTER TABLE sales_deliveries ADD COLUMN reversed_at DATETIME;
