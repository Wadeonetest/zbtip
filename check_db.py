# -*- coding: utf-8 -*-
import os
import sqlite3

DB_PATH = "screen_recorder.db"

def check_db():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        print("Database OK")
        return True
    except sqlite3.OperationalError as e:
        print("Database Error:", str(e))
        return False

if __name__ == "__main__":
    check_db()