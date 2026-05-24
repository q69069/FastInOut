"""创建 token_blacklist 表"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "fastinout.db")


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS token_blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_hash VARCHAR(64) UNIQUE NOT NULL,
            expires_at DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_token_blacklist_hash ON token_blacklist(token_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_token_blacklist_expires ON token_blacklist(expires_at)")
    conn.commit()
    conn.close()
    print("token_blacklist 表创建完成")


if __name__ == "__main__":
    migrate()
