"""
商品三单位字段迁移

使用方法:
    cd server
    python db_migrations/add_three_unit_fields.py
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

    print(f"Adding three-unit fields to: {DB_PATH}\n")

    add_column(cursor, 'products', 'small_unit_name', "VARCHAR(20) DEFAULT ''")
    add_column(cursor, 'products', 'medium_unit_name', "VARCHAR(20)")
    add_column(cursor, 'products', 'medium_conv_rate', "FLOAT")
    add_column(cursor, 'products', 'large_unit_name', "VARCHAR(20)")
    add_column(cursor, 'products', 'large_conv_rate', "FLOAT")
    add_column(cursor, 'products', 'default_unit_level', "VARCHAR(10) DEFAULT 'small'")

    # 迁移现有 unit → small_unit_name
    cursor.execute("UPDATE products SET small_unit_name = COALESCE(unit, '') WHERE small_unit_name IS NULL OR small_unit_name = ''")
    cursor.execute("UPDATE products SET default_unit_level = 'small' WHERE default_unit_level IS NULL OR default_unit_level = ''")

    conn.commit()
    conn.close()
    print("\nThree-unit fields migration completed!")


if __name__ == "__main__":
    fix_schema()
