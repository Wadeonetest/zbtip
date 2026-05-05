# -*- coding: utf-8 -*-
"""
同步历史录制任务的路径
确保所有录制记录的路径指向正确的 recordings 文件夹
"""
import os
import re

def sync_recordings_paths():
    base_dir = r"d:\代码存档\zbtip"
    recordings_file = os.path.join(base_dir, "recordings.txt")
    recordings_dir = os.path.join(base_dir, "recordings")
    
    print("="*60)
    print("  同步历史录制任务路径")
    print("="*60)
    print()
    
    if not os.path.exists(recordings_file):
        print(f"错误: {recordings_file} 不存在")
        return
    
    # 读取现有记录
    with open(recordings_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"读取到 {len(lines)} 条历史记录")
    print()
    
    # 首先扫描 recordings 目录下的所有会话文件夹，建立文件名到路径的映射
    filename_map = {}
    for session_name in os.listdir(recordings_dir):
        session_path = os.path.join(recordings_dir, session_name)
        if os.path.isdir(session_path):
            for filename in os.listdir(session_path):
                if filename.endswith('.avi') or filename.endswith('.mp4'):
                    full_path = os.path.join(session_path, filename)
                    filename_map[filename] = full_path
                    # 同时也存储带前缀的版本（以防文件名是 recording_xxx.avi）
                    if filename.startswith('recording_'):
                        filename_map[filename] = full_path
    
    print(f"扫描到 {len(filename_map)} 个录制文件")
    print()
    
    updated_lines = []
    changes_count = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            updated_lines.append(line)
            continue
        
        # 解析行：格式是 "时间 - 路径"
        match = re.match(r'^(.*?) - (.*)$', line)
        if not match:
            updated_lines.append(line)
            continue
        
        timestamp, original_path = match.groups()
        
        # 检查路径是否需要更新
        new_path = original_path
        
        # 如果路径不存在，尝试寻找匹配的文件
        if not os.path.exists(original_path):
            filename = os.path.basename(original_path)
            
            # 情况1: 直接根据文件名查找
            if filename in filename_map:
                new_path = filename_map[filename]
                if new_path != original_path:
                    print(f"更新: {filename}")
                    print(f"  旧: {original_path}")
                    print(f"  新: {new_path}")
                    changes_count += 1
            else:
                # 情况2: 尝试从文件名中提取时间戳
                # 支持两种格式: recording_1776875604.avi 或 recording_20260424_001027.avi
                file_match1 = re.match(r'recording_(\d+_\d+)\.', filename)
                file_match2 = re.match(r'recording_(\d{10,})\.', filename)
                
                if file_match1 or file_match2:
                    session_name = file_match1.group(1) if file_match1 else file_match2.group(1)
                    session_dir = os.path.join(recordings_dir, session_name)
                    if os.path.exists(session_dir):
                        # 在该会话文件夹中查找文件
                        for f in os.listdir(session_dir):
                            if f.startswith('recording_') and (f.endswith('.avi') or f.endswith('.mp4')):
                                # 找到第一个匹配的文件
                                new_path = os.path.join(session_dir, f)
                                if new_path != original_path:
                                    print(f"更新: {filename} -> {f}")
                                    print(f"  旧: {original_path}")
                                    print(f"  新: {new_path}")
                                    changes_count += 1
                                break
        
        # 保存更新后的行
        updated_lines.append(f"{timestamp} - {new_path}")
    
    print()
    if changes_count > 0:
        # 备份原文件
        backup_file = recordings_file + '.backup'
        import shutil
        shutil.copy2(recordings_file, backup_file)
        print(f"已备份原文件到: {backup_file}")
        
        # 写入更新后的内容
        with open(recordings_file, 'w', encoding='utf-8') as f:
            for line in updated_lines:
                f.write(line + '\n')
        
        print(f"成功更新 {changes_count} 条记录!")
    else:
        print("所有路径都是最新的，无需更新。")
    
    print()
    print("="*60)
    print("  验证路径是否存在")
    print("="*60)
    
    # 验证更新后的路径
    valid_count = 0
    invalid_count = 0
    
    with open(recordings_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            match = re.match(r'^(.*?) - (.*)$', line)
            if match:
                _, path = match.groups()
                if os.path.exists(path):
                    valid_count += 1
                else:
                    invalid_count += 1
                    print(f"不存在: {path}")
    
    print()
    print(f"有效路径: {valid_count}")
    print(f"无效路径: {invalid_count}")
    print("="*60)

if __name__ == "__main__":
    sync_recordings_paths()

