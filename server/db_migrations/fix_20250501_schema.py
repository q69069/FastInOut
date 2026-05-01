"""
数据库Schema修复脚本 - 2026-05-01
修复SQLAlchemy模型与SQLite数据库不同步的问题

使用方法:
    cd server
    python db_migrations/fix_20250501_schema.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'fastinout.db')

def fix_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Fixing schema for: {DB_PATH}")
    
    # 1. Fix warehouses table - add missing columns
    cursor.execute("SELECT name FROM pragma_table_info('warehouses') WHERE name='warehouse_type'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE warehouses ADD COLUMN warehouse_type VARCHAR(20) DEFAULT 'normal'")
        print("  + Added warehouses.warehouse_type")
    
    cursor.execute("SELECT name FROM pragma_table_info('warehouses') WHERE name='description'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE warehouses ADD COLUMN description VARCHAR(500)")
        print("  + Added warehouses.description")
    
    # 2. Fix products table - add base_unit_id
    cursor.execute("SELECT name FROM pragma_table_info('products') WHERE name='base_unit_id'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE products ADD COLUMN base_unit_id INTEGER")
        print("  + Added products.base_unit_id")
    
    # 3. Fix receipts table - add matched
    cursor.execute("SELECT name FROM pragma_table_info('receipts') WHERE name='matched'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE receipts ADD COLUMN matched BOOLEAN DEFAULT 0")
        print("  + Added receipts.matched")
    
    # 4. Fix payments table - add matched
    cursor.execute("SELECT name FROM pragma_table_info('payments') WHERE name='matched'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE payments ADD COLUMN matched BOOLEAN DEFAULT 0")
        print("  + Added payments.matched")
    
    # 5. Create inventory_flow table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_flow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            flow_type VARCHAR(20) NOT NULL,
            quantity FLOAT NOT NULL,
            before_qty FLOAT DEFAULT 0,
            after_qty FLOAT DEFAULT 0,
            reference_type VARCHAR(50),
            reference_id INTEGER,
            reference_code VARCHAR(50),
            remark VARCHAR(500),
            operator_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
        )
    """)
    print("  + Created inventory_flow table")
    
    conn.commit()
    conn.close()
    print("\nSchema fix completed!")

if __name__ == "__main__":
    fix_schema()
