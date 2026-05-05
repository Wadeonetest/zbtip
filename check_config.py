import sqlite3

conn = sqlite3.connect(r'd:\代码存档\zbtip\screen_recorder.db')
cursor = conn.cursor()

cursor.execute("SELECT id, name, value, description FROM config WHERE name LIKE '%title%' OR description LIKE '%标记助手%' OR value LIKE '%标记助手%'")
results = cursor.fetchall()

print("查找包含'标记助手'的配置:")
for row in results:
    print(f"  id: {row[0]}, name: {row[1]}, value: {row[2]}, description: {row[3]}")

if not results:
    print("  未找到包含'标记助手'的配置记录")

conn.close()
