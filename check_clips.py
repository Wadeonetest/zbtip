import os
import json

session_dir = r"d:\代码存档\zbtip\recordings\20260502_011027"
clip_dir = os.path.join(session_dir, "截取视频")

print(f"=== 检查片段文件夹结构 ===")
print(f"会话目录: {session_dir}")
print(f"截取视频文件夹: {clip_dir}")
print(f"文件夹存在: {os.path.exists(clip_dir)}")

if os.path.exists(clip_dir):
    items = os.listdir(clip_dir)
    print(f"\n截取视频文件夹中的内容 ({len(items)} 个):")
    for item in items:
        item_path = os.path.join(clip_dir, item)
        if os.path.isdir(item_path):
            print(f"\n  文件夹: {item}")
            files = os.listdir(item_path)
            for f in files:
                f_path = os.path.join(item_path, f)
                print(f"    - {f}")
                
                # 检查签名文件内容
                if f == "clip_info.json":
                    try:
                        with open(f_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            print(f"      内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
                    except Exception as e:
                        print(f"      读取失败: {e}")
        else:
            print(f"  文件: {item}")

print("\n=== 检查完成 ===")