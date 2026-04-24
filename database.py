import sqlite3
DB_NAME = "users.db"
def get_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE,password TEXT)
    """)
    conn.commit()
    conn.close()