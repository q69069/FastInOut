import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from routers import (
    auth, company, warehouses, employees,
    categories, products, customers, suppliers,
    inventory, purchases, sales, finance,
    reports, system, units, promotions, roles,
    backup, customer_prices, crm, salesmen, batches, bank,
    print_templates, data_import, invoices, supplier_recon,
    route, audit, price_change, vehicle
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

        # customers 新字段
        cust_cols = [c['name'] for c in inspector.get_columns('customers')]
        if 'route_id' not in cust_cols:
            conn.execute(text('ALTER TABLE customers ADD COLUMN route_id INTEGER'))
        if 'salesman_ids' not in cust_cols:
            conn.execute(text('ALTER TABLE customers ADD COLUMN salesman_ids VARCHAR(200)'))
        if 'default_warehouse_id' not in cust_cols:
            conn.execute(text('ALTER TABLE customers ADD COLUMN default_warehouse_id INTEGER'))

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
        conn.commit()

auto_migrate()

# 初始化默认角色
from routers.roles import init_default_roles
from routers.print_templates import init_default_templates
db = SessionLocal()
try:
    init_default_roles(db)
    init_default_templates(db)
finally:
    db.close()

app = FastAPI(
    title="FastInOut 快消品进销存管理系统",
    description="快消品进销存管理系统",
    version="0.3.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
