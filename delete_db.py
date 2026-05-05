import os
db_path = "screen_recorder.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"已删除 {db_path}")
else:
    print(f"{db_path} 不存在")