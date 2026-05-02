import sqlite3
conn = sqlite3.connect('fastinout.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Total tables:', len(tables))

for table in ['employees', 'roles', 'warehouses', 'products']:
    try:
        cursor.execute('PRAGMA table_info(' + table + ')')
        cols = cursor.fetchall()
        print(table + ':', len(cols), 'columns -', [c[1] for c in cols])
    except Exception as e:
        print(table + ': ERROR -', e)

conn.close()
