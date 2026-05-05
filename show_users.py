# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = "screen_recorder.db"

def print_table(cursor, table_name):
    print(f"\n{'='*80}")
    print(f"【{table_name}】")
    print('='*80)

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    if not columns:
        print("表不存在或为空")
        return

    col_names = [col[1] for col in columns]
    print(f"列名: {', '.join(col_names)}")
    print('-'*80)

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if not rows:
        print("无数据")
        return

    for i, row in enumerate(rows, 1):
        print(f"[{i}]", " | ".join(str(val) for val in row))

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print_table(cursor, "users")

    conn.close()

if __name__ == "__main__":
    main()