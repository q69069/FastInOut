"""
数据库Schema修复脚本 - 2026-05-02
添加审核字段到所有单据表

使用方法:
    cd server
    python db_migrations/add_audit_fields.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'fastinout.db')


def column_exists(cursor, table, column):
    cursor.execute(f"SELECT name FROM pragma_table_info('{table}') WHERE name=?", (column,))
    return cursor.fetchone() is not None


def add_column(cursor, table, column, definition):
    if not column_exists(cursor, table, column):
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"  + Added {table}.{column}")


def fix_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"Fixing schema for: {DB_PATH}\n")

    # 1. purchase_orders - add audit fields
    add_column(cursor, 'purchase_orders', 'audit_status', "VARCHAR(20) DEFAULT 'pending'")
    add_column(cursor, 'purchase_orders', 'auditor_id', "INTEGER")
    add_column(cursor, 'purchase_orders', 'audit_time', "TIMESTAMP")
    add_column(cursor, 'purchase_orders', 'audit_comment', "TEXT")

    # 2. purchase_stockins - add audit fields
    add_column(cursor, 'purchase_stockins', 'audit_status', "VARCHAR(20) DEFAULT 'pending'")
    add_column(cursor, 'purchase_stockins', 'auditor_id', "INTEGER")
    add_column(cursor, 'purchase_stockins', 'audit_time', "TIMESTAMP")
    add_column(cursor, 'purchase_stockins', 'audit_comment', "TEXT")

    # 3. purchase_returns - add audit fields
    add_column(cursor, 'purchase_returns', 'audit_status', "VARCHAR(20) DEFAULT 'pending'")
    add_column(cursor, 'purchase_returns', 'auditor_id', "INTEGER")
    add_column(cursor, 'purchase_returns', 'audit_time', "TIMESTAMP")
    add_column(cursor, 'purchase_returns', 'audit_comment', "TEXT")

    # 4. sales_orders - add audit fields
    add_column(cursor, 'sales_orders', 'audit_status', "VARCHAR(20) DEFAULT 'pending'")
    add_column(cursor, 'sales_orders', 'auditor_id', "INTEGER")
    add_column(cursor, 'sales_orders', 'audit_time', "TIMESTAMP")
    add_column(cursor, 'sales_orders', 'audit_comment', "TEXT")

    # 5. sales_stockouts - add audit fields
    add_column(cursor, 'sales_stockouts', 'audit_status', "VARCHAR(20) DEFAULT 'pending'")
    add_column(cursor, 'sales_stockouts', 'auditor_id', "INTEGER")
    add_column(cursor, 'sales_stockouts', 'audit_time', "TIMESTAMP")
    add_column(cursor, 'sales_stockouts', 'audit_comment', "TEXT")

    # 6. sales_returns - add audit fields
    add_column(cursor, 'sales_returns', 'audit_status', "VARCHAR(20) DEFAULT 'pending'")
    add_column(cursor, 'sales_returns', 'auditor_id', "INTEGER")
    add_column(cursor, 'sales_returns', 'audit_time', "TIMESTAMP")
    add_column(cursor, 'sales_returns', 'audit_comment', "TEXT")

    # 7. inventory_transfers - add audit fields
    add_column(cursor, 'inventory_transfers', 'audit_status', "VARCHAR(20) DEFAULT 'pending'")
    add_column(cursor, 'inventory_transfers', 'auditor_id', "INTEGER")
    add_column(cursor, 'inventory_transfers', 'audit_time', "TIMESTAMP")
    add_column(cursor, 'inventory_transfers', 'audit_comment', "TEXT")

    # 8. vehicle_sales_outs - add audit fields
    add_column(cursor, 'vehicle_sales_outs', 'audit_status', "VARCHAR(20) DEFAULT 'pending'")
    add_column(cursor, 'vehicle_sales_outs', 'auditor_id', "INTEGER")
    add_column(cursor, 'vehicle_sales_outs', 'audit_time', "TIMESTAMP")
    add_column(cursor, 'vehicle_sales_outs', 'audit_comment', "TEXT")

    # 9. vehicle_returns - add audit fields
    add_column(cursor, 'vehicle_returns', 'audit_status', "VARCHAR(20) DEFAULT 'pending'")
    add_column(cursor, 'vehicle_returns', 'auditor_id', "INTEGER")
    add_column(cursor, 'vehicle_returns', 'audit_time', "TIMESTAMP")
    add_column(cursor, 'vehicle_returns', 'audit_comment', "TEXT")

    # 10. vehicle_losses - add audit fields
    add_column(cursor, 'vehicle_losses', 'audit_status', "VARCHAR(20) DEFAULT 'pending'")
    add_column(cursor, 'vehicle_losses', 'auditor_id', "INTEGER")
    add_column(cursor, 'vehicle_losses', 'audit_time', "TIMESTAMP")
    add_column(cursor, 'vehicle_losses', 'audit_comment', "TEXT")

    conn.commit()
    conn.close()
    print("\nSchema fix completed!")


if __name__ == "__main__":
    fix_schema()