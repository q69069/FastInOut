import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
# Phase 0: 导入新模型，确保 Base.metadata.create_all 建表
import models.http_audit_log
import models.sales_delivery
import models.purchase_receipt
import models.expense
import models.vehicle_load
import models.settlement
import models.advance_payment
import models.damage_report
import models.commission
import models.company_config
import models.reconciliation
import models.purchase_return_dlv
from routers import (
    auth, company, warehouses, employees,
    categories, products, customers, suppliers,
    inventory, purchases, sales, finance,
    reports, system, units, promotions, roles,
    backup, customer_prices, crm, salesmen, batches, bank,
    print_templates, data_import, invoices, supplier_recon,
    route, audit, price_change, vehicle, operation_log,
    message, advance_deduction, todos, customer_visits,
    sales_delivery, purchase_receipt, expense, stocktaking,
    sales_return_dlv, audit_log, account_ledger,
    vehicle_load, settlement, advance_payment, damage_report,
    commission, report_enhanced, monitor, reconciliation, company_config,
    purchase_return_dlv
)

# 创建所有表
Base.metadata.create_all(bind=engine)

# 自动迁移：添加缺失的列
from sqlalchemy import text, inspect
def auto_migrate():
    inspector = inspect(engine)
    with engine.connect() as conn:
        # products.level_prices
        cols = inspector.get_columns('products')
        col_names = [c['name'] for c in cols]
        if 'level_prices' not in col_names:
            conn.execute(text('ALTER TABLE products ADD COLUMN level_prices VARCHAR(500)'))
        if 'purchase_price' not in col_names:
            conn.execute(text('ALTER TABLE products ADD COLUMN purchase_price REAL DEFAULT 0'))
        if 'cost_price' not in col_names:
            conn.execute(text('ALTER TABLE products ADD COLUMN cost_price REAL DEFAULT 0'))
        if 'min_price' not in col_names:
            conn.execute(text('ALTER TABLE products ADD COLUMN min_price REAL DEFAULT 0'))

        # employees 新字段
        emp_cols = [c['name'] for c in inspector.get_columns('employees')]
        if 'role_type' not in emp_cols:
            conn.execute(text('ALTER TABLE employees ADD COLUMN role_type VARCHAR(20)'))
        if 'warehouse_ids' not in emp_cols:
            conn.execute(text('ALTER TABLE employees ADD COLUMN warehouse_ids VARCHAR(200)'))
        if 'route_ids' not in emp_cols:
            conn.execute(text('ALTER TABLE employees ADD COLUMN route_ids VARCHAR(200)'))
        if 'bypass_audit' not in emp_cols:
            conn.execute(text('ALTER TABLE employees ADD COLUMN bypass_audit INTEGER DEFAULT 0'))
        if 'online_status' not in emp_cols:
            conn.execute(text('ALTER TABLE employees ADD COLUMN online_status VARCHAR(10) DEFAULT "offline"'))
        if 'report_to' not in emp_cols:
            conn.execute(text('ALTER TABLE employees ADD COLUMN report_to INTEGER'))

        # warehouses 新字段（Phase B+C）
        wh_cols = [c['name'] for c in inspector.get_columns('warehouses')]
        if 'plate_number' not in wh_cols:
            conn.execute(text('ALTER TABLE warehouses ADD COLUMN plate_number VARCHAR(20)'))
        if 'driver_name' not in wh_cols:
            conn.execute(text('ALTER TABLE warehouses ADD COLUMN driver_name VARCHAR(50)'))
        if 'driver_phone' not in wh_cols:
            conn.execute(text('ALTER TABLE warehouses ADD COLUMN driver_phone VARCHAR(20)'))
        if 'capacity' not in wh_cols:
            conn.execute(text('ALTER TABLE warehouses ADD COLUMN capacity REAL'))

        # inventory_checks 新字段（Phase D 轮岗盘点）
        ic_cols = [c['name'] for c in inspector.get_columns('inventory_checks')]
        if 'checker_id' not in ic_cols:
            conn.execute(text('ALTER TABLE inventory_checks ADD COLUMN checker_id INTEGER'))

        # products 新字段（Phase C 档案扩充）
        if 'brand' not in col_names:
            conn.execute(text('ALTER TABLE products ADD COLUMN brand VARCHAR(50)'))

        # customers 新字段（Phase C 档案扩充）
        if 'channel' not in cust_cols:
            conn.execute(text('ALTER TABLE customers ADD COLUMN channel VARCHAR(50)'))
        if 'customer_level' not in cust_cols:
            conn.execute(text('ALTER TABLE customers ADD COLUMN customer_level VARCHAR(20)'))

        # suppliers 新字段（Phase C 档案扩充）
        sup_cols = [c['name'] for c in inspector.get_columns('suppliers')]
        if 'channel' not in sup_cols:
            conn.execute(text('ALTER TABLE suppliers ADD COLUMN channel VARCHAR(50)'))

        # roles 新字段
        role_cols = [c['name'] for c in inspector.get_columns('roles')]
        if 'role_key' not in role_cols:
            conn.execute(text('ALTER TABLE roles ADD COLUMN role_key VARCHAR(20)'))
        if 'is_system' not in role_cols:
            conn.execute(text('ALTER TABLE roles ADD COLUMN is_system INTEGER DEFAULT 1'))
        if 'sort_order' not in role_cols:
            conn.execute(text('ALTER TABLE roles ADD COLUMN sort_order INTEGER DEFAULT 0'))
        if 'status' not in role_cols:
            conn.execute(text('ALTER TABLE roles ADD COLUMN status VARCHAR(10) DEFAULT "active"'))

        # customers 新字段
        cust_cols = [c['name'] for c in inspector.get_columns('customers')]
        if 'route_id' not in cust_cols:
            conn.execute(text('ALTER TABLE customers ADD COLUMN route_id INTEGER'))
        if 'salesman_ids' not in cust_cols:
            conn.execute(text('ALTER TABLE customers ADD COLUMN salesman_ids VARCHAR(200)'))
        if 'default_warehouse_id' not in cust_cols:
            conn.execute(text('ALTER TABLE customers ADD COLUMN default_warehouse_id INTEGER'))

        # sales_orders 新字段
        so_cols = [c['name'] for c in inspector.get_columns('sales_orders')]
        if 'route_id' not in so_cols:
            conn.execute(text('ALTER TABLE sales_orders ADD COLUMN route_id INTEGER'))
        if 'operator_id' not in so_cols:
            conn.execute(text('ALTER TABLE sales_orders ADD COLUMN operator_id INTEGER'))

        # invoices 表（发票管理用）
        tables = inspector.get_table_names()
        if 'invoices' not in tables:
            conn.execute(text('''CREATE TABLE invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_type VARCHAR(20) NOT NULL,
                invoice_code VARCHAR(50),
                invoice_no VARCHAR(50),
                related_id INTEGER,
                related_type VARCHAR(20),
                customer_id INTEGER,
                supplier_id INTEGER,
                amount REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                total_amount REAL DEFAULT 0,
                invoice_date DATE,
                status INTEGER DEFAULT 1,
                remark VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''))
        # operation_logs 表（操作日志用）
        if 'operation_logs' not in tables:
            conn.execute(text('''CREATE TABLE operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username VARCHAR(50),
                module VARCHAR(50),
                action VARCHAR(20),
                target_type VARCHAR(50),
                target_id INTEGER,
                target_name VARCHAR(200),
                detail TEXT,
                ip VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''))
        # routes 表（路线档案）
        if 'routes' not in tables:
            conn.execute(text('''CREATE TABLE routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(50) NOT NULL,
                warehouse_id INTEGER,
                sort_order INTEGER DEFAULT 0,
                description TEXT,
                status VARCHAR(10) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''))
        # audit_logs 表（审核记录）
        if 'audit_logs' not in tables:
            conn.execute(text('''CREATE TABLE audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_type VARCHAR(50) NOT NULL,
                target_id INTEGER NOT NULL,
                target_code VARCHAR(50),
                action VARCHAR(20) NOT NULL,
                comment TEXT,
                auditor_id INTEGER,
                auditor_name VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(50),
                device_info VARCHAR(200)
            )'''))
        # price_change_logs 表（价格变动）
        if 'price_change_logs' not in tables:
            conn.execute(text('''CREATE TABLE price_change_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                field_name VARCHAR(30),
                old_value NUMERIC(12,2),
                new_value NUMERIC(12,2),
                operator_id INTEGER,
                operator_name VARCHAR(50),
                change_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(50)
            )'''))
        # vehicle_sales_outs 表（车销出库）
        if 'vehicle_sales_outs' not in tables:
            conn.execute(text('''CREATE TABLE vehicle_sales_outs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(50) UNIQUE NOT NULL,
                employee_id INTEGER,
                vehicle_warehouse_id INTEGER,
                total_amount REAL DEFAULT 0,
                remark TEXT,
                status VARCHAR(20) DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confirmed_at TIMESTAMP
            )'''))
        # vehicle_returns 表（车销回库）
        if 'vehicle_returns' not in tables:
            conn.execute(text('''CREATE TABLE vehicle_returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(50) UNIQUE NOT NULL,
                vehicle_sales_out_id INTEGER,
                employee_id INTEGER,
                total_amount REAL DEFAULT 0,
                remark TEXT,
                status VARCHAR(20) DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confirmed_at TIMESTAMP
            )'''))
        # vehicle_losses 表（车销报损）
        if 'vehicle_losses' not in tables:
            conn.execute(text('''CREATE TABLE vehicle_losses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(50) UNIQUE NOT NULL,
                vehicle_sales_out_id INTEGER,
                employee_id INTEGER,
                total_amount REAL DEFAULT 0,
                reason TEXT,
                status VARCHAR(20) DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confirmed_at TIMESTAMP
            )'''))
        # warehouse_routes 表
        if 'warehouse_routes' not in tables:
            conn.execute(text('''CREATE TABLE warehouse_routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                warehouse_id INTEGER NOT NULL,
                route_id INTEGER NOT NULL,
                UNIQUE(warehouse_id, route_id)
            )'''))
        # employee_warehouses 表
        if 'employee_warehouses' not in tables:
            conn.execute(text('''CREATE TABLE employee_warehouses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                warehouse_id INTEGER NOT NULL,
                UNIQUE(employee_id, warehouse_id)
            )'''))
        # employee_routes 表
        if 'employee_routes' not in tables:
            conn.execute(text('''CREATE TABLE employee_routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                route_id INTEGER NOT NULL,
                UNIQUE(employee_id, route_id)
            )'''))
        # modules 表（权限模块）
        if 'modules' not in tables:
            conn.execute(text('''CREATE TABLE modules (
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''))
        # role_module_permissions 表
        if 'role_module_permissions' not in tables:
            conn.execute(text('''CREATE TABLE role_module_permissions (
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
            )'''))
        # operation_permissions 表
        if 'operation_permissions' not in tables:
            conn.execute(text('''CREATE TABLE operation_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_id INTEGER NOT NULL,
                operation_key VARCHAR(50) NOT NULL,
                allowed BOOLEAN DEFAULT 0,
                data_scope VARCHAR(20) DEFAULT 'all',
                UNIQUE(role_id, operation_key)
            )'''))
        # employee_roles 表
        if 'employee_roles' not in tables:
            conn.execute(text('''CREATE TABLE employee_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                UNIQUE(employee_id, role_id)
            )'''))
        conn.commit()

auto_migrate()

# 初始化默认角色
from routers.roles import init_default_roles, init_modules, init_role_permissions
from routers.print_templates import init_default_templates
db = SessionLocal()
try:
    init_default_roles(db)
    init_modules(db)
    init_role_permissions(db)
    init_default_templates(db)
finally:
    db.close()

app = FastAPI(
    title="FastInOut 快消品进销存管理系统",
    description="快消品进销存管理系统",
    version="0.4.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 0: HTTP 审计中间件
from middleware.audit import AuditMiddleware
app.add_middleware(AuditMiddleware)

# 注册路由
app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(company.router)
app.include_router(warehouses.router)
app.include_router(employees.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(suppliers.router)
app.include_router(inventory.router)
app.include_router(purchases.router)
app.include_router(sales.router)
app.include_router(finance.router)
app.include_router(reports.router)
app.include_router(system.router)
app.include_router(units.router)
app.include_router(promotions.router)
app.include_router(backup.router)
app.include_router(customer_prices.router)
app.include_router(crm.router)
app.include_router(salesmen.router)
app.include_router(batches.router)
app.include_router(bank.router)
app.include_router(print_templates.router)
app.include_router(data_import.router)
app.include_router(invoices.router)
app.include_router(supplier_recon.router)
app.include_router(route.router)
app.include_router(audit.router)
app.include_router(price_change.router)
app.include_router(vehicle.router)
app.include_router(operation_log.router)
app.include_router(message.router)
app.include_router(advance_deduction.router)
app.include_router(todos.router)
app.include_router(customer_visits.router)
app.include_router(sales_delivery.router)
app.include_router(purchase_receipt.router)
app.include_router(expense.router)
app.include_router(stocktaking.router)
app.include_router(sales_return_dlv.router)
app.include_router(audit_log.router)
app.include_router(account_ledger.router)
app.include_router(vehicle_load.router)
app.include_router(settlement.router)
app.include_router(advance_payment.router)
app.include_router(damage_report.router)
app.include_router(commission.router)
app.include_router(report_enhanced.router)
app.include_router(monitor.router)
app.include_router(reconciliation.router)
app.include_router(company_config.router)
app.include_router(purchase_return_dlv.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
