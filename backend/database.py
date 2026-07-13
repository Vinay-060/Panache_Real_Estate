import sqlite3

conn = sqlite3.connect(
    "panache.db",
    check_same_thread=False
)

cur = conn.cursor()

cur.execute("""

CREATE TABLE IF NOT EXISTS users(

user_id TEXT PRIMARY KEY,

conversation TEXT,

saved INTEGER DEFAULT 0

)

""")

conn.commit()