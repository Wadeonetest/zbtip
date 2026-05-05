# -*- coding: utf-8 -*-
import os
import sqlite3

DB_PATH = "screen_recorder.db"

def fix_db_lock():
    """修复数据库锁定问题"""
    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        print("数据库文件不存在，将创建新数据库")
        return True
    
    # 尝试正常连接
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        print("数据库正常")
        return True
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("数据库被锁定，尝试修复...")
            
            # 尝试删除锁定文件
            lock_files = [
                DB_PATH + "-journal",
                DB_PATH.replace(".db", "-wal"),
                DB_PATH.replace(".db", "-shm")
            ]
            
            for lock_file in lock_files:
                if os.path.exists(lock_file):
                    try:
                        os.remove(lock_file)
                        print(f"已删除锁定文件: {lock_file}")
                    except Exception as ex:
                        print(f"删除失败: {ex}")
            
            # 再次尝试连接
            try:
                conn = sqlite3.connect(DB_PATH, timeout=5)
                conn.execute("PRAGMA integrity_check")
                conn.close()
                print("数据库锁定已修复")
                return True
            except Exception as ex:
                print(f"修复失败: {ex}")
                print("建议手动删除数据库文件后重新运行程序")
                return False
        else:
            print(f"数据库错误: {e}")
            return False

if __name__ == "__main__":
    fix_db_lock()