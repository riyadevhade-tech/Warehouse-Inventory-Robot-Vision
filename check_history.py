import sqlite3

conn = sqlite3.connect("robot_vision_history.db")

rows = conn.execute(
    "SELECT scan_id, product_name, detected_objects, status, scan_time "
    "FROM vision_history ORDER BY scan_id DESC"
).fetchall()

for row in rows:
    print(row)

conn.close()