import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import (
    auth, company, warehouses, employees,
    categories, products, customers, suppliers,
    inventory, purchases, sales, finance,
    reports, system
)

# 创建所有表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastInOut 快消品进销存管理系统",
    description="快消品进销存管理系统",
    version="0.2.0"
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


@app.get("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
