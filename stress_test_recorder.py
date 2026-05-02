# -*- coding: utf-8 -*-
"""
压力测试脚本：测试真实的 screen_recorder.py 频繁标记进度功能
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import sys

# 导入真实的 ScreenRecorder 类
from screen_recorder import ScreenRecorder

class StressTestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("录屏工具标记压力测试")
        self.root.geometry("600x500")

        # 隐藏主窗口
        self.root.withdraw()

        # 创建真实的 ScreenRecorder
        self.recorder = ScreenRecorder(self.root)

        # 测试状态
        self.is_running = False
        self.test_thread = None
        self.mark_count = 0

        # 创建测试窗口
        self.create_test_window()

    def create_test_window(self):
        """创建测试窗口"""
        test_window = tk.Toplevel(self.root)
        test_window.title("标记进度压力测试")
        test_window.geometry("500x450")

        title = tk.Label(test_window, text="录屏工具 - 标记进度压力测试", font=('Arial', 16, 'bold'))
        title.pack(pady=15)

        # 提示
        tk.Label(test_window, text="⚠️ 请先开始录屏，然后进行标记压力测试", font=('Arial', 10), fg="orange").pack(pady=5)

        # 状态显示
        self.status_label = tk.Label(test_window, text="等待开始录屏...", font=('Arial', 12))
        self.status_label.pack(pady=10)

        # 配置区域
        config_frame = tk.LabelFrame(test_window, text="测试配置", padx=10, pady=10)
        config_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(config_frame, text="标记次数:").grid(row=0, column=0, sticky=tk.W)
        self.mark_count_var = tk.IntVar(value=100)
        tk.Entry(config_frame, textvariable=self.mark_count_var, width=10).grid(row=0, column=1, padx=5)

        tk.Label(config_frame, text="间隔(ms):").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.interval_var = tk.IntVar(value=100)
        tk.Entry(config_frame, textvariable=self.interval_var, width=10).grid(row=0, column=3, padx=5)

        # 按钮区域
        btn_frame = tk.Frame(test_window)
        btn_frame.pack(pady=15)

        self.start_btn = ttk.Button(btn_frame, text="开始压力测试", command=self.start_test, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="停止测试", command=self.stop_test, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # 进度显示
        self.progress_label = tk.Label(test_window, text="进度: 0 / 0", font=('Arial', 12))
        self.progress_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(test_window, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)

        # 日志显示
        log_frame = tk.LabelFrame(test_window, text="测试日志", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.log_text = tk.Text(log_frame, height=12, width=55, bg="#1a1a1a", fg="#00ff00", font=('Courier', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 绑定关闭事件
        test_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        test_window.focus()

    def log(self, message):
        """添加日志"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def update_status(self, message):
        """更新状态"""
        self.status_label.config(text=message)
        self.log(f"[状态] {message}")

    def start_test(self):
        """开始压力测试"""
        if not self.recorder.recording and not self.recorder.video_file:
            messagebox.showwarning("警告", "请先开始录屏或加载视频文件")
            return

        self.is_running = True
        self.mark_count = 0
        self.log("=" * 50)
        self.log("开始压力测试")
        self.log(f"配置: {self.mark_count_var.get()}次标记, 间隔{self.interval_var.get()}ms")

        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar['maximum'] = self.mark_count_var.get()
        self.progress_bar['value'] = 0

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

        self.root.after(0, lambda: self.update_status("测试进行中..."))

        for i in range(mark_count):
            if not self.is_running:
                break

            # 调用真实的 mark_progress
            try:
                self.recorder.mark_progress()
                self.mark_count += 1
                self.root.after(0, lambda n=i: self.update_progress_value(n + 1))
                self.root.after(0, lambda: self.progress_label.config(text=f"进度: {self.mark_count} / {mark_count}"))
            except Exception as e:
                self.root.after(0, lambda msg=f"错误: {e}": self.log(f"[错误] {msg}"))

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

    def test_complete(self):
        """测试完成"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

        result_msg = f"测试完成! 共标记 {self.mark_count} 次"
        self.update_status(result_msg)
        self.log("=" * 50)
        self.log(result_msg)

        # 检查标记数量
        saved_markers_file = None
        if self.recorder.current_session_dir:
            saved_markers_file = os.path.join(self.recorder.current_session_dir, "markers.json")

        if saved_markers_file and os.path.exists(saved_markers_file):
            import json
            with open(saved_markers_file, 'r', encoding='utf-8') as f:
                saved_markers = json.load(f)
            self.log(f"保存的标记数量: {len(saved_markers)}")
            self.log(f"文件位置: {saved_markers_file}")

            if len(saved_markers) == self.mark_count:
                self.log("✅ 测试通过! 标记数量匹配")
            else:
                self.log(f"❌ 测试失败! 标记数量不匹配: 预期{self.mark_count}, 实际{len(saved_markers)}")
        else:
            self.log("⚠️ 未找到标记保存文件")

    def stop_test(self):
        """停止测试"""
        self.is_running = False
        if self.test_thread:
            self.test_thread.join(timeout=1)
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("测试已手动停止")
        self.log("[停止] 测试已手动停止")

    def enable_start_button(self):
        """启用开始按钮"""
        self.start_btn.config(state=tk.NORMAL)
        self.update_status("就绪 - 可以开始压力测试")

    def on_closing(self):
        """关闭窗口"""
        self.is_running = False
        if self.test_thread:
            self.test_thread.join(timeout=1)
        self.root.quit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # 先启动录屏工具（会显示主窗口）
    app = StressTestApp()

    # 显示主窗口
    app.root.deiconify()

    # 5秒后启用测试按钮（模拟用户开始录屏）
    def enable_after_delay():
        app.root.after(2000, app.enable_start_button)

    enable_after_delay()

    app.run()