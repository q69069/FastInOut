"""
初始化数据库 - 创建所有新表
"""
import sys
sys.path.insert(0, '.')

from database import engine, Base
from models.route import Route
from models.audit import AuditLog
from models.price_change import PriceChangeLog
from models.vehicle import VehicleSalesOut, VehicleReturn, VehicleLoss
from models.warehouse_route import WarehouseRoute
from models.employee_warehouse import EmployeeWarehouse
from models.employee_route import EmployeeRoute
from models.employee import Employee
from models.customer import Customer


def init_db():
    print("正在创建所有新表...")
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成！")


if __name__ == "__main__":
    init_db()
