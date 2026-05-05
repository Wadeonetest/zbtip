
import sqlite3

conn = sqlite3.connect(r'd:\代码存档\zbtip\screen_recorder.db')
cursor = conn.cursor()

print("="*100)
print("📊 本地数据库详细结构说明")
print("="*100)

# ================== users 表结构说明 ==================
print("\n🔵 " + "="*100)
print("users 表（用户账号表）")
print("="*100)

users_schema = {
    "id": {"中文名": "用户ID", "类型": "INTEGER", "主键": "是", "自增": "是", "说明": "用户唯一标识符，系统自动生成"},
    "email": {"中文名": "邮箱", "类型": "TEXT", "唯一": "是", "说明": "用户邮箱地址，用于登录"},
    "phone": {"中文名": "手机号", "类型": "TEXT", "唯一": "是", "说明": "用户手机号，用于登录"},
    "password_hash": {"中文名": "密码哈希", "类型": "TEXT", "说明": "SHA256加密后的密码"},
    "nickname": {"中文名": "昵称", "类型": "TEXT", "说明": "用户显示名称"},
    "avatar": {"中文名": "头像URL", "类型": "TEXT", "说明": "用户头像图片地址"},
    "login_type": {"中文名": "登录类型", "类型": "TEXT", "说明": "登录方式：email/phone/wechat"},
    "wechat_openid": {"中文名": "微信OpenID", "类型": "TEXT", "唯一": "是", "说明": "微信授权登录的唯一标识"},
    "is_vip": {"中文名": "是否VIP", "类型": "BOOLEAN", "默认值": "0", "说明": "是否VIP会员：0否/1是"},
    "vip_expire_at": {"中文名": "VIP到期时间", "类型": "DATETIME", "说明": "会员过期时间，NULL表示永久"},
    "last_login_at": {"中文名": "最后登录时间", "类型": "DATETIME", "说明": "用户最后一次登录的时间"},
    "remaining_marks": {"中文名": "剩余标记次数", "类型": "INTEGER", "默认值": "0", "说明": "剩余标记进度功能使用次数"},
    "status": {"中文名": "账号状态", "类型": "INTEGER", "默认值": "1", "说明": "账号状态：0禁用/1启用"},
    "created_at": {"中文名": "创建时间", "类型": "DATETIME", "说明": "账号注册时间"},
    "updated_at": {"中文名": "更新时间", "类型": "DATETIME", "说明": "账号信息最后修改时间"}
}

print("\n【字段列表】")
print(f"{'字段名':<20} {'中文名':<12} {'数据类型':<12} {'键/约束':<16} {'默认值':<10} {'说明'}")
print("-" * 100)
for field, info in users_schema.items():
    keys_constraints = []
    if info.get("主键"): keys_constraints.append("主键")
    if info.get("自增"): keys_constraints.append("自增")
    if info.get("唯一"): keys_constraints.append("唯一")
    keys_str = "/".join(keys_constraints) if keys_constraints else "-"
    default = info.get("默认值", "-")
    print(f"{field:<20} {info['中文名']:<12} {info['类型']:<12} {keys_str:<16} {str(default):<10} {info['说明']}")

# 查询实际数据
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
print(f"\n【数据统计】: 共 {len(users)} 条记录")

if users:
    columns = [desc[0] for desc in cursor.description]
    for idx, user in enumerate(users, 1):
        print(f"\n--- 用户 {idx} ---")
        for col_name, value in zip(columns, user):
            field_info = users_schema.get(col_name, {"中文名": "-", "类型": "-"})
            value_display = value if value is not None else "(NULL)"
            print(f"  {col_name} ({field_info['中文名']}): {value_display}")
else:
    print("\n  ⚠️ 表为空（还没有注册用户）")

# ================== vip_purchases 表结构说明 ==================
print("\n\n🟡 " + "="*100)
print("vip_purchases 表（VIP购买记录表）")
print("="*100)

vip_schema = {
    "id": {"中文名": "记录ID", "类型": "TEXT", "主键": "是", "说明": "UUID格式的唯一标识符"},
    "user_id": {"中文名": "用户ID", "类型": "INTEGER", "外键": "是", "说明": "关联users表的id"},
    "vip_type": {"中文名": "VIP类型", "类型": "TEXT", "说明": "会员类型：month(月度)/year(年度)/lifetime(终身)"},
    "vip_name": {"中文名": "VIP名称", "类型": "TEXT", "说明": "会员名称，如'月度会员'、'年度会员'"},
    "duration_days": {"中文名": "时长(天)", "类型": "INTEGER", "说明": "会员天数：月度30/年度365/终身NULL"},
    "start_at": {"中文名": "开始时间", "类型": "DATETIME", "说明": "会员生效开始时间"},
    "expire_at": {"中文名": "到期时间", "类型": "DATETIME", "说明": "会员到期时间，NULL表示永久"},
    "order_no": {"中文名": "订单号", "类型": "TEXT", "唯一": "是", "说明": "购买订单号，格式：VIP+时间戳"},
    "amount": {"中文名": "金额", "类型": "REAL", "说明": "购买金额（元）"},
    "status": {"中文名": "状态", "类型": "INTEGER", "默认值": "1", "说明": "记录状态：0已取消/1有效/2已过期"},
    "created_at": {"中文名": "创建时间", "类型": "DATETIME", "说明": "购买记录创建时间"}
}

print("\n【字段列表】")
print(f"{'字段名':<20} {'中文名':<12} {'数据类型':<12} {'键/约束':<16} {'默认值':<10} {'说明'}")
print("-" * 100)
for field, info in vip_schema.items():
    keys_constraints = []
    if info.get("主键"): keys_constraints.append("主键")
    if info.get("外键"): keys_constraints.append("外键")
    if info.get("唯一"): keys_constraints.append("唯一")
    keys_str = "/".join(keys_constraints) if keys_constraints else "-"
    default = info.get("默认值", "-")
    print(f"{field:<20} {info['中文名']:<12} {info['类型']:<12} {keys_str:<16} {str(default):<10} {info['说明']}")

# 查询实际数据
cursor.execute("SELECT * FROM vip_purchases")
purchases = cursor.fetchall()
print(f"\n【数据统计】: 共 {len(purchases)} 条记录")

if purchases:
    columns = [desc[0] for desc in cursor.description]
    for idx, purchase in enumerate(purchases, 1):
        print(f"\n--- VIP购买记录 {idx} ---")
        for col_name, value in zip(columns, purchase):
            field_info = vip_schema.get(col_name, {"中文名": "-", "类型": "-"})
            value_display = value if value is not None else "(NULL)"
            print(f"  {col_name} ({field_info['中文名']}): {value_display}")
else:
    print("\n  ⚠️ 表为空（还没有VIP购买记录）")

# ================== config 表结构说明 ==================
print("\n\n🟢 " + "="*100)
print("config 表（功能配置表）")
print("="*100)

config_schema = {
    "id": {"中文名": "配置ID", "类型": "INTEGER", "主键": "是", "说明": "配置唯一标识符"},
    "name": {"中文名": "配置名称", "类型": "TEXT", "唯一": "是", "说明": "配置项名称"},
    "value": {"中文名": "配置值", "类型": "TEXT", "说明": "配置项的值"},
    "description": {"中文名": "配置描述", "类型": "TEXT", "说明": "配置项的说明"}
}

print("\n【字段列表】")
print(f"{'字段名':<20} {'中文名':<12} {'数据类型':<12} {'键/约束':<16} {'说明'}")
print("-" * 100)
for field, info in config_schema.items():
    keys_constraints = []
    if info.get("主键"): keys_constraints.append("主键")
    if info.get("唯一"): keys_constraints.append("唯一")
    keys_str = "/".join(keys_constraints) if keys_constraints else "-"
    print(f"{field:<20} {info['中文名']:<12} {info['类型']:<12} {keys_str:<16} {info['说明']}")

# 查询实际数据
cursor.execute("SELECT * FROM config")
configs = cursor.fetchall()
print(f"\n【数据统计】: 共 {len(configs)} 条记录")

if configs:
    columns = [desc[0] for desc in cursor.description]
    for idx, config in enumerate(configs, 1):
        print(f"\n--- 配置项 {idx} ---")
        for col_name, value in zip(columns, config):
            field_info = config_schema.get(col_name, {"中文名": "-", "类型": "-"})
            value_display = value if value is not None else "(NULL)"
            print(f"  {col_name} ({field_info['中文名']}): {value_display}")
else:
    print("\n  ⚠️ 表为空（还没有配置数据）")

# ================== 数据库统计信息 ==================
print("\n\n📋 " + "="*100)
print("数据库统计信息")
print("="*100)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\n数据库文件: screen_recorder.db")
print(f"表数量: {len(tables)}")
print("\n各表记录数:")
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  - {table_name}: {count} 条记录")

conn.close()
print("\n" + "="*100)
print("✅ 查询结束")
print("="*100)
