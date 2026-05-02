
import sqlite3
import hashlib
import os

db_path = r'd:\代码存档\zbtip\screen_recorder.db'

print("="*80)
print("🔍 数据库连接测试")
print("="*80)

# 检查数据库文件是否存在
print(f"\n1. 检查数据库文件:")
print(f"   路径: {db_path}")
print(f"   文件存在: {os.path.exists(db_path)}")

if not os.path.exists(db_path):
    print("   ❌ 数据库文件不存在，程序会自动创建")
    print("   现在手动创建表结构...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            phone TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            nickname TEXT,
            avatar TEXT,
            login_type TEXT NOT NULL,
            wechat_openid TEXT UNIQUE,
            is_vip BOOLEAN DEFAULT 0,
            vip_expire_at DATETIME,
            last_login_at DATETIME,
            status INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vip_purchases (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            vip_type TEXT NOT NULL,
            vip_name TEXT NOT NULL,
            duration_days INTEGER NOT NULL,
            start_at DATETIME NOT NULL,
            expire_at DATETIME,
            order_no TEXT UNIQUE,
            amount REAL NOT NULL,
            status INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("   ✅ 表结构创建成功！")
else:
    print("   ✅ 数据库文件存在")

# 连接数据库
print(f"\n2. 连接数据库...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
print("   ✅ 连接成功")

# 检查表是否存在
print(f"\n3. 检查表:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"   表列表: {[t[0] for t in tables]}")

# 检查当前记录数
print(f"\n4. 当前users表记录数:")
cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
print(f"   记录数: {count}")

# 如果有记录，显示所有
if count > 0:
    print(f"\n5. 当前用户数据:")
    cursor.execute("SELECT * FROM users")
    for row in cursor.fetchall():
        print(f"   {row}")
else:
    print(f"\n5. 插入测试数据...")
    
    # 密码加密
    raw_password = "wdx971104"
    password_hash = hashlib.sha256(raw_password.encode()).hexdigest()
    print(f"   原始密码: {raw_password}")
    print(f"   加密后: {password_hash}")
    
    try:
        cursor.execute('''
            INSERT INTO users (
                email, phone, password_hash, nickname, login_type,
                is_vip, vip_expire_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            '2051103849@qq.com',
            '18943057927',
            password_hash,
            'wade',
            'email',
            0,
            '2026-05-01 00:00:00',
            1
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        print(f"   ✅ 插入成功！user_id = {user_id}")
        
        # 立即查询验证
        print(f"\n6. 验证插入结果:")
        cursor.execute("SELECT COUNT(*) FROM users")
        new_count = cursor.fetchone()[0]
        print(f"   现在记录数: {new_count}")
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            print(f"   用户数据: {user}")
        
    except sqlite3.Error as e:
        print(f"   ❌ 插入失败: {e}")

conn.close()

print("\n" + "="*80)
print("✅ 脚本执行完成！")
print("="*80)
