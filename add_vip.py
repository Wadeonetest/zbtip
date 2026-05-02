import sqlite3
import os
from datetime import datetime, timedelta
import hashlib
import uuid

db_path = os.path.join(os.path.dirname(__file__), "screen_recorder.db")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== 为用户添加会员 ===")

phone = "22222222222"
vip_name = "月度会员"
vip_type = "month"
amount = 19.9
expire_date = "2026-05-03 23:59:59"

# 检查用户是否存在
cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
user = cursor.fetchone()

if not user:
    print("用户不存在，正在创建用户...")

    # 创建默认用户
    hashed_pwd = hashlib.sha256("123456".encode()).hexdigest()
    now = datetime.utcnow() + timedelta(hours=8)
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        INSERT INTO users (phone, password_hash, nickname, login_type, remaining_marks, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (phone, hashed_pwd, "VIP用户", "phone", 2, now_str, now_str))

    user_id = cursor.lastrowid
    print("用户已创建，ID: {}".format(user_id))
else:
    user_id = user['id']
    print("找到用户，ID: {}, 昵称: {}".format(user_id, user['nickname']))

# 为用户购买VIP
now = datetime.utcnow() + timedelta(hours=8)
start_str = now.strftime('%Y-%m-%d %H:%M:%S')

purchase_id = str(uuid.uuid4())
order_no = "VIP{}".format(now.strftime('%Y%m%d%H%M%S'))

cursor.execute('''
    INSERT INTO vip_purchases (id, user_id, vip_type, vip_name, duration_days, start_at, expire_at, order_no, amount, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (purchase_id, user_id, vip_type, vip_name, 30, start_str, expire_date, order_no, amount, start_str))

# 更新用户状态
vip_marks = 999999999
cursor.execute('''
    UPDATE users SET is_vip = 1, vip_expire_at = ?, remaining_marks = ?, updated_at = ? WHERE id = ?
''', (expire_date, vip_marks, start_str, user_id))

conn.commit()

# 验证
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
updated_user = cursor.fetchone()
print("\n更新后用户信息：")
print("  昵称: {}".format(updated_user['nickname']))
print("  是否VIP: {}".format("是" if updated_user['is_vip'] else "否"))
print("  VIP过期时间: {}".format(updated_user['vip_expire_at']))
print("  剩余标记次数: {}".format(updated_user['remaining_marks']))

conn.close()

print("\n=== 完成 ===")
