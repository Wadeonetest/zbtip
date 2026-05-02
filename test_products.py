import sqlite3

def get_connection():
    conn = sqlite3.connect("screen_recorder.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_vip_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, price, days, description, sort_order, status
        FROM vip_products 
        WHERE status = 1 
        ORDER BY sort_order ASC
    ''')
    products = cursor.fetchall()
    conn.close()
    return [dict(p) for p in products]

products = get_vip_products()
print("=== get_vip_products() 返回 ===")
for p in products:
    print(p)
print(f"\n总共有 {len(products)} 个商品")