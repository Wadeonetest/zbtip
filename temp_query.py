import sqlite3
conn = sqlite3.connect(r'd:\代码存档\zbtip\screen_recorder.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print('=' * 70)
print('version_history 表 - 版本历史')
print('=' * 70)

cursor.execute('SELECT * FROM version_history')
for row in cursor.fetchall():
    print(f'id: {row["id"]}')
    print(f'version: {row["version"]}')
    print(f'release_date: {row["release_date"]}')
    print(f'is_latest: {row["is_latest"]}')
    print(f'update_url: {row["update_url"]}')
    print(f'changelog: {row["changelog"]}')
    print(f'file_hash: {row["file_hash"]}')
    print(f'force_update: {row["force_update"]}')
    print('-' * 70)

conn.close()
