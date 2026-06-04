import sqlite3

conn = sqlite3.connect("files.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    file_type TEXT,
    size INTEGER,
    upload_date TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully!")