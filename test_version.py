# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('screen_recorder.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print('=' * 50)
print('测试1：数据库 version_history 表数据')
print('=' * 50)

cursor.execute('SELECT * FROM version_history')
rows = cursor.fetchall()
for row in rows:
    print(f'版本: {row["version"]}')
    print(f'发布日期: {row["release_date"]}')
    print(f'是否最新: {row["is_latest"]}')
    print(f'更新链接: {row["update_url"]}')
    print(f'更新日志: {row["changelog"]}')
    print(f'文件哈希: {row["file_hash"]}')
    print('-' * 30)

print()
print('=' * 50)
print('测试2：版本比较逻辑')
print('=' * 50)

def compare_versions(v1, v2):
    v1_parts = [int(p) for p in v1.lstrip('v').split('.')]
    v2_parts = [int(p) for p in v2.lstrip('v').split('.')]
    for i in range(max(len(v1_parts), len(v2_parts))):
        p1 = v1_parts[i] if i < len(v1_parts) else 0
        p2 = v2_parts[i] if i < len(v2_parts) else 0
        if p1 < p2:
            return -1
        elif p1 > p2:
            return 1
    return 0

CURRENT_VERSION = 'v1.0.0'
latest_version = 'v1.0.0'

result = compare_versions(CURRENT_VERSION, latest_version)
print(f'当前版本: {CURRENT_VERSION}')
print(f'最新版本: {latest_version}')
print(f'比较结果: {result} (0表示相等)')

print()
print('=' * 50)
print('测试3：模拟升级场景')
print('=' * 50)

# 场景1：当前版本低于最新版本
CURRENT_VERSION = 'v1.0.0'
latest_version = 'v1.1.0'
result = compare_versions(CURRENT_VERSION, latest_version)
print(f'场景1: 当前={CURRENT_VERSION}, 最新={latest_version}')
print(f'结果: {result} -> 发现新版本，应弹出更新提示')

# 场景2：当前版本等于最新版本
CURRENT_VERSION = 'v1.0.0'
latest_version = 'v1.0.0'
result = compare_versions(CURRENT_VERSION, latest_version)
print(f'场景2: 当前={CURRENT_VERSION}, 最新={latest_version}')
print(f'结果: {result} -> 已是最新版本')

conn.close()
print()
print('=' * 50)
print('测试完成')
print('=' * 50)