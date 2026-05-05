import sqlite3

conn = sqlite3.connect(r'd:\代码存档\zbtip\screen_recorder.db')
cursor = conn.cursor()

print('=' * 80)
print('直播录屏标记助手 - 数据库全部内容')
print('=' * 80)
print()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

for (table_name,) in tables:
    print('=' * 80)
    print(f'表: {table_name}')
    print('=' * 80)
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print('列结构:')
    for col in columns:
        print(f'  {col[1]} ({col[2]}) {"PK" if col[5] else ""}')
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    print(f'\n数据 ({len(rows)} 条):')
    if rows:
        col_names = [col[1] for col in columns]
        for row in rows:
            print('  ' + ', '.join(f'{k}: {repr(v)}' for k, v in zip(col_names, row)))
    else:
        print('  (空表)')
    print()

conn.close()
print('=' * 80)
print('打印完成')
print('=' * 80)
