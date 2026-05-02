import sqlite3

conn = sqlite3.connect("screen_recorder.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM vip_products")
products = cursor.fetchall()

print("=== vip_products 表内容 ===")
for p in products:
    print(p)

print(f"\n总共有 {len(products)} 条记录")

conn.close()