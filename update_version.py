import sqlite3
conn = sqlite3.connect('screen_recorder.db')
cursor = conn.cursor()
cursor.execute("UPDATE version_history SET version='v1.1.0', changelog='1. 新增版本检测功能\n2. 新增法律声明\n3. 新增用户协议' WHERE is_latest=1")
conn.commit()
print('已更新版本为 v1.1.0')
cursor.execute('SELECT * FROM version_history')
for row in cursor.fetchall():
    print(row)
conn.close()