-- ═══════════════════════════════════════════
-- Phase 0 Migration v1.1：仅新建表+扩展字段
-- 权限表/模块表/角色扩展 已在 auto_migrate 中处理，此处跳过
-- 实际建表由 SQLAlchemy models + Base.metadata.create_all 完成
-- 此文件仅作为参考文档
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

-- 2. sales_deliveries 表（替代 sales_stockouts）
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
    remark TEXT
);

-- 3. sales_delivery_items 表
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

-- 4. purchase_receipts 表（替代 purchase_stockins）
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

-- 5. purchase_receipt_items 表
CREATE TABLE IF NOT EXISTS purchase_receipt_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    order_item_id INTEGER,
    quantity FLOAT DEFAULT 0,
    unit_price FLOAT DEFAULT 0,
    amount FLOAT DEFAULT 0
);

-- 6. employee 扩展
ALTER TABLE employees ADD COLUMN report_to INTEGER REFERENCES employees(id);

-- 7. product 扩展
ALTER TABLE products ADD COLUMN min_price FLOAT DEFAULT 0;

-- 8. employee.report_to 初始化
UPDATE employees SET report_to = 1 WHERE report_to IS NULL AND id != 1;
