import sqlite3

db = "robot_vision_history.db"

conn = sqlite3.connect(db)
cursor = conn.cursor()

cursor.execute(
    "DELETE FROM vision_history WHERE product_name = ?",
    ("Mouse",)
)

deleted = cursor.rowcount

conn.commit()
conn.close()

print(f"Deleted Mouse scan records: {deleted}")