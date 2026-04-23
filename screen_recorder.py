# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import cv2
import numpy as np
import threading
import time
import os
import sys

class ScreenRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("屏幕录制工具")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        self.recording = False
        self.paused = False
        self.recorder = None
        self.video_file = None
        self.markers = []
        self.marker_count = 0
        self.clips = []
        self.clip_start = None
        self.video_duration = 0
        self.current_time = 0
        self.update_thread = None
        self.stop_update = False
        self.recorded_frames = 0
        self.x = 0
        self.y = 0
        self.width = 1080
        self.height = 608
        self.recording_start_time = 0
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.video_capture = None
        self.video_playing = False
        self.video_thread = None
        self.stop_video = False
        self.video_paused = False
        self.recordings_file = "recordings.txt"
        self.progress_knob_id = None
        self.progress_bar_dragging = False
        
        # 截取视频相关变量
        self.clip_mode = False
        self.clip_start = 0
        self.clip_end = 0
        self.clip_start_id = None
        self.clip_end_id = None
        self.clip_area_id = None
        self.dragging_clip_start = False
        self.dragging_clip_end = False
        
        self.create_ui()
    
    def create_ui(self):
        self.control_frame = ttk.Frame(self.root, padding=10)
        self.control_frame.pack(fill=tk.X, side=tk.TOP)
        ttk.Label(self.control_frame, text="屏幕录制工具", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        self.button_frame = ttk.Frame(self.control_frame)
        self.button_frame.pack(side=tk.RIGHT)
        self.start_btn = ttk.Button(self.button_frame, text="开始录屏", command=self.start_recording)
        self.start_btn = ttk.Button(self.button_frame, text="开始录屏", command=self.start_recording)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.pause_btn = ttk.Button(self.button_frame, text="暂停录屏", command=self.pause_recording, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = ttk.Button(self.button_frame, text="结束录屏", command=self.stop_recording, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.mark_btn = ttk.Button(self.button_frame, text="标记进度", command=self.mark_progress, state=tk.DISABLED)
        self.mark_btn.pack(side=tk.LEFT, padx=5)
        
        self.clip_btn = ttk.Button(self.button_frame, text="截取视频", command=self.start_clip, state=tk.DISABLED)
        self.clip_btn.pack(side=tk.LEFT, padx=5)
        
        self.finish_clip_btn = ttk.Button(self.button_frame, text="完成截取", command=self.finish_clip, state=tk.DISABLED)
        self.finish_clip_btn.pack(side=tk.LEFT, padx=5)
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.area_frame = ttk.LabelFrame(self.left_frame, text="录屏区域设置", padding=10)
        self.area_frame.pack(fill=tk.X, padx=5, pady=5)
        area_grid = ttk.Frame(self.area_frame)
        area_grid.pack(fill=tk.X)
        ttk.Label(area_grid, text="X坐标:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.x_entry = ttk.Entry(area_grid, width=10)
        self.x_entry.insert(0, "0")
        self.x_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(area_grid, text="Y坐标:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.y_entry = ttk.Entry(area_grid, width=10)
        self.y_entry.insert(0, "0")
        self.y_entry.grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(area_grid, text="宽度:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.width_entry = ttk.Entry(area_grid, width=10)
        self.width_entry.insert(0, "1080")
        self.width_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(area_grid, text="高度:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.height_entry = ttk.Entry(area_grid, width=10)
        self.height_entry.insert(0, "608")
        self.height_entry.grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(area_grid, text="拖拽选择区域", command=self.start_drag_selection).grid(row=2, column=0, columnspan=4, pady=10)
        self.video_frame = ttk.LabelFrame(self.left_frame, text="视频预览", padding=10)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas = tk.Canvas(self.video_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        video_controls = ttk.Frame(self.video_frame, padding=5)
        video_controls.pack(fill=tk.X, pady=5)
        self.play_btn = ttk.Button(video_controls, text="播放", command=self.play_video, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        self.pause_video_btn = ttk.Button(video_controls, text="暂停", command=self.pause_video, state=tk.DISABLED)
        self.pause_video_btn.pack(side=tk.LEFT, padx=5)
        self.progress_frame = ttk.Frame(self.left_frame, padding=10)
        self.progress_frame.pack(fill=tk.X, padx=5, pady=5)
        self.progress_canvas = tk.Canvas(self.progress_frame, height=40, bg="#333", cursor="hand1")
        self.progress_canvas.pack(fill=tk.X, padx=5)
        self.progress_canvas.bind('<Button-1>', self.on_progress_click)
        self.progress_canvas.bind('<B1-Motion>', self.on_progress_drag)
        self.progress_canvas.bind('<ButtonRelease-1>', self.on_progress_release)
        self.time_label = ttk.Label(self.progress_frame, text="00:00 / 00:00")
        self.time_label.pack(side=tk.RIGHT, padx=5)
        self.right_frame = ttk.LabelFrame(self.main_frame, text="视频片段", padding=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        self.clip_listbox = tk.Listbox(self.right_frame, height=20)
        self.clip_listbox.pack(fill=tk.BOTH, expand=True)
        clip_buttons = ttk.Frame(self.right_frame)
        clip_buttons.pack(fill=tk.X, pady=10)
        ttk.Button(clip_buttons, text="播放选中片段", command=self.play_selected_clip).pack(side=tk.LEFT, padx=5)
        ttk.Button(clip_buttons, text="删除选中片段", command=self.delete_selected_clip).pack(side=tk.LEFT, padx=5)
        self.notification = tk.Toplevel(self.root)
        self.notification.title("通知")
        self.notification.geometry("300x100")
        self.notification.transient(self.root)
        self.notification.withdraw()
        self.notification_label = ttk.Label(self.notification, text="")
        self.notification_label.pack(pady=10)
        notification_buttons = ttk.Frame(self.notification)
        notification_buttons.pack(pady=10)
        ttk.Button(notification_buttons, text="编辑", command=self.open_marker_edit).pack(side=tk.LEFT, padx=5)
        ttk.Button(notification_buttons, text="确定", command=self.notification.withdraw).pack(side=tk.LEFT, padx=5)
        self.marker_edit_window = tk.Toplevel(self.root)
        self.marker_edit_window.title("编辑标记")
        self.marker_edit_window.geometry("400x200")
        self.marker_edit_window.transient(self.root)
        self.marker_edit_window.withdraw()
        ttk.Label(self.marker_edit_window, text="标记名称:").pack(pady=5)
        self.marker_name_var = tk.StringVar()
        ttk.Entry(self.marker_edit_window, textvariable=self.marker_name_var).pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(self.marker_edit_window, text="备注:").pack(pady=5)
        self.marker_note_var = tk.StringVar()
        ttk.Entry(self.marker_edit_window, textvariable=self.marker_note_var).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(self.marker_edit_window, text="保存", command=self.save_marker_edit).pack(pady=10)
        ttk.Button(self.marker_edit_window, text="取消", command=self.marker_edit_window.withdraw).pack(pady=5)
        self.current_marker_index = -1
    
    def start_drag_selection(self):
        self.root.iconify()
        time.sleep(0.5)
        box = pyautogui.selectROI("选择录屏区域", False)
        self.root.deiconify()
        if box:
            x, y, w, h = box
            self.x_entry.delete(0, tk.END)
            self.x_entry.insert(0, str(x))
            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, str(y))
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(w))
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(h))
    
    def start_recording(self):
        try:
            self.x = int(self.x_entry.get())
            self.y = int(self.y_entry.get())
            self.width = int(self.width_entry.get())
            self.height = int(self.height_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        if self.width <= 0 or self.height <= 0:
            messagebox.showerror("错误", "宽度和高度必须大于0")
            return
        self.recording = True
        self.paused = False
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.mark_btn.config(state=tk.NORMAL)
        self.clip_btn.config(state=tk.DISABLED)
        self.recording_start_time = time.time()
        self.current_time = 0
        self.recorded_frames = 0
        self.update_thread = threading.Thread(target=self.update_progress)
        self.stop_update = False
        self.update_thread.daemon = True
        self.update_thread.start()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.video_file = f"recording_{timestamp}.avi"
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.recorder = cv2.VideoWriter(self.video_file, fourcc, 20.0, (self.width, self.height))
        self.recorder_thread = threading.Thread(target=self.record_screen)
        self.recorder_thread.daemon = True
        self.recorder_thread.start()
        self.show_notification("开始录屏")
    
    def pause_recording(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="继续录屏")
            self.show_notification("暂停录屏")
        else:
            self.pause_btn.config(text="暂停录屏")
            self.recording_start_time += time.time() - self.pause_time
            self.show_notification("继续录屏")
    
    def stop_recording(self):
        self.recording = False
        if self.paused:
            self.recording_start_time += time.time() - self.pause_time
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.mark_btn.config(state=tk.NORMAL)
        self.clip_btn.config(state=tk.NORMAL)
        self.stop_update = True
        if self.update_thread:
            self.update_thread.join(timeout=1)
        if self.recorder:
            self.recorder.release()
        if self.video_file and os.path.exists(self.video_file):
            self.calculate_video_duration()
            self.play_btn.config(state=tk.NORMAL)
            self.show_notification("录屏完成")
            self.save_recording_path()
    
    def record_screen(self):
        while self.recording:
            if not self.paused:
                screenshot = pyautogui.screenshot(region=(self.x, self.y, self.width, self.height))
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                self.recorder.write(frame)
                self.recorded_frames += 1
                time.sleep(0.05)
            else:
                if not hasattr(self, 'pause_time'):
                    self.pause_time = time.time()
                time.sleep(0.1)
    
    def calculate_video_duration(self):
        if self.video_file:
            cap = cv2.VideoCapture(self.video_file)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                if fps > 0:
                    self.video_duration = frame_count / fps
                cap.release()
    
    def update_progress_bar(self):
        self.progress_canvas.delete('all')
        width = self.progress_canvas.winfo_width()
        height = self.progress_canvas.winfo_height()
        if width == 0 or height == 0:
            return
        if self.video_duration > 0:
            progress = self.current_time / self.video_duration
        else:
            progress = 0
        self.progress_canvas.create_rectangle(0, 0, width, height, fill="#333", outline="")
        progress_width = int(width * progress)
        self.progress_canvas.create_rectangle(0, 0, progress_width, height, fill="#4CAF50", outline="")
        knob_x = progress_width
        self.progress_canvas.create_oval(knob_x - 8, 0, knob_x + 8, height, fill="#fff", outline="#ddd", width=2)
        if self.recording or self.video_duration > 0:
            total_duration = self.video_duration if self.video_duration > 0 else self.current_time + 1
            if total_duration > 0:
                for marker in self.markers:
                    marker_time = marker["time"]
                    if marker_time <= total_duration:
                        marker_pos = (marker_time / total_duration) * width
                        marker_id = self.progress_canvas.create_oval(
                            marker_pos - 4, 0, marker_pos + 4, height,
                            fill="#ffeb3b", outline="#fbc02d", width=2
                        )
                        try:
                            self.progress_canvas.tag_bind(marker_id, "<Button-1>", lambda e, idx=self.markers.index(marker): self.jump_to_marker_and_play(idx))
                        except Exception:
                            pass
        
        # 绘制截取视频标识
        if self.clip_mode and self.video_duration > 0:
            total_duration = self.video_duration
            if total_duration > 0:
                # 计算开始和结束位置
                start_pos = (self.clip_start / total_duration) * width
                end_pos = (self.clip_end / total_duration) * width
                
                # 绘制截取区域
                if start_pos < end_pos:
                    self.clip_area_id = self.progress_canvas.create_rectangle(
                        start_pos, 0, end_pos, height,
                        fill="#33691e", outline="", stipple="gray50"
                    )
                
                # 绘制开始截取标识（剪映样式 - 更明显）
                # 绘制垂直线
                start_line_id = self.progress_canvas.create_line(
                    start_pos, 0, start_pos, height + 20,
                    fill="#4caf50", width=6
                )
                # 绘制三角形箭头（在时间轴上方）
                self.clip_start_id = self.progress_canvas.create_polygon(
                    start_pos - 20, 20, start_pos + 20, 20, start_pos, 0,
                    fill="#4caf50", outline="#388e3c", width=3
                )
                # 添加开始标记文本
                start_text_id = self.progress_canvas.create_text(
                    start_pos, -5,
                    text="开始",
                    fill="#4caf50",
                    font=("Arial", 14, "bold"),
                    anchor=tk.S
                )
                # 创建一个透明的大区域用于点击
                start_hitbox_id = self.progress_canvas.create_rectangle(
                    start_pos - 30, -15, start_pos + 30, height + 15,
                    fill="", outline=""
                )
                
                # 为开始标记的所有元素添加标签
                self.progress_canvas.addtag_withtag("clip_start", start_line_id)
                self.progress_canvas.addtag_withtag("clip_start", self.clip_start_id)
                self.progress_canvas.addtag_withtag("clip_start", start_text_id)
                self.progress_canvas.addtag_withtag("clip_start", start_hitbox_id)
                
                # 绘制结束截取标识（剪映样式 - 更明显）
                # 绘制垂直线
                end_line_id = self.progress_canvas.create_line(
                    end_pos, 0, end_pos, height + 20,
                    fill="#f44336", width=6
                )
                # 绘制三角形箭头（在时间轴上方）
                self.clip_end_id = self.progress_canvas.create_polygon(
                    end_pos - 20, 20, end_pos + 20, 20, end_pos, 0,
                    fill="#f44336", outline="#d32f2f", width=3
                )
                # 添加结束标记文本
                end_text_id = self.progress_canvas.create_text(
                    end_pos, -5,
                    text="结束",
                    fill="#f44336",
                    font=("Arial", 14, "bold"),
                    anchor=tk.S
                )
                # 创建一个透明的大区域用于点击
                end_hitbox_id = self.progress_canvas.create_rectangle(
                    end_pos - 30, -15, end_pos + 30, height + 15,
                    fill="", outline=""
                )
                
                # 为结束标记的所有元素添加标签
                self.progress_canvas.addtag_withtag("clip_end", end_line_id)
                self.progress_canvas.addtag_withtag("clip_end", self.clip_end_id)
                self.progress_canvas.addtag_withtag("clip_end", end_text_id)
                self.progress_canvas.addtag_withtag("clip_end", end_hitbox_id)
                
                # 设置层级置顶
                self.progress_canvas.tag_raise("clip_start")
                self.progress_canvas.tag_raise("clip_end")
                
                # 绑定拖动事件
                try:
                    # 为开始标记标签绑定事件
                    self.progress_canvas.tag_bind("clip_start", "<Button-1>", self.on_clip_start_click)
                    self.progress_canvas.tag_bind("clip_start", "<B1-Motion>", self.on_clip_start_drag)
                    self.progress_canvas.tag_bind("clip_start", "<ButtonRelease-1>", self.on_clip_release)
                    
                    # 为结束标记标签绑定事件
                    self.progress_canvas.tag_bind("clip_end", "<Button-1>", self.on_clip_end_click)
                    self.progress_canvas.tag_bind("clip_end", "<B1-Motion>", self.on_clip_end_drag)
                    self.progress_canvas.tag_bind("clip_end", "<ButtonRelease-1>", self.on_clip_release)
                    
                    # 为整个画布添加全局事件绑定，确保剪辑模式下的点击事件被正确处理
                    self.progress_canvas.bind("<Button-1>", self.on_canvas_click)
                    self.progress_canvas.bind("<B1-Motion>", self.on_canvas_drag)
                    self.progress_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
                    
                    print("剪辑标记事件绑定成功")
                except Exception as e:
                    print(f"事件绑定失败: {e}")
    
    def update_progress(self):
        while not self.stop_update:
            if self.recording:
                self.current_time = time.time() - self.recording_start_time
            elif self.video_duration > 0 and self.video_playing and not self.progress_bar_dragging:
                if not self.video_paused:
                    self.current_time += 0.1
                    if self.current_time >= self.video_duration:
                        self.current_time = self.video_duration
                        self.video_playing = False
                        self.play_btn.config(state=tk.NORMAL)
                        self.pause_video_btn.config(state=tk.DISABLED)
            if self.recording or self.video_duration > 0:
                if not self.progress_bar_dragging:
                    self.update_progress_bar()
                self.update_time_label()
            time.sleep(0.1)
    
    def update_time_label(self):
        current = self.format_time(self.current_time)
        if self.recording:
            total = "--:--"
        else:
            total = self.format_time(self.video_duration)
        self.time_label.config(text=f"{current} / {total}")
    
    def mark_progress(self):
        if self.recording or self.video_file:
            marker = {
                "id": self.marker_count + 1, "name": str(self.marker_count + 1), "time": self.current_time if self.video_file else time.time() - self.recording_start_time, "note": ""
            }
            self.markers.append(marker)
            self.marker_count += 1
            self.update_progress_bar()
            self.show_notification(f"已完成标记：{self.marker_count}")
    
    def start_clip(self):
        if self.video_file and self.video_duration > 0:
            self.clip_mode = True
            self.clip_start = 0
            self.clip_end = self.video_duration
            self.clip_btn.config(state=tk.DISABLED)
            self.finish_clip_btn.config(state=tk.NORMAL)
            self.update_progress_bar()
    
    def finish_clip(self):
        if self.clip_mode:
            if self.clip_start < self.clip_end:
                clip = {
                    "id": len(self.clips) + 1,
                    "start": self.clip_start,
                    "end": self.clip_end,
                    "duration": self.clip_end - self.clip_start
                }
                self.clips.append(clip)
                self.update_clips()
                self.show_notification(f"已完成截取，片段时长：{self.format_time(clip['duration'])}")
            self.clip_mode = False
            self.clip_btn.config(state=tk.NORMAL)
            self.finish_clip_btn.config(state=tk.DISABLED)
            self.update_progress_bar()
    
    def on_clip_start_click(self, event):
        print(f"开始标记点击事件触发，坐标: ({event.x}, {event.y})")
        self.dragging_clip_start = True
    
    def on_clip_start_drag(self, event):
        if self.dragging_clip_start and self.clip_mode and self.video_duration > 0:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                # 计算新的开始位置
                new_pos = max(0, min(event.x, width))
                new_time = (new_pos / width) * self.video_duration
                # 确保开始位置小于结束位置
                if new_time < self.clip_end:
                    self.clip_start = new_time
                    self.update_progress_bar()
    
    def on_clip_end_click(self, event):
        print(f"结束标记点击事件触发，坐标: ({event.x}, {event.y})")
        self.dragging_clip_end = True
    
    def on_clip_end_drag(self, event):
        if self.dragging_clip_end and self.clip_mode and self.video_duration > 0:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                # 计算新的结束位置
                new_pos = max(0, min(event.x, width))
                new_time = (new_pos / width) * self.video_duration
                # 确保结束位置大于开始位置
                if new_time > self.clip_start:
                    self.clip_end = new_time
                    self.update_progress_bar()
    
    def on_clip_release(self, event):
        print(f"释放事件触发，坐标: ({event.x}, {event.y})")
        self.dragging_clip_start = False
        self.dragging_clip_end = False
    
    def on_canvas_click(self, event):
        if self.clip_mode and self.video_duration > 0:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                # 计算点击位置对应的时间
                click_time = (event.x / width) * self.video_duration
                
                # 检查点击位置是否靠近开始标记
                start_pos = (self.clip_start / self.video_duration) * width
                end_pos = (self.clip_end / self.video_duration) * width
                
                # 定义点击区域的阈值
                threshold = 30
                
                if abs(event.x - start_pos) <= threshold:
                    print(f"点击了开始标记附近，坐标: ({event.x}, {event.y})")
                    self.dragging_clip_start = True
                elif abs(event.x - end_pos) <= threshold:
                    print(f"点击了结束标记附近，坐标: ({event.x}, {event.y})")
                    self.dragging_clip_end = True
    
    def on_canvas_drag(self, event):
        if self.clip_mode and self.video_duration > 0:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                # 计算拖动位置对应的时间
                drag_time = (event.x / width) * self.video_duration
                
                if self.dragging_clip_start and drag_time < self.clip_end:
                    self.clip_start = drag_time
                    self.update_progress_bar()
                elif self.dragging_clip_end and drag_time > self.clip_start:
                    self.clip_end = drag_time
                    self.update_progress_bar()
    
    def on_canvas_release(self, event):
        if self.clip_mode:
            self.dragging_clip_start = False
            self.dragging_clip_end = False
    
    def jump_to_marker(self, index):
        if 0 <= index < len(self.markers):
            self.current_time = self.markers[index]["time"]
            if self.video_duration > 0:
                self.update_progress_bar()
                self.update_time_label()
            self.current_marker_index = index
    
    def jump_to_marker_and_play(self, index):
        if self.video_playing:
            self.pause_video()
            if self.video_thread:
                self.video_thread.join(timeout=0.5)
        self.jump_to_marker(index)
        if self.video_file:
            self.play_video()
    
    def update_clips(self):
        self.clip_listbox.delete(0, tk.END)
        for clip in self.clips:
            start = self.format_time(clip["start"])
            end = self.format_time(clip["end"])
            duration = self.format_time(clip["duration"])
            self.clip_listbox.insert(tk.END, f"片段 {clip['id']}: {start} - {end} ({duration})")
    
    def play_selected_clip(self):
        selected = self.clip_listbox.curselection()
        if selected:
            clip = self.clips[selected[0]]
            self.play_clip(clip)
    
    def play_clip(self, clip):
        if self.video_file:
            self.stop_video = True
            if self.video_thread:
                self.video_thread.join(timeout=1)
            self.video_thread = threading.Thread(target=self.play_clip_thread, args=(clip,))
            self.video_thread.daemon = True
            self.video_thread.start()
    
    def play_clip_thread(self, clip):
        cap = cv2.VideoCapture(self.video_file)
        if not cap.isOpened():
            messagebox.showerror("错误", "无法打开视频文件")
            return
        start_frame = int(clip["start"] * cap.get(cv2.CAP_PROP_FPS))
        end_frame = int(clip["end"] * cap.get(cv2.CAP_PROP_FPS))
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        current_frame = start_frame
        clip_window = tk.Toplevel(self.root)
        clip_window.title(f"播放片段 {clip['id']}")
        clip_window.geometry(f"{self.width}x{self.height + 50}")
        clip_canvas = tk.Canvas(clip_window, bg="black")
        clip_canvas.pack(fill=tk.BOTH, expand=True)
        clip_window.protocol("WM_DELETE_WINDOW", lambda: self.on_clip_window_close(clip_window, cap))
        self.stop_video = False
        while current_frame <= end_frame and not self.stop_video:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            clip_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            clip_canvas.imgtk = imgtk
            clip_window.update()
            time.sleep(0.05)
            current_frame += 1
        cap.release()
        clip_window.destroy()
    
    def on_clip_window_close(self, window, cap):
        self.stop_video = True
        cap.release()
        window.destroy()
    
    def delete_selected_clip(self):
        selected = self.clip_listbox.curselection()
        if selected:
            self.clips.pop(selected[0])
            self.update_clips()
    
    def play_video(self):
        if self.video_file:
            self.stop_video = True
            if self.video_thread:
                self.video_thread.join(timeout=1)
            self.video_playing = True
            self.video_paused = False
            self.play_btn.config(state=tk.DISABLED)
            self.pause_video_btn.config(state=tk.NORMAL)
            self.video_thread = threading.Thread(target=self.play_video_thread)
            self.video_thread.daemon = True
            self.video_thread.start()
    
    def play_video_thread(self):
        self.video_capture = cv2.VideoCapture(self.video_file)
        if not self.video_capture.isOpened():
            messagebox.showerror("错误", "无法打开视频文件")
            self.video_playing = False
            self.play_btn.config(state=tk.NORMAL)
            self.pause_video_btn.config(state=tk.DISABLED)
            return
        self.stop_video = False
        while self.video_playing and not self.stop_video:
            if not self.video_paused:
                ret, frame = self.video_capture.read()
                if not ret:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.canvas.imgtk = imgtk
                self.root.update()
                time.sleep(0.05)
            else:
                time.sleep(0.1)
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        self.video_playing = False
        self.play_btn.config(state=tk.NORMAL)
        self.pause_video_btn.config(state=tk.DISABLED)
    
    def pause_video(self):
        self.video_paused = not self.video_paused
    
    def on_progress_click(self, event):
        if self.video_duration > 0:
            # 检查是否点击了剪辑标记区域
            if not self.clip_mode:
                self.progress_bar_dragging = True
                width = self.progress_canvas.winfo_width()
                if width > 0:
                    position = max(0, min(1, event.x / width))
                    self.current_time = position * self.video_duration
                    self.update_progress_bar()
                    self.update_time_label()
            else:
                # 在剪辑模式下，不处理进度条点击，让剪辑标记的点击事件优先处理
                pass
    
    def on_progress_drag(self, event):
        if self.progress_bar_dragging and self.video_duration > 0:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                position = max(0, min(1, event.x / width))
                self.current_time = position * self.video_duration
                self.update_progress_bar()
                self.update_time_label()
    
    def on_progress_release(self, event):
        if self.progress_bar_dragging:
            self.progress_bar_dragging = False
            if self.video_playing and self.video_capture:
                self.video_capture.set(cv2.CAP_PROP_POS_MSEC, self.current_time * 1000)
    
    def show_notification(self, message):
        self.notification_label.config(text=message)
        self.notification.deiconify()
        self.notification.after(3000, self.notification.withdraw)
    
    def open_marker_edit(self):
        if self.current_marker_index >= 0 and self.current_marker_index < len(self.markers):
            marker = self.markers[self.current_marker_index]
            self.marker_name_var.set(marker["name"])
            self.marker_note_var.set(marker.get("note", ""))
            self.marker_edit_window.deiconify()
    
    def save_marker_edit(self):
        if self.current_marker_index >= 0 and self.current_marker_index < len(self.markers):
            self.markers[self.current_marker_index]["name"] = self.marker_name_var.get()
            self.markers[self.current_marker_index]["note"] = self.marker_note_var.get()
            self.marker_edit_window.withdraw()
            self.show_notification("标记已更新")
    
    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def save_recording_path(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(current_dir, self.recordings_file), 'a', encoding='utf-8') as f:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp} - {os.path.join(current_dir, self.video_file)}\n")
        except Exception as e:
            print(f"[ERROR] 保存录屏路径失败: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    from PIL import Image, ImageTk
    root = tk.Tk()
    app = ScreenRecorder(root)
    root.mainloop()
