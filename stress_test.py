# -*- coding: utf-8 -*-
"""
压力测试脚本：模拟频繁点击标记进度按钮
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import sys
import json
import shutil

# 添加父目录到路径，以便导入screen_recorder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class StressTestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("标记进度压力测试")
        self.root.geometry("400x300")

        # 测试变量
        self.mark_count = 0
        self.markers = []
        self.current_session_dir = os.path.join(os.getcwd(), "recordings", "stress_test")
        self.is_running = False

        # 创建测试按钮
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        self.start_btn = ttk.Button(btn_frame, text="开始压力测试 (100次快速标记)", command=self.start_stress_test)
        self.start_btn.pack(pady=10)

        self.stop_btn = ttk.Button(btn_frame, text="停止测试", command=self.stop_test, state=tk.DISABLED)
        self.stop_btn.pack(pady=10)

        # 状态显示
        self.status_label = tk.Label(self.root, text="等待开始...", font=('Arial', 12))
        self.status_label.pack(pady=20)

        # 计数显示
        self.count_label = tk.Label(self.root, text="标记次数: 0", font=('Arial', 14))
        self.count_label.pack(pady=10)

    def save_markers_to_file(self):
        """保存标记信息到JSON文件"""
        if not self.current_session_dir or not self.markers:
            return

        os.makedirs(self.current_session_dir, exist_ok=True)
        markers_file = os.path.join(self.current_session_dir, "markers.json")
        try:
            with open(markers_file, 'w', encoding='utf-8') as f:
                json.dump(self.markers, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存标记失败: {e}")

    def mark_progress(self):
        """模拟标记进度"""
        marker_time = time.time() - self.start_time
        marker = {
            "id": self.mark_count + 1,
            "name": str(self.mark_count + 1),
            "time": marker_time,
            "note": f"测试标记 {self.mark_count + 1}"
        }
        self.markers.append(marker)
        self.mark_count += 1
        self.count_label.config(text=f"标记次数: {self.mark_count}")

        # 保存到文件
        self.save_markers_to_file()

    def start_stress_test(self):
        """开始压力测试"""
        self.is_running = True
        self.mark_count = 0
        self.markers = []
        self.start_time = time.time()

        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="测试进行中...")

        # 在新线程中运行测试
        test_thread = threading.Thread(target=self.run_stress_test)
        test_thread.daemon = True
        test_thread.start()

    def run_stress_test(self):
        """执行压力测试"""
        target_count = 100
        interval = 0.05  # 50ms间隔 = 每秒20次

        for i in range(target_count):
            if not self.is_running:
                break

            # 在主线程中调用（因为Tkinter不是线程安全的）
            self.root.after(0, self.mark_progress)

            # 等待指定间隔
            time.sleep(interval)

        # 测试完成
        self.root.after(0, self.test_complete)

    def test_complete(self):
        """测试完成"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text=f"测试完成! 共标记 {self.mark_count} 次")

        # 验证文件
        markers_file = os.path.join(self.current_session_dir, "markers.json")
        if os.path.exists(markers_file):
            with open(markers_file, 'r', encoding='utf-8') as f:
                saved_markers = json.load(f)
            self.status_label.config(text=f"测试完成! 标记:{self.mark_count} 保存:{len(saved_markers)}")

        print(f"压力测试完成: 标记 {self.mark_count} 次")

    def stop_test(self):
        """停止测试"""
        self.is_running = False
        self.status_label.config(text="测试已停止")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = StressTestApp()
    app.run()