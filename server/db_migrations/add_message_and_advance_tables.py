"""
数据库Schema修复脚本 - 2026-05-02
添加消息中心和预收预付抵扣表

使用方法:
    cd server
    python db_migrations/add_message_and_advance_tables.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'fastinout.db')


def table_exists(cursor, table):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cursor.fetchone() is not None


def fix_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"Fixing schema for: {DB_PATH}\n")

    # 1. Create messages table
    if not table_exists(cursor, 'messages'):
        cursor.execute("""
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type VARCHAR(20),
                title VARCHAR(200),
                content TEXT,
                recipient_id INTEGER,
                sender_id INTEGER,
                status VARCHAR(20) DEFAULT 'unread',
                reference_type VARCHAR(50),
                reference_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                FOREIGN KEY (recipient_id) REFERENCES employees(id),
                FOREIGN KEY (sender_id) REFERENCES employees(id)
            )
        """)
        print("  + Created messages table")
    else:
        print("  - messages table already exists")

    # 2. Create advance_deductions table
    if not table_exists(cursor, 'advance_deductions'):
        cursor.execute("""
            CREATE TABLE advance_deductions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type VARCHAR(10) NOT NULL,
                customer_id INTEGER,
                supplier_id INTEGER,
                source_type VARCHAR(20) NOT NULL,
                source_id INTEGER NOT NULL,
                source_code VARCHAR(50),
                order_type VARCHAR(20) NOT NULL,
                order_id INTEGER NOT NULL,
                order_code VARCHAR(50),
                amount FLOAT NOT NULL,
                remark TEXT,
                operator_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
                FOREIGN KEY (operator_id) REFERENCES employees(id)
            )
        """)
        print("  + Created advance_deductions table")
    else:
        print("  - advance_deductions table already exists")

    conn.commit()
    conn.close()
    print("\nSchema fix completed!")


if __name__ == "__main__":
    fix_schema()