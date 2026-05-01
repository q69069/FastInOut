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
