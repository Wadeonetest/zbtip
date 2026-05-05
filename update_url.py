import sqlite3
import os
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screen_recorder.db')
print(f"数据库路径: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("UPDATE version_history SET update_url='http://127.0.0.1:8888/update_v1.1.0.exe' WHERE is_latest=1")
conn.commit()
cursor.execute('SELECT * FROM version_history')
for row in cursor.fetchall():
    print(row)
conn.close()
print()
print('已更新 update_url 为 http://127.0.0.1:8888/update_v1.1.0.exe')