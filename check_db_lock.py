# -*- coding: utf-8 -*-
import os
import sqlite3

DB_PATH = "screen_recorder.db"

def check_and_fix_db_lock():
    """检查并修复数据库锁定问题"""
    # 尝试获取数据库锁
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        print("✓ 数据库正常，没有锁定")
        return True
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("✗ 数据库被锁定")
            return False
        else:
            print(f"✗ 数据库错误: {e}")
            return False

def main():
    print("="*50)
    print("数据库锁定检测工具")
    print("="*50)
    
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}")
        return
    
    # 检查锁定状态
    is_ok = check_and_fix_db_lock()
    
    if not is_ok:
        print("\n尝试释放锁定...")
        # 尝试强制释放
        try:
            # 创建一个新连接尝试获取锁
            conn = sqlite3.connect(DB_PATH, timeout=15)
            conn.execute("PRAGMA journal_mode=DELETE;")
            conn.commit()
            conn.close()
            print("✓ 已尝试释放锁定")
        except Exception as e:
            print(f"✗ 释放失败: {e}")
        
        # 再次检查
        print("\n再次检查...")
        if check_and_fix_db_lock():
            print("✓ 数据库已恢复正常")
        else:
            print("✗ 数据库仍然锁定，请关闭其他正在使用该数据库的程序")

if __name__ == "__main__":
    main()