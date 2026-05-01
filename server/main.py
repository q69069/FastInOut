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
    print_templates, data_import
)

# 创建所有表
Base.metadata.create_all(bind=engine)

# 自动迁移：添加缺失的列
from sqlalchemy import text, inspect
def auto_migrate():
    inspector = inspect(engine)
    with engine.connect() as conn:
        # products.level_prices
        cols = [c['name'] for c in inspector.get_columns('products')]
        if 'level_prices' not in cols:
            conn.execute(text('ALTER TABLE products ADD COLUMN level_prices VARCHAR(500)'))
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


@app.get("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
