"""
商品品牌ID字段迁移

使用方法:
    cd server
    python db_migrations/add_brand_id_to_products.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'fastinout.db')


def column_exists(cursor, table, column):
    cursor.execute(f"SELECT name FROM pragma_table_info('{table}') WHERE name=?", (column,))
    return cursor.fetchone() is not None


def fix_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"Adding brand_id to: {DB_PATH}\n")

    if not column_exists(cursor, 'products', 'brand_id'):
        cursor.execute("ALTER TABLE products ADD COLUMN brand_id INTEGER")
        print("  + Added products.brand_id")

    conn.commit()
    conn.close()
    print("\nBrand ID migration completed!")


if __name__ == "__main__":
    fix_schema()
