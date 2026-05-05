# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = "screen_recorder.db"

def print_table_data(cursor, table_name):
    print(f"\n{'='*80}")
    print(f"【{table_name}】")
    print('='*80)
    
    # 获取表结构
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    if not columns:
        print("表不存在或为空")
        return
    
    col_names = [col[1] for col in columns]
    print(f"列名: {', '.join(col_names)}")
    print('-'*80)
    
    # 获取数据
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        print("无数据")
        return
    
    for i, row in enumerate(rows, 1):
        print(f"[{i}]", " | ".join(str(val) for val in row))

def main():
    if not __import__('os').path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"数据库: {DB_PATH}")
    print(f"表数量: {len(tables)}")
    
    for (table_name,) in tables:
        print_table_data(cursor, table_name)
    
    print(f"\n{'='*80}")
    print("查询完成")
    print('='*80)
    
    conn.close()

if __name__ == "__main__":
    main()