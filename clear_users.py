import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "screen_recorder.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 清空用户信息表 ===")

# 检查是否有用户数据
cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
print(f"当前用户数量: {count}")

if count > 0:
    # 清空用户表（保留表结构）
    cursor.execute("DELETE FROM users")
    # 重置自增ID
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
    # 同时清空VIP购买记录
    cursor.execute("DELETE FROM vip_purchases")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='vip_purchases'")
    conn.commit()
    
    # 验证
    cursor.execute("SELECT COUNT(*) FROM users")
    new_count = cursor.fetchone()[0]
    print(f"清空后用户数量: {new_count}")
    print("✅ 用户信息表已清空！")
else:
    print("ℹ️ 用户信息表已经是空的")

conn.close()

print("\n=== 完成 ===")
