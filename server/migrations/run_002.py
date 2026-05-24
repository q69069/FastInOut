"""运行 002_add_reverse_columns 迁移脚本"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "fastinout.db")

COLUMNS = [
    ("sales_orders", "reverse_reason", "VARCHAR(200)"),
    ("sales_orders", "reversed_by", "INTEGER"),
    ("sales_orders", "reversed_at", "DATETIME"),
    ("sales_stockouts", "reverse_reason", "VARCHAR(200)"),
    ("sales_stockouts", "reversed_by", "INTEGER"),
    ("sales_stockouts", "reversed_at", "DATETIME"),
    ("sales_returns", "reverse_reason", "VARCHAR(200)"),
    ("sales_returns", "reversed_by", "INTEGER"),
    ("sales_returns", "reversed_at", "DATETIME"),
    ("purchase_orders", "reverse_reason", "VARCHAR(200)"),
    ("purchase_orders", "reversed_by", "INTEGER"),
    ("purchase_orders", "reversed_at", "DATETIME"),
    ("purchase_stockins", "reverse_reason", "VARCHAR(200)"),
    ("purchase_stockins", "reversed_by", "INTEGER"),
    ("purchase_stockins", "reversed_at", "DATETIME"),
    ("purchase_returns", "reverse_reason", "VARCHAR(200)"),
    ("purchase_returns", "reversed_by", "INTEGER"),
    ("purchase_returns", "reversed_at", "DATETIME"),
    ("purchase_receipts", "reverse_reason", "VARCHAR(200)"),
    ("purchase_receipts", "reversed_by", "INTEGER"),
    ("purchase_receipts", "reversed_at", "DATETIME"),
    ("purchase_return_deliveries", "reverse_reason", "VARCHAR(200)"),
    ("purchase_return_deliveries", "reversed_by", "INTEGER"),
    ("purchase_return_deliveries", "reversed_at", "DATETIME"),
    ("sales_deliveries", "reverse_reason", "VARCHAR(200)"),
    ("sales_deliveries", "reversed_by", "INTEGER"),
    ("sales_deliveries", "reversed_at", "DATETIME"),
]

def run():
    if not os.path.exists(DB_PATH):
        print(f"数据库不存在: {DB_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for table, col, col_type in COLUMNS:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
            print(f"  + {table}.{col}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"  = {table}.{col} (已存在)")
            else:
                print(f"  ! {table}.{col}: {e}")
    conn.commit()
    conn.close()
    print("迁移完成")

if __name__ == "__main__":
    run()
