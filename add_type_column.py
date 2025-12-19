from app import app, db
import sqlite3
import os

# 连接到SQLite数据库
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'site.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 添加type字段到message表
try:
    cursor.execute("ALTER TABLE message ADD COLUMN type VARCHAR(10) DEFAULT 'text'")
    conn.commit()
    print("Successfully added 'type' column to message table")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column 'type' already exists in message table")
    else:
        print(f"Error adding column: {e}")

# 验证表结构
cursor.execute("PRAGMA table_info(message);")
columns = cursor.fetchall()
print("\nMessage table structure:")
for col in columns:
    print(f"  {col[1]} ({col[2]}) - Not Null: {bool(col[3])} - Default: {col[4]} - PK: {bool(col[5])}")

conn.close()