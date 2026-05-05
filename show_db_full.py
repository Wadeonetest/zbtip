# -*- coding: utf-8 -*-
import sqlite3
import textwrap

DB_PATH = "screen_recorder.db"

def print_divider(length=80, char='='):
    print(char * length)

def print_title(text, char='='):
    print()
    print_divider()
    print(f"  {text}")
    print_divider()

def format_value(value, max_len=50):
    if value is None:
        return "NULL"
    s = str(value)
    if len(s) > max_len:
        return s[:max_len-3] + "..."
    return s

def print_table_schema(cursor, table_name):
    print_title(f"【{table_name}】表结构")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    if not columns:
        print("表不存在")
        return
    
    print(f"{'序号':<6} {'列名':<20} {'类型':<15} {'非空':<8} {'默认值':<15} {'主键':<8}")
    print("-" * 82)
    for col in columns:
        cid, name, ctype, notnull, dflt_value, pk = col
        print(f"{cid:<6} {name:<20} {ctype:<15} {str(notnull):<8} {str(dflt_value):<15} {str(pk):<8}")

def print_table_data(cursor, table_name):
    print_title(f"【{table_name}】数据")
    
    # 获取列名
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    if not columns:
        print("表不存在")
        return
    
    col_names = [col[1] for col in columns]
    col_count = len(col_names)
    
    # 获取数据
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        print("无数据")
        return
    
    print(f"共 {len(rows)} 条记录\n")
    
    for i, row in enumerate(rows, 1):
        print(f"  ┌────────────────── 记录 #{i} ──────────────────")
        for j in range(col_count):
            val = format_value(row[j])
            # 对长文本进行换行
            if len(val) > 40:
                wrapped = textwrap.wrap(val, width=50)
                print(f"  │ {col_names[j]:<18} : {wrapped[0]}")
                for line in wrapped[1:]:
                    print(f"  │ {' ':18}   {line}")
            else:
                print(f"  │ {col_names[j]:<18} : {val}")
        print(f"  └────────────────────────────────────────────────")
        print()

def main():
    if not __import__('os').path.exists(DB_PATH):
        print(f"错误: 数据库文件不存在: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print_divider(85)
    print(f"{' ' * 10}数据库完整结构和数据")
    print(f"{' ' * 10}文件: {DB_PATH}")
    print_divider(85)
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f"\n共有 {len(tables)} 个表: {', '.join(t[0] for t in tables)}")
    
    for (table_name,) in tables:
        print_table_schema(cursor, table_name)
        print_table_data(cursor, table_name)
    
    print_title("查询完成")
    conn.close()

if __name__ == "__main__":
    main()