"""
添加单位字段到所有单据明细表

使用方法:
    cd server
    python db_migrations/add_unit_fields.py
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

    print(f"Adding unit fields to: {DB_PATH}\n")

    tables = [
        'purchase_order_items',
        'purchase_stockin_items',
        'purchase_return_items',
        'purchase_return_delivery_items',
        'purchase_receipt_items',
        'sales_order_items',
        'sales_stockout_items',
        'sales_return_items',
        'sales_delivery_items',
        'inventory_transfer_items',
        'inventory_check_items',
        'vehicle_load_items',
        'damage_report_items',
    ]

    for table in tables:
        add_column(cursor, table, 'unit_id', "INTEGER")
        add_column(cursor, table, 'unit_quantity', "FLOAT DEFAULT 1")
        add_column(cursor, table, 'unit_conv_rate', "FLOAT DEFAULT 1")

    conn.commit()
    conn.close()
    print("\nUnit fields migration completed!")


if __name__ == "__main__":
    fix_schema()
