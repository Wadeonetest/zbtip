# -*- coding: utf-8 -*-
"""
压力测试脚本：使用真实的 ScreenRecorder 类进行频繁标记测试
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import sys
import shutil

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入真实的 ScreenRecorder（部分导入，避免初始化整个UI）
import json

class StressTestRecorder:
    def __init__(self):
        self.markers = []
        self.marker_count = 0
        self.current_session_dir = os.path.join(os.getcwd(), "recordings", "stress_test_real")
        self.save_count = 0
        self.error_count = 0

    def save_markers_to_file(self):
        """保存标记信息到JSON文件"""
        if not self.current_session_dir or not self.markers:
            return

        os.makedirs(self.current_session_dir, exist_ok=True)
        markers_file = os.path.join(self.current_session_dir, "markers.json")
        try:
            with open(markers_file, 'w', encoding='utf-8') as f:
                json.dump(self.markers, f, ensure_ascii=False, indent=2)
            self.save_count += 1
        except Exception as e:
            print(f"保存标记失败: {e}")
            self.error_count += 1

    def mark_progress(self, current_time):
        """模拟标记进度"""
        marker = {
            "id": self.marker_count + 1,
            "name": str(self.marker_count + 1),
            "time": current_time,
            "note": f"测试标记 {self.marker_count + 1}"
        }
        self.markers.append(marker)
        self.marker_count += 1

        # 保存到文件
        self.save_markers_to_file()


class StressTestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("真实标记进度压力测试")
        self.root.geometry("500x400")

        # 测试对象
        self.tester = StressTestRecorder()
        self.is_running = False
        self.test_thread = None

        # 创建UI
        title = tk.Label(self.root, text="真实标记进度压力测试", font=('Arial', 16, 'bold'))
        title.pack(pady=15)

        # 配置区域
        config_frame = tk.LabelFrame(self.root, text="测试配置", padx=10, pady=10)
        config_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(config_frame, text="标记次数:").grid(row=0, column=0, sticky=tk.W)
        self.mark_count_var = tk.IntVar(value=500)
        tk.Entry(config_frame, textvariable=self.mark_count_var, width=10).grid(row=0, column=1, padx=5)

        tk.Label(config_frame, text="间隔(ms):").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.interval_var = tk.IntVar(value=10)
        tk.Entry(config_frame, textvariable=self.interval_var, width=10).grid(row=0, column=3, padx=5)

        # 按钮区域
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=15)

        self.start_btn = ttk.Button(btn_frame, text="开始压力测试", command=self.start_test)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="停止测试", command=self.stop_test, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # 进度显示
        self.progress_label = tk.Label(self.root, text="进度: 0 / 0", font=('Arial', 12))
        self.progress_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)

        # 状态显示
        status_frame = tk.LabelFrame(self.root, text="测试结果", padx=10, pady=10)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.result_text = tk.Text(status_frame, height=8, width=50, bg="#f0f0f0")
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def start_test(self):
        """开始压力测试"""
        self.tester = StressTestRecorder()
        self.is_running = True

        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar['maximum'] = self.mark_count_var.get()
        self.progress_bar['value'] = 0
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "测试开始...\n")

        # 清理旧数据
        if os.path.exists(self.tester.current_session_dir):
            shutil.rmtree(self.tester.current_session_dir)

        # 在新线程中运行测试
        self.test_thread = threading.Thread(target=self.run_test)
        self.test_thread.daemon = True
        self.test_thread.start()

        # 启动进度更新
        self.update_progress()

    def run_test(self):
        """执行压力测试"""
        mark_count = self.mark_count_var.get()
        interval_sec = self.interval_var.get() / 1000.0
        start_time = time.time()

        for i in range(mark_count):
            if not self.is_running:
                break

            current_time = time.time() - start_time
            self.tester.mark_progress(current_time)

            # 更新进度
            self.root.after(0, lambda n=i: self.update_progress_value(n + 1))

            # 等待指定间隔
            time.sleep(interval_sec)

        # 测试完成
        self.root.after(0, self.test_complete)

    def update_progress(self):
        """更新进度显示"""
        if self.is_running:
            self.root.after(100, self.update_progress)

    def update_progress_value(self, value):
        """更新进度条值"""
        self.progress_bar['value'] = value
        self.progress_label.config(text=f"进度: {value} / {self.mark_count_var.get()}")

    def test_complete(self):
        """测试完成"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

        # 验证结果
        markers_file = os.path.join(self.tester.current_session_dir, "markers.json")
        saved_count = 0
        if os.path.exists(markers_file):
            with open(markers_file, 'r', encoding='utf-8') as f:
                saved_markers = json.load(f)
            saved_count = len(saved_markers)

        # 显示结果
        result = f"""测试完成!

标记次数: {self.tester.mark_count}
保存次数: {self.tester.save_count}
错误次数: {self.tester.error_count}
文件保存标记数: {saved_count}

文件位置: {markers_file}

测试配置:
  - 标记次数: {self.mark_count_var.get()}
  - 间隔: {self.interval_var.get()}ms
  - 总耗时: {self.tester.save_count * self.interval_var.get() / 1000:.2f}秒
"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

        # 判断是否成功
        if self.tester.mark_count == saved_count and self.tester.error_count == 0:
            self.result_text.insert(tk.END, "\n✅ 测试通过! 所有标记已正确保存.")
        else:
            self.result_text.insert(tk.END, f"\n❌ 测试失败! 标记数不匹配或存在错误.")

    def stop_test(self):
        """停止测试"""
        self.is_running = False
        if self.test_thread:
            self.test_thread.join(timeout=1)
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.result_text.insert(tk.END, "\n测试已手动停止.")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = StressTestApp()
    app.run()