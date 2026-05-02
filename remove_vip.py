import sqlite3
import os
from datetime import datetime, timedelta

db_path = os.path.join(os.path.dirname(__file__), "screen_recorder.db")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== 将用户改为非会员 ===")

phone = "18943057927"

# 检查用户是否存在
cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
user = cursor.fetchone()

if not user:
    print("手机号 {} 的用户不存在！".format(phone))
else:
    user_id = user['id']
    print("找到用户，ID: {}, 昵称: {}".format(user_id, user['nickname']))
    print("  当前是否VIP: {}".format("是" if user['is_vip'] else "否"))
    print("  VIP过期时间: {}".format(user['vip_expire_at']))

    # 更新用户状态为非会员
    now = datetime.utcnow() + timedelta(hours=8)
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    
    default_marks = 2  # 非会员默认次数
    
    cursor.execute('''
        UPDATE users SET is_vip = 0, vip_expire_at = NULL, remaining_marks = ?, updated_at = ? WHERE id = ?
    ''', (default_marks, now_str, user_id))

    # 同时更新VIP购买记录状态为过期（可选）
    cursor.execute('''
        UPDATE vip_purchases SET status = 0 WHERE user_id = ? AND status = 1
    ''', (user_id,))

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