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
        self.width = 1920
        self.height = 1080
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
        
        # 存储每个视频文件对应的标记列表
        self.video_markers = {}
        
        # 截取视频相关变量
        self.clip_mode = False
        self.clip_start = 0
        self.clip_end = 0
        self.clip_start_id = None
        self.clip_end_id = None
        self.clip_area_id = None
        self.dragging_clip_start = False
        self.dragging_clip_end = False
        
        # 缩略功能区相关属性
        self.mini_window = None
        self.mini_pause_btn = None
        self.mini_stop_btn = None
        self.mini_mark_btn = None
        self.mini_status_label = None

        self.create_ui()
    
    def create_ui(self):
        # 设置现代主题 - 剪映专业风格
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 主色调定义 - 剪映专业级深色主题
        self.bg_color = "#0d0d0d"           # 深黑色背景
        self.card_bg = "#1a1a1a"            # 卡片背景
        self.light_bg = "#252525"           # 浅色背景
        self.text_color = "#ffffff"         # 白色文字
        self.secondary_text = "#999999"     # 次要文字
        self.accent_color = "#ff6c37"       # 橙红色强调色（剪映主题色）
        self.accent_hover = "#ff8560"       # 悬停色
        self.success_color = "#4CAF50"      # 成功色
        self.danger_color = "#f44336"       # 危险色
        self.border_color = "#333333"       # 边框色
        self.input_bg = "#2d2d2d"           # 输入框背景
        
        # 配置主窗口
        self.root.configure(bg=self.bg_color)
        self.root.option_add('*Font', 'Arial 9')
        
        # 配置样式
        # 框架样式
        self.style.configure('Custom.TFrame', background=self.bg_color)
        self.style.configure('Card.TFrame', background=self.card_bg)
        self.style.configure('Light.TFrame', background=self.light_bg)
        
        # LabelFrame样式
        self.style.configure('Custom.TLabelframe', background=self.card_bg,
                           borderwidth=0, relief='flat')
        self.style.configure('Custom.TLabelframe.Label', background=self.card_bg,
                           foreground=self.secondary_text)
        
        # Label样式
        self.style.configure('Custom.TLabel', background=self.bg_color,
                          foreground=self.text_color)
        self.style.configure('Title.TLabel', background=self.card_bg,
                          foreground=self.text_color)
        self.style.configure('Small.TLabel', background=self.card_bg,
                          foreground=self.secondary_text)
        
        # 按钮基础样式
        self.style.configure('Custom.TButton',
                          background=self.light_bg,
                          foreground=self.text_color,
                          font=('Arial', 9, 'bold'),
                          padding=(16, 8),
                          borderwidth=0,
                          relief='flat',
                          focuscolor='none')
        self.style.map('Custom.TButton',
                    background=[('active', '#303030'), ('pressed', '#202020')],
                    foreground=[('active', self.text_color)])
        
        # 强调按钮样式
        self.style.configure('Accent.TButton',
                          background=self.accent_color,
                          foreground='#ffffff',
                          font=('Arial', 9, 'bold'),
                          padding=(16, 8),
                          borderwidth=0,
                          relief='flat',
                          focuscolor='none')
        self.style.map('Accent.TButton',
                    background=[('active', self.accent_hover), ('pressed', '#e55b2d')],
                    foreground=[('active', '#ffffff')])
        
        # 危险按钮样式
        self.style.configure('Danger.TButton',
                          background=self.danger_color,
                          foreground='#ffffff',
                          font=('Arial', 9, 'bold'),
                          padding=(16, 8),
                          borderwidth=0,
                          relief='flat',
                          focuscolor='none')
        self.style.map('Danger.TButton',
                    background=[('active', '#ff6060'), ('pressed', '#d32f2f')],
                    foreground=[('active', '#ffffff')])
        
        # 输入框样式
        self.style.configure('Custom.TEntry',
                          fieldbackground=self.input_bg,
                          foreground=self.text_color,
                          background=self.light_bg,
                          borderwidth=1,
                          relief='solid',
                          padding=4)
        self.style.map('Custom.TEntry',
                    fieldbackground=[('focus', '#303030')])
        
        # 控制栏 - 使用卡片式设计
        self.control_frame = tk.Frame(self.root, bg=self.card_bg, padx=20, pady=16)
        self.control_frame.pack(fill=tk.X, side=tk.TOP)
        
        tk.Label(self.control_frame, text="屏幕录制工具", 
                font=('Arial', 16, 'bold'),
                bg=self.card_bg, fg=self.text_color).pack(side=tk.LEFT)
        
        self.button_frame = tk.Frame(self.control_frame, bg=self.card_bg)
        self.button_frame.pack(side=tk.RIGHT)
        
        # 主按钮 - 使用grid布局固定位置
        self.start_btn = ttk.Button(self.button_frame, text="开始录屏", command=self.start_recording, 
                                  style='Accent.TButton')
        self.start_btn.grid(row=0, column=0, padx=6, pady=2)
        
        self.pause_btn = ttk.Button(self.button_frame, text="暂停录屏", command=self.pause_recording, 
                                  style='Custom.TButton')
        # 初始状态隐藏
        
        self.stop_btn = ttk.Button(self.button_frame, text="结束录屏", command=self.stop_recording, 
                                  style='Danger.TButton')
        # 初始状态隐藏
        
        self.mark_btn = ttk.Button(self.button_frame, text="标记进度", command=self.mark_progress, 
                                  style='Custom.TButton')
        # 初始状态隐藏
        
        self.clip_btn = ttk.Button(self.button_frame, text="截取视频", command=self.start_clip, 
                                  state=tk.DISABLED, style='Custom.TButton')
        self.clip_btn.grid(row=0, column=4, padx=6, pady=2)
        
        self.finish_clip_btn = ttk.Button(self.button_frame, text="完成截取", command=self.finish_clip, 
                                         state=tk.DISABLED, style='Accent.TButton')
        self.finish_clip_btn.grid(row=0, column=5, padx=6, pady=2)

        # 主框架
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧框架
        self.left_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 视频预览 - 卡片式设计
        self.video_frame = ttk.LabelFrame(self.left_frame, text="视频预览", padding=12, style='Custom.TLabelframe')
        self.video_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        # 视频画布 - 圆角边框效果
        self.canvas = tk.Canvas(self.video_frame, bg="#0a0a0a", 
                              highlightthickness=1, highlightbackground="#2a2a2a")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 视频控制栏
        video_controls = tk.Frame(self.video_frame, bg=self.card_bg)
        video_controls.pack(fill=tk.X, pady=(10, 0))
        
        self.play_btn = ttk.Button(video_controls, text="播放", command=self.play_video, 
                                  state=tk.DISABLED, style='Custom.TButton')
        self.play_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        self.pause_video_btn = ttk.Button(video_controls, text="暂停", command=self.pause_video, 
                                        state=tk.DISABLED, style='Custom.TButton')
        self.pause_video_btn.pack(side=tk.LEFT)
        
        # 进度条区域 - 卡片式设计
        self.progress_frame = ttk.LabelFrame(self.left_frame, text="进度", padding=12, style='Custom.TLabelframe')
        self.progress_frame.pack(fill=tk.X)
        
        # 进度画布
        self.progress_canvas = tk.Canvas(self.progress_frame, height=120, bg="#151515", 
                                      cursor="hand1", highlightthickness=1, 
                                      highlightbackground="#2a2a2a")
        self.progress_canvas.pack(fill=tk.X, pady=(8, 0))
        self.progress_canvas.bind('<Button-1>', self.on_progress_click)
        self.progress_canvas.bind('<B1-Motion>', self.on_progress_drag)
        self.progress_canvas.bind('<ButtonRelease-1>', self.on_progress_release)
        
        # 时间标签
        self.time_label = tk.Label(self.progress_frame, text="00:00 / 00:00", 
                                  font=('Arial', 9),
                                  bg=self.card_bg, fg=self.secondary_text)
        self.time_label.pack(side=tk.RIGHT, pady=(8, 0))
        # 右侧视频片段面板 - 卡片式设计
        self.right_frame = ttk.LabelFrame(self.main_frame, text="视频片段", padding=12, style='Custom.TLabelframe')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=0)
        self.right_frame.configure(width=300)
        
        # 片段列表
        self.clip_listbox = tk.Listbox(self.right_frame, 
                                     height=20, 
                                     bg="#151515", 
                                     fg=self.text_color, 
                                     highlightthickness=1, 
                                     highlightbackground="#2a2a2a",
                                     selectbackground=self.accent_color,
                                     selectforeground="white",
                                     font=('Arial', 9),
                                     bd=0, relief='flat',
                                     activestyle='none')
        self.clip_listbox.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        
        # 片段控制按钮
        clip_buttons = tk.Frame(self.right_frame, bg=self.card_bg)
        clip_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(clip_buttons, text="播放选中", command=self.play_selected_clip, 
                  style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(clip_buttons, text="删除片段", command=self.delete_selected_clip, 
                  style='Danger.TButton').pack(side=tk.LEFT)
        # 通知窗口
        self.notification = tk.Toplevel(self.root)
        self.notification.title("通知")
        self.notification.geometry("300x110")
        self.notification.transient(self.root)
        self.notification.withdraw()
        self.notification.configure(bg=self.card_bg)
        
        self.notification_label = tk.Label(self.notification, text="", 
                                         font=('Arial', 10),
                                         bg=self.card_bg, fg=self.text_color)
        self.notification_label.pack(pady=18)
        
        notification_buttons = tk.Frame(self.notification, bg=self.card_bg)
        notification_buttons.pack(pady=12)
        
        ttk.Button(notification_buttons, text="编辑", command=self.open_marker_edit, 
                  style='Custom.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(notification_buttons, text="确定", command=self.notification.withdraw, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=10)
        
        # 标记编辑窗口
        self.marker_edit_window = tk.Toplevel(self.root)
        self.marker_edit_window.title("编辑标记")
        self.marker_edit_window.geometry("400x220")
        self.marker_edit_window.transient(self.root)
        self.marker_edit_window.withdraw()
        self.marker_edit_window.configure(bg=self.card_bg)
        
        tk.Label(self.marker_edit_window, text="标记名称:", 
                font=('Arial', 10),
                bg=self.card_bg, fg=self.text_color).pack(pady=10)
        self.marker_name_var = tk.StringVar()
        ttk.Entry(self.marker_edit_window, textvariable=self.marker_name_var, 
                 style='Custom.TEntry').pack(fill=tk.X, padx=20, pady=6)
        
        tk.Label(self.marker_edit_window, text="备注:", 
                font=('Arial', 10),
                bg=self.card_bg, fg=self.text_color).pack(pady=10)
        self.marker_note_var = tk.StringVar()
        ttk.Entry(self.marker_edit_window, textvariable=self.marker_note_var, 
                 style='Custom.TEntry').pack(fill=tk.X, padx=20, pady=6)
        
        button_frame = tk.Frame(self.marker_edit_window, bg=self.card_bg)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="保存", command=self.save_marker_edit, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=12)
        ttk.Button(button_frame, text="取消", command=self.marker_edit_window.withdraw, 
                  style='Custom.TButton').pack(side=tk.LEFT, padx=12)
        
        self.current_marker_index = -1

    def start_recording(self):
        screen_width, screen_height = pyautogui.size()
        self.x = 0
        self.y = 0
        self.width = screen_width
        self.height = screen_height
        
        self.recording = True
        self.paused = False
        # 录制时：显示暂停、结束、标记按钮，隐藏开始按钮
        self.start_btn.grid_remove()
        self.pause_btn.grid(row=0, column=0, padx=6, pady=2)
        self.stop_btn.grid(row=0, column=1, padx=6, pady=2)
        self.mark_btn.grid(row=0, column=2, padx=6, pady=2)
        self.clip_btn.config(state=tk.DISABLED)
        
        # 设置视频文件路径
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.video_file = os.path.join(current_dir, f"recording_{timestamp}.avi")
        
        # 重置标记相关变量
        self.markers = []
        self.marker_count = 0
        
        self.recording_start_time = time.time()
        self.current_time = 0
        self.recorded_frames = 0
        self.update_thread = threading.Thread(target=self.update_progress)
        self.stop_update = False
        self.update_thread.daemon = True
        self.update_thread.start()
        self.recorder = cv2.VideoWriter(self.video_file, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (self.width, self.height))
        self.record_thread = threading.Thread(target=self.record_screen)
        self.record_thread.daemon = True
        self.record_thread.start()
        
        # 创建缩略功能区
        self.create_mini_control()
        
        # 最小化主窗口
        self.root.iconify()
        
        self.show_notification("开始录屏", is_weak=True)
    
    def pause_recording(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="继续录屏")
            # 更新缩略功能区的按钮文本
            if hasattr(self, 'mini_pause_btn') and self.mini_pause_btn:
                self.mini_pause_btn.config(text="继续录屏")
            # 更新状态标签
            if hasattr(self, 'mini_status_label') and self.mini_status_label:
                self.mini_status_label.config(text="已暂停", foreground='orange')
            self.show_notification("暂停录屏", is_weak=True)
        else:
            self.pause_btn.config(text="暂停录屏")
            # 更新缩略功能区的按钮文本
            if hasattr(self, 'mini_pause_btn') and self.mini_pause_btn:
                self.mini_pause_btn.config(text="暂停录屏")
            # 更新状态标签
            if hasattr(self, 'mini_status_label') and self.mini_status_label:
                self.mini_status_label.config(text="录屏中...", foreground='green')
            self.recording_start_time += time.time() - self.pause_time
            self.show_notification("继续录屏", is_weak=True)
    
    def stop_recording(self):
        self.recording = False
        if self.paused:
            self.recording_start_time += time.time() - self.pause_time
        # 未录制时：显示开始按钮，隐藏暂停、结束、标记按钮
        self.pause_btn.grid_remove()
        self.stop_btn.grid_remove()
        self.mark_btn.grid_remove()
        self.start_btn.grid(row=0, column=0, padx=6, pady=2)
        self.clip_btn.config(state=tk.NORMAL)
        self.stop_update = True
        if self.update_thread:
            self.update_thread.join(timeout=1)
        if self.recorder:
            self.recorder.release()
        
        # 等待录屏线程结束
        if hasattr(self, 'record_thread') and self.record_thread:
            self.record_thread.join(timeout=2)
        
        # 关闭缩略功能区
        self.close_mini_control()
        
        # 恢复主窗口
        self.root.deiconify()
        
        if self.video_file and os.path.exists(self.video_file):
            # 计算视频实际时长
            self.calculate_video_duration()
            
            # 调整标记时间，确保与视频实际时长匹配
            if self.video_duration > 0 and self.markers:
                # 录制时的总时长
                recorded_duration = time.time() - self.recording_start_time
                if recorded_duration > 0:
                    # 计算时间比例，调整标记时间
                    time_ratio = self.video_duration / recorded_duration
                    for marker in self.markers:
                        marker["time"] = marker["time"] * time_ratio
            
            # 保存当前视频的标记
            self.video_markers[self.video_file] = self.markers.copy()
            
            self.play_btn.config(state=tk.NORMAL)
            self.show_notification("录屏完成", is_weak=True)
            self.save_recording_path()
            # 显示视频第一帧
            self.show_first_frame()
    
    def show_first_frame(self):
        """显示视频的第一帧画面"""
        if not self.video_file or not os.path.exists(self.video_file):
            return
        
        # 加载当前视频的标记
        if self.video_file in self.video_markers:
            self.markers = self.video_markers[self.video_file].copy()
            self.marker_count = len(self.markers)
        else:
            self.markers = []
            self.marker_count = 0
        
        cap = cv2.VideoCapture(self.video_file)
        if not cap.isOpened():
            cap.release()
            return
        
        # 读取第一帧
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return
        
        # 转换颜色空间
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 获取画布尺寸并缩放
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 0 and canvas_height > 0:
            img = Image.fromarray(frame)
            img_width, img_height = img.size
            canvas_ratio = canvas_width / canvas_height
            img_ratio = img_width / img_height
            
            if canvas_ratio > img_ratio:
                new_height = canvas_height
                new_width = int(img_width * (canvas_height / img_height))
            else:
                new_width = canvas_width
                new_height = int(img_height * (canvas_width / img_width))
            
            img = img.resize((new_width, new_height), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # 居中显示
            x_offset = (canvas_width - new_width) // 2
            y_offset = (canvas_height - new_height) // 2
            self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=imgtk)
            self.canvas.imgtk = imgtk
        
        # 更新进度条，显示当前视频的标记
        self.update_progress_bar()
    
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
        
        # 添加留白区域
        padding = 20  # 左右留白的宽度
        usable_width = width - 2 * padding
        
        if self.video_duration > 0:
            progress = self.current_time / self.video_duration
        else:
            progress = 0
        
        # 绘制背景
        self.progress_canvas.create_rectangle(0, 0, width, height, fill="#333", outline="")
        
        # 绘制进度条（在画布下方，考虑留白）
        progress_bar_y = height - 30
        progress_bar_height = 20
        progress_width = int(usable_width * progress)
        self.progress_canvas.create_rectangle(padding, progress_bar_y, width - padding, progress_bar_y + progress_bar_height, fill="#444", outline="")
        self.progress_canvas.create_rectangle(padding, progress_bar_y, padding + progress_width, progress_bar_y + progress_bar_height, fill="#4CAF50", outline="")
        
        # 绘制黄色标记（在进度条上方）
        if self.recording or self.video_duration > 0:
            # 在录制模式下，使用 current_time 作为总时长
            # 在播放模式下，使用 video_duration 或所有标记的最大时间
            max_marker_time = 0
            if self.recording:
                total_duration = self.current_time if self.current_time > 0 else 1
            else:
                # 如果 video_duration 为0或小于任何标记的时间，使用标记的最大时间
                max_marker_time = max([m["time"] for m in self.markers]) if self.markers else 0
                if self.video_duration <= 0 or self.video_duration < max_marker_time:
                    total_duration = max_marker_time if max_marker_time > 0 else 1
                else:
                    total_duration = self.video_duration
            print(f"[调试] 绘制标记: 录制模式={self.recording}, video_duration={self.video_duration:.2f}, max_marker_time={max_marker_time:.2f}, total_duration={total_duration:.2f}, 标记数量={len(self.markers)}")
            if total_duration > 0:
                for marker in self.markers:
                    marker_time = marker["time"]
                    print(f"[调试] 标记时间: {marker_time:.2f}, 条件: {marker_time} <= {total_duration}")
                    if marker_time <= total_duration:
                        marker_pos = padding + (marker_time / total_duration) * usable_width
                        # 确保标记不会超出画布边界
                        marker_pos = max(padding + 4, min(width - padding - 4, marker_pos))
                        print(f"[调试] 绘制标记: 位置={marker_pos:.2f}, 时间={marker_time:.2f}, 画布宽度={width}")
                        marker_id = self.progress_canvas.create_oval(
                            marker_pos - 4, progress_bar_y - 10, marker_pos + 4, progress_bar_y,
                            fill="#ffeb3b", outline="#fbc02d", width=2
                        )
                        # 为标记添加标签
                        self.progress_canvas.addtag_withtag("yellow_marker", marker_id)
                        try:
                            idx = self.markers.index(marker)
                            print(f"[调试] 标记索引: {idx}")
                            self.progress_canvas.tag_bind(marker_id, "<Button-1>", lambda e, idx=idx: self.jump_to_marker_and_play(idx))
                        except Exception as ex:
                            print(f"[调试] 标记绑定失败: {ex}")
                            pass
        
        # 在非录制模式下，确保黄色标记在最上层（但在剪辑标记之下）
        if not self.recording and self.markers:
            self.progress_canvas.tag_raise("yellow_marker")
        
        # 绘制截取视频标识
        if self.clip_mode and self.video_duration > 0:
            total_duration = self.video_duration
            if total_duration > 0:
                # 计算开始和结束位置，考虑留白
                start_pos = padding + (self.clip_start / total_duration) * usable_width
                end_pos = padding + (self.clip_end / total_duration) * usable_width
                
                # 绘制截取区域
                if start_pos < end_pos:
                    self.clip_area_id = self.progress_canvas.create_rectangle(
                        start_pos, 0, end_pos, height,
                        fill="#33691e", outline="", stipple="gray50"
                    )
                
                # 绘制开始截取标识（长方形样式，在画布内）
                rect_width = 50
                rect_height = 120  # 长方形长度，确保在画布内显示
                # 计算开始标记的位置，确保在画布范围内
                start_rect_x1 = max(0, start_pos - rect_width // 2)
                start_rect_x2 = min(width, start_pos + rect_width // 2)
                # 绘制长方形（在画布上方，中心与进度条位置对齐）
                self.clip_start_id = self.progress_canvas.create_rectangle(
                    start_rect_x1, 10,
                    start_rect_x2, 10 + rect_height,
                    fill="#4caf50", outline="#388e3c", width=2
                )
                # 添加开始位置文本（竖向排列4个字，居中显示）
                start_text_id = self.progress_canvas.create_text(
                    start_pos, 10 + rect_height // 2,
                    text="开\n始\n位\n置",
                    fill="white",
                    font=("Arial", 10, "bold"),
                    anchor=tk.CENTER
                )
                # 创建一个透明的大区域用于点击，确保在画布范围内
                start_hitbox_x1 = max(0, start_pos - 30)
                start_hitbox_x2 = min(width, start_pos + 30)
                start_hitbox_id = self.progress_canvas.create_rectangle(
                    start_hitbox_x1, 5, start_hitbox_x2, 15 + rect_height,
                    fill="", outline=""
                )
                
                # 为开始标记的所有元素添加标签
                self.progress_canvas.addtag_withtag("clip_start", self.clip_start_id)
                self.progress_canvas.addtag_withtag("clip_start", start_text_id)
                self.progress_canvas.addtag_withtag("clip_start", start_hitbox_id)
                
                # 绘制结束截取标识（长方形样式，在画布内）
                # 计算结束标记的位置，确保在画布范围内
                end_rect_x1 = max(0, end_pos - rect_width // 2)
                end_rect_x2 = min(width, end_pos + rect_width // 2)
                # 绘制长方形（在画布上方，中心与进度条位置对齐）
                self.clip_end_id = self.progress_canvas.create_rectangle(
                    end_rect_x1, 10,
                    end_rect_x2, 10 + rect_height,
                    fill="#f44336", outline="#d32f2f", width=2
                )
                # 添加结束位置文本（竖向排列4个字，居中显示）
                end_text_id = self.progress_canvas.create_text(
                    end_pos, 10 + rect_height // 2,
                    text="结\n束\n位\n置",
                    fill="white",
                    font=("Arial", 10, "bold"),
                    anchor=tk.CENTER
                )
                # 创建一个透明的大区域用于点击，确保在画布范围内
                end_hitbox_x1 = max(0, end_pos - 30)
                end_hitbox_x2 = min(width, end_pos + 30)
                end_hitbox_id = self.progress_canvas.create_rectangle(
                    end_hitbox_x1, 5, end_hitbox_x2, 15 + rect_height,
                    fill="", outline=""
                )
                
                # 为结束标记的所有元素添加标签
                self.progress_canvas.addtag_withtag("clip_end", self.clip_end_id)
                self.progress_canvas.addtag_withtag("clip_end", end_text_id)
                self.progress_canvas.addtag_withtag("clip_end", end_hitbox_id)
                
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
                
                # 设置层级置顶（剪辑标记在所有元素之上，包括黄色标记和进度旋钮）
                self.progress_canvas.tag_raise("clip_start")
                self.progress_canvas.tag_raise("clip_end")
                self.progress_canvas.tag_raise("yellow_marker")
        
        # 最后绘制进度旋钮，确保它在所有元素之上
        knob_x = padding + progress_width
        knob_id = self.progress_canvas.create_oval(
            knob_x - 8, progress_bar_y - 5, knob_x + 8, progress_bar_y + progress_bar_height + 5,
            fill="#fff", outline="#ddd", width=2
        )
        # 为旋钮添加标签并设置为置顶
        self.progress_canvas.addtag_withtag("progress_knob", knob_id)
        self.progress_canvas.tag_raise("progress_knob")
    
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
            marker_time = self.current_time if self.video_file else time.time() - self.recording_start_time
            print(f"[调试] 添加标记: 时间={marker_time:.2f}")
            marker = {
                "id": self.marker_count + 1, "name": str(self.marker_count + 1), "time": marker_time, "note": ""
            }
            self.markers.append(marker)
            self.marker_count += 1
            print(f"[调试] 标记已添加，当前标记数量={len(self.markers)}")
            for i, m in enumerate(self.markers):
                print(f"[调试] 标记{i}: 时间={m['time']:.2f}")
            self.update_progress_bar()
            self.show_notification(f"已完成标记：{self.marker_count}", is_weak=True)
    
    def start_clip(self):
        if self.video_file and self.video_duration > 0:
            self.clip_mode = True
            self.clip_start = 0
            self.clip_end = self.video_duration
            # 切换按钮为取消截取
            self.clip_btn.config(text="取消截取", command=self.cancel_clip, state=tk.NORMAL)
            self.finish_clip_btn.config(state=tk.NORMAL)
            self.update_progress_bar()

    def cancel_clip(self):
        """取消截取视频"""
        self.clip_mode = False
        # 恢复按钮为截取视频
        self.clip_btn.config(text="截取视频", command=self.start_clip, state=tk.NORMAL)
        self.finish_clip_btn.config(state=tk.DISABLED)
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
                self.show_notification(f"已完成截取，片段时长：{self.format_time(clip['duration'])}", is_weak=True)
            self.clip_mode = False
            # 恢复按钮为截取视频
            self.clip_btn.config(text="截取视频", command=self.start_clip, state=tk.NORMAL)
            self.finish_clip_btn.config(state=tk.DISABLED)
            self.update_progress_bar()
    
    def on_clip_start_click(self, event):
        print(f"开始标记点击事件触发，坐标: ({event.x}, {event.y})")
        self.dragging_clip_start = True
    
    def on_clip_start_drag(self, event):
        if self.dragging_clip_start and self.clip_mode and self.video_duration > 0:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                padding = 20
                usable_width = width - 2 * padding
                # 计算新的开始位置，考虑留白
                if event.x < padding:
                    new_pos = padding
                elif event.x > width - padding:
                    new_pos = width - padding
                else:
                    new_pos = event.x
                new_time = ((new_pos - padding) / usable_width) * self.video_duration
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
                padding = 20
                usable_width = width - 2 * padding
                # 计算新的结束位置，考虑留白
                if event.x < padding:
                    new_pos = padding
                elif event.x > width - padding:
                    new_pos = width - padding
                else:
                    new_pos = event.x
                new_time = ((new_pos - padding) / usable_width) * self.video_duration
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
                padding = 20
                usable_width = width - 2 * padding
                # 计算拖动位置对应的时间，限制在画布范围内
                if event.x < padding:
                    new_pos = padding
                elif event.x > width - padding:
                    new_pos = width - padding
                else:
                    new_pos = event.x
                drag_time = ((new_pos - padding) / usable_width) * self.video_duration
                
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
            print("\n=== 开始播放剪辑 ===")
            print(f"剪辑信息: 开始时间={clip['start']:.2f}秒, 结束时间={clip['end']:.2f}秒, 时长={clip['duration']:.2f}秒")
            
            # 检查剪辑时间范围是否有效
            if clip['start'] >= clip['end']:
                print("[错误] 剪辑时间范围无效: 开始时间 >= 结束时间")
                messagebox.showerror("错误", "剪辑时间范围无效")
                return
            
            # 检查视频文件是否存在
            if not os.path.exists(self.video_file):
                print(f"[错误] 视频文件不存在: {self.video_file}")
                messagebox.showerror("错误", "视频文件不存在")
                return
            
            print(f"视频文件: {self.video_file}")
            print(f"文件大小: {os.path.getsize(self.video_file):,} 字节")
            
            # 停止当前可能正在播放的视频
            print(f"当前 stop_video 值: {self.stop_video}")
            self.stop_video = True
            print(f"设置 stop_video 为 True")
            if self.video_thread:
                print("等待当前视频线程结束...")
                self.video_thread.join(timeout=1)
                print("当前视频线程已结束")
            # 重置 stop_video 为 False，为新的剪辑播放做准备
            self.stop_video = False
            print(f"重置 stop_video 为 False")
            # 启动剪辑播放线程
            print("启动剪辑播放线程...")
            self.video_thread = threading.Thread(target=self.play_clip_thread, args=(clip,))
            self.video_thread.daemon = True
            self.video_thread.start()
            print("剪辑播放线程已启动")
    
    def play_clip_thread(self, clip):
        print("\n=== 剪辑播放线程开始 ===")
        print(f"线程ID: {threading.get_ident()}")
        cap = cv2.VideoCapture(self.video_file)
        if not cap.isOpened():
            print("[错误] 无法打开视频文件")
            messagebox.showerror("错误", "无法打开视频文件")
            return
        
        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"视频信息: FPS={fps:.1f}, 总帧数={total_frames}")
        
        start_frame = int(clip["start"] * fps)
        end_frame = int(clip["end"] * fps)
        print(f"剪辑范围: 开始帧={start_frame}, 结束帧={end_frame}")
        
        # 设置起始帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        current_frame = start_frame
        print(f"当前帧设置为: {current_frame}")
        
        # 计算弹窗大小为当前工具窗口的70%
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        if root_width == 0 or root_height == 0:
            # 如果窗口还未初始化，使用默认值
            root_width = 1200
            root_height = 800
        window_width = int(root_width * 0.7)
        window_height = int(root_height * 0.7)
        print(f"弹窗大小: {window_width}x{window_height}")
        
        # 创建播放窗口
        clip_window = tk.Toplevel(self.root)
        clip_window.title(f"播放片段 {clip['id']}")
        clip_window.geometry(f"{window_width}x{window_height}")
        clip_window.resizable(True, True)
        
        # 创建画布
        clip_canvas = tk.Canvas(clip_window, bg="black")
        clip_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 创建控制按钮框架
        control_frame = tk.Frame(clip_window, bg="#333")
        control_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        # 播放按钮
        def play_video():
            nonlocal is_playing, current_frame, frame_count
            if not is_playing:
                is_playing = True
                play_btn.config(state=tk.DISABLED)
                pause_btn.config(state=tk.NORMAL)
            # 如果已经播放到结尾，重新开始播放
            if current_frame > end_frame:
                current_frame = start_frame
                frame_count = 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                # 重置时间和进度条
                time_var.set(f"00:00 / {format_time(total_clip_frames / fps)}")
                width = progress_canvas.winfo_width()
                if width > 0:
                    progress_canvas.delete('all')
                    progress_canvas.create_rectangle(0, 0, width, 20, fill="#555", outline="")
                    progress_canvas.create_oval(-6, 2, 6, 18, fill="#fff", outline="#ddd", width=2)
        
        # 暂停按钮
        def pause_video():
            nonlocal is_playing
            if is_playing:
                is_playing = False
                play_btn.config(state=tk.NORMAL)
                pause_btn.config(state=tk.DISABLED)
        
        is_playing = True
        play_btn = tk.Button(control_frame, text="播放", command=play_video, padx=10, pady=5)
        play_btn.pack(side=tk.LEFT, padx=5)
        play_btn.config(state=tk.DISABLED)  # 初始状态下播放中，禁用播放按钮
        
        pause_btn = tk.Button(control_frame, text="暂停", command=pause_video, padx=10, pady=5)
        pause_btn.pack(side=tk.LEFT, padx=5)
        pause_btn.config(state=tk.NORMAL)  # 初始状态下播放中，启用暂停按钮
        
        # 关闭按钮（隐藏）
        def close_window():
            nonlocal stop_playback
            stop_playback = True
            cap.release()
            clip_window.destroy()
        
        # 隐藏关闭按钮，通过窗口关闭按钮关闭
        clip_window.protocol("WM_DELETE_WINDOW", close_window)
        
        # 时间轴和进度条（与主页面保持一致）
        time_frame = tk.Frame(control_frame, bg="#333")
        time_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # 时间标签
        time_var = tk.StringVar()
        time_var.set("00:00 / 00:00")
        time_label = tk.Label(time_frame, textvariable=time_var, fg="white", bg="#333")
        time_label.pack(side=tk.RIGHT, padx=10)
        
        # 进度条画布
        progress_canvas = tk.Canvas(time_frame, height=20, bg="#333", highlightthickness=0)
        progress_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # 进度条拖动状态
        progress_bar_dragging = False
        
        # 进度条点击事件
        def on_progress_click(event):
            nonlocal progress_bar_dragging, current_frame
            if not progress_bar_dragging:
                width = progress_canvas.winfo_width()
                if width > 0:
                    position = max(0, min(1, event.x / width))
                    # 计算新的帧位置
                    new_frame = int(start_frame + position * total_clip_frames)
                    new_frame = max(start_frame, min(end_frame, new_frame))
                    # 设置视频位置
                    cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
                    current_frame = new_frame
        
        # 进度条拖动事件
        def on_progress_drag(event):
            nonlocal progress_bar_dragging, current_frame
            if progress_bar_dragging:
                width = progress_canvas.winfo_width()
                if width > 0:
                    position = max(0, min(1, event.x / width))
                    # 计算新的帧位置
                    new_frame = int(start_frame + position * total_clip_frames)
                    new_frame = max(start_frame, min(end_frame, new_frame))
                    # 设置视频位置
                    cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
                    current_frame = new_frame
        
        # 进度条释放事件
        def on_progress_release(event):
            nonlocal progress_bar_dragging
            progress_bar_dragging = False
        
        # 绑定进度条事件
        progress_canvas.bind("<Button-1>", on_progress_click)
        progress_canvas.bind("<B1-Motion>", on_progress_drag)
        progress_canvas.bind("<ButtonRelease-1>", on_progress_release)
        
        # 窗口关闭事件
        clip_window.protocol("WM_DELETE_WINDOW", close_window)
        print("播放窗口已创建")
        
        # 确保 stop_video 为 False
        self.stop_video = False
        stop_playback = False
        print(f"线程内设置 stop_video 为: {self.stop_video}")
        
        # 计算总帧数，用于调试
        total_clip_frames = end_frame - start_frame + 1
        print(f"剪辑总帧数: {total_clip_frames}")
        
        # 格式化时间函数
        def format_time(seconds):
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes:02d}:{secs:02d}"
        
        # 检查循环条件
        print(f"循环前检查: current_frame={current_frame}, end_frame={end_frame}, stop_video={self.stop_video}")
        print(f"循环条件: {current_frame <= end_frame} and {not self.stop_video} and {not stop_playback} = {current_frame <= end_frame and not self.stop_video and not stop_playback}")
        
        frame_count = 0
        # 主循环：保持线程活跃，支持重复播放
        while not self.stop_video and not stop_playback:
            # 检查是否需要重新开始播放
            if is_playing:
                # 如果已经播放到结尾，停止播放
                if current_frame > end_frame:
                    is_playing = False
                    play_btn.config(state=tk.NORMAL)  # 启用播放按钮
                    pause_btn.config(state=tk.DISABLED)  # 禁用暂停按钮
                    # 重置到开始位置
                    current_frame = start_frame
                    frame_count = 0
                    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                    # 重置时间和进度条
                    time_var.set(f"00:00 / {format_time(total_clip_frames / fps)}")
                    width = progress_canvas.winfo_width()
                    if width > 0:
                        progress_canvas.delete('all')
                        progress_canvas.create_rectangle(0, 0, width, 20, fill="#555", outline="")
                        progress_canvas.create_oval(-6, 2, 6, 18, fill="#fff", outline="#ddd", width=2)
                    # 跳过本次循环，等待用户点击播放
                    clip_window.update()
                    time.sleep(0.1)
                    continue
                
                # 检查是否到达结束帧
                if current_frame == end_frame:
                    # 播放完最后一帧后停止
                    is_playing = False
                    play_btn.config(state=tk.NORMAL)  # 启用播放按钮
                    pause_btn.config(state=tk.DISABLED)  # 禁用暂停按钮
                    # 重置到开始位置
                    current_frame = start_frame
                    frame_count = 0
                    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                    # 重置时间和进度条
                    time_var.set(f"00:00 / {format_time(total_clip_frames / fps)}")
                    width = progress_canvas.winfo_width()
                    if width > 0:
                        progress_canvas.delete('all')
                        progress_canvas.create_rectangle(0, 0, width, 20, fill="#555", outline="")
                        progress_canvas.create_oval(-6, 2, 6, 18, fill="#fff", outline="#ddd", width=2)
                    # 跳过本次循环，等待用户点击播放
                    clip_window.update()
                    time.sleep(0.1)
                    continue
                
                print(f"\n循环开始: 第{frame_count}次迭代")
                print(f"当前状态: current_frame={current_frame}, end_frame={end_frame}, stop_video={self.stop_video}, stop_playback={stop_playback}")
                
                # 读取帧
                ret, frame = cap.read()
                print(f"读取帧: ret={ret}")
                
                if not ret:
                    print(f"[警告] 读取帧失败，当前帧: {current_frame}")
                    # 停止播放
                    is_playing = False
                    play_btn.config(state=tk.NORMAL)  # 启用播放按钮
                    pause_btn.config(state=tk.DISABLED)  # 禁用暂停按钮
                    # 重置到开始位置
                    current_frame = start_frame
                    frame_count = 0
                    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                    # 重置时间和进度条
                    time_var.set(f"00:00 / {format_time(total_clip_frames / fps)}")
                    width = progress_canvas.winfo_width()
                    if width > 0:
                        progress_canvas.delete('all')
                        progress_canvas.create_rectangle(0, 0, width, 20, fill="#555", outline="")
                        progress_canvas.create_oval(-6, 2, 6, 18, fill="#fff", outline="#ddd", width=2)
                    # 跳过本次循环，等待用户点击播放
                    clip_window.update()
                    time.sleep(0.1)
                    continue
                
                # 转换颜色并调整大小以适应窗口
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # 获取画布大小
                canvas_width = clip_canvas.winfo_width()
                canvas_height = clip_canvas.winfo_height()
                if canvas_width > 0 and canvas_height > 0:
                    # 调整帧大小
                    img = Image.fromarray(frame)
                    img = img.resize((canvas_width, canvas_height), Image.LANCZOS)
                    imgtk = ImageTk.PhotoImage(image=img)
                    clip_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                    clip_canvas.imgtk = imgtk
                
                clip_window.update()
                print("帧已显示")
                
                # 延时
                time.sleep(1/fps)  # 使用视频的实际帧率
                current_frame += 1
                frame_count += 1
                
                # 计算当前时间和总时间
                current_time = (current_frame - start_frame) / fps
                total_time = total_clip_frames / fps
                
                # 更新时间标签
                time_var.set(f"{format_time(current_time)} / {format_time(total_time)}")
                
                # 更新进度条
                width = progress_canvas.winfo_width()
                if width > 0:
                    progress = (current_frame - start_frame) / total_clip_frames
                    progress_width = int(width * progress)
                    # 清除旧的进度条
                    progress_canvas.delete('all')
                    # 绘制背景
                    progress_canvas.create_rectangle(0, 0, width, 20, fill="#555", outline="")
                    # 绘制进度
                    progress_canvas.create_rectangle(0, 0, progress_width, 20, fill="#4CAF50", outline="")
                    # 绘制旋钮
                    knob_x = progress_width
                    progress_canvas.create_oval(knob_x - 6, 2, knob_x + 6, 18, fill="#fff", outline="#ddd", width=2)
                
                # 每5帧打印一次进度
                if frame_count % 5 == 0:
                    print(f"播放进度: 帧 {current_frame}/{end_frame} ({(current_frame-start_frame)/total_clip_frames*100:.1f}%)")
            else:
                # 暂停状态或等待播放
                clip_window.update()
                time.sleep(0.1)
        
        print(f"\n=== 循环结束 ===")
        print(f"最终状态: current_frame={current_frame}, end_frame={end_frame}, stop_video={self.stop_video}, stop_playback={stop_playback}")
        print(f"播放了 {frame_count} 帧")
        
        # 清理
        print("释放视频捕获")
        cap.release()
        print("销毁播放窗口")
        clip_window.destroy()
        print("剪辑播放线程结束")
    
    def on_clip_window_close(self, window, cap):
        """旧的窗口关闭处理函数（保留以确保兼容性）"""
        self.stop_video = True
        try:
            cap.release()
        except:
            pass
        try:
            window.destroy()
        except:
            pass
    
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
        print("\n=== 主页面视频播放线程开始 ===")
        self.video_capture = cv2.VideoCapture(self.video_file)
        if not self.video_capture.isOpened():
            messagebox.showerror("错误", "无法打开视频文件")
            self.video_playing = False
            self.play_btn.config(state=tk.NORMAL)
            self.pause_video_btn.config(state=tk.DISABLED)
            return
        self.stop_video = False
        frame_count = 0
        print(f"开始播放视频: {self.video_file}")
        
        # 检查是否处于截取视频状态
        if self.clip_mode and self.video_duration > 0:
            # 设置视频起始位置为入点
            start_pos_msec = self.clip_start * 1000
            self.video_capture.set(cv2.CAP_PROP_POS_MSEC, start_pos_msec)
            print(f"截取模式：从 {self.clip_start:.2f} 秒开始播放，到 {self.clip_end:.2f} 秒结束")
        
        while self.video_playing and not self.stop_video:
            if not self.video_paused:
                ret, frame = self.video_capture.read()
                if not ret:
                    print(f"[主页面] 读取帧失败，播放结束")
                    break
                # 获取当前播放位置（毫秒）并更新 current_time
                current_pos_msec = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)
                self.current_time = current_pos_msec / 1000.0
                
                # 检查是否处于截取视频状态，如果是，检查是否到达出点
                if self.clip_mode and self.video_duration > 0:
                    if self.current_time > self.clip_end:
                        print(f"[主页面] 到达出点 {self.clip_end:.2f} 秒，播放结束")
                        break
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                # 缩放帧以适应canvas大小，保持宽高比
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                if canvas_width > 0 and canvas_height > 0:
                    img_width, img_height = img.size
                    canvas_ratio = canvas_width / canvas_height
                    img_ratio = img_width / img_height
                    
                    if canvas_ratio > img_ratio:
                        # Canvas更宽，以高度为基准缩放
                        new_height = canvas_height
                        new_width = int(img_width * (canvas_height / img_height))
                    else:
                        # Canvas更高，以宽度为基准缩放
                        new_width = canvas_width
                        new_height = int(img_height * (canvas_width / img_width))
                    
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=imgtk)
                self.canvas.imgtk = imgtk
                self.root.update()
                
                # 每10帧更新一次进度条，避免过于频繁的更新
                frame_count += 1
                if frame_count % 10 == 0:
                    self.update_progress_bar()
                    self.update_time_label()
                
                time.sleep(0.05)
            else:
                time.sleep(0.1)
        
        print(f"[主页面] 播放循环结束，frame_count={frame_count}")
        
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        self.video_playing = False
        self.play_btn.config(state=tk.NORMAL)
        self.pause_video_btn.config(state=tk.DISABLED)
        # 播放结束时更新进度条到结束位置
        self.current_time = self.video_duration
        self.update_progress_bar()
        self.update_time_label()
        print("[主页面] 视频播放完成，状态已更新")
    
    def pause_video(self):
        self.video_paused = not self.video_paused
    
    def on_progress_click(self, event):
        if self.video_duration > 0:
            # 检查是否点击了剪辑标记区域
            if not self.clip_mode:
                self.progress_bar_dragging = True
                width = self.progress_canvas.winfo_width()
                if width > 0:
                    padding = 20
                    usable_width = width - 2 * padding
                    # 计算点击位置，考虑留白
                    if event.x < padding:
                        position = 0
                    elif event.x > width - padding:
                        position = 1
                    else:
                        position = (event.x - padding) / usable_width
                    self.current_time = position * self.video_duration
                    # 显示时间提示
                    self.show_time_tooltip(event.x, event.y, self.current_time)
                    self.update_progress_bar()
                    self.update_time_label()
            else:
                # 在剪辑模式下，不处理进度条点击，让剪辑标记的点击事件优先处理
                pass
    
    def on_progress_drag(self, event):
        if self.progress_bar_dragging and self.video_duration > 0:
            width = self.progress_canvas.winfo_width()
            if width > 0:
                padding = 20
                usable_width = width - 2 * padding
                # 计算拖动位置，考虑留白
                if event.x < padding:
                    position = 0
                elif event.x > width - padding:
                    position = 1
                else:
                    position = (event.x - padding) / usable_width
                self.current_time = position * self.video_duration
                # 显示时间提示
                self.show_time_tooltip(event.x, event.y, self.current_time)
                self.update_progress_bar()
                self.update_time_label()
    
    def on_progress_release(self, event):
        if self.progress_bar_dragging:
            self.progress_bar_dragging = False
            if self.video_playing and self.video_capture:
                self.video_capture.set(cv2.CAP_PROP_POS_MSEC, self.current_time * 1000)
            # 销毁时间提示窗口
            if hasattr(self, 'time_tooltip') and self.time_tooltip:
                try:
                    self.time_tooltip.destroy()
                except:
                    pass
    
    def show_notification(self, message, is_weak=False):
        if is_weak:
            # 弱提示，自动消失
            weak_notification = tk.Toplevel(self.root)
            weak_notification.title("通知")
            weak_notification.geometry("260x80")
            weak_notification.transient(self.root)
            weak_notification.attributes('-topmost', True)
            weak_notification.configure(bg=self.card_bg)
            
            # 添加边框效果
            weak_notification.overrideredirect(True)
            
            # 创建圆角效果的画布
            canvas = tk.Canvas(weak_notification, width=260, height=80, bg=self.card_bg, 
                            highlightthickness=1, highlightbackground=self.border_color)
            canvas.pack()
            
            # 绘制圆角背景
            def create_roundrectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
                points = [
                    x1+radius, y1,
                    x2-radius, y1,
                    x2, y1+radius,
                    x2, y2-radius,
                    x2-radius, y2,
                    x1+radius, y2,
                    x1, y2-radius,
                    x1, y1+radius
                ]
                return canvas.create_polygon(points, **kwargs)
            
            create_roundrectangle(canvas, 0, 0, 260, 80, 8, fill=self.light_bg, outline=self.accent_color)
            
            # 添加文本
            canvas.create_text(130, 40, text=message, fill=self.text_color, font=('Arial', 10, 'bold'))
            
            # 计算位置，让通知显示在屏幕右下角
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = screen_width - 280
            y = screen_height - 100
            weak_notification.geometry(f"260x80+{x}+{y}")
            
            # 显示通知
            weak_notification.deiconify()
            
            # 2秒后自动销毁
            self.root.after(2000, lambda: weak_notification.destroy())
        else:
            # 强提示，需要用户确认
            self.notification_label.config(text=message)
            self.notification.deiconify()
    
    def open_marker_edit(self):
        if 0 <= self.current_marker_index < len(self.markers):
            marker = self.markers[self.current_marker_index]
            self.marker_name_var.set(marker.get("name", str(marker["id"])))
            self.marker_note_var.set(marker.get("note", ""))
            self.marker_edit_window.deiconify()
    
    def save_marker_edit(self):
        if 0 <= self.current_marker_index < len(self.markers):
            marker = self.markers[self.current_marker_index]
            marker["name"] = self.marker_name_var.get() or str(marker["id"])
            marker["note"] = self.marker_note_var.get()
            self.marker_edit_window.withdraw()
            self.notification.withdraw()
    
    def create_mini_control(self):
        """创建缩略功能区"""
        # 检查是否已存在缩略功能区
        if hasattr(self, 'mini_window') and self.mini_window:
            try:
                self.mini_window.destroy()
            except:
                pass
        
        # 创建缩略功能区窗口 - 作为完全独立的窗口
        self.mini_window = tk.Toplevel()  # 不指定master，使其成为独立窗口
        self.mini_window.title("录屏控制")
        self.mini_window.geometry("450x150")  # 增大窗口大小，确保能容纳所有内容
        self.mini_window.attributes('-topmost', True)  # 始终显示在最前面
        self.mini_window.attributes('-toolwindow', True)  # 工具窗口风格
        self.mini_window.configure(bg="#1a1a1a")  # 直接使用颜色值，避免依赖主窗口
        
        # 固定在屏幕顶部
        self.mini_window.geometry("450x150+50+50")
        
        # 创建控制按钮
        button_frame = tk.Frame(self.mini_window, bg="#1a1a1a")
        button_frame.pack(fill=tk.X, pady=20, padx=20)  # 增加边距
        
        # 创建按钮
        self.mini_pause_btn = ttk.Button(button_frame, text="暂停录屏", command=self.pause_recording, width=10)
        self.mini_pause_btn.pack(side=tk.LEFT, padx=10)  # 增加按钮间距
        
        self.mini_stop_btn = ttk.Button(button_frame, text="结束录屏", command=self.stop_recording, width=10)
        self.mini_stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.mini_mark_btn = ttk.Button(button_frame, text="标记进度", command=self.mark_progress, width=10)
        self.mini_mark_btn.pack(side=tk.LEFT, padx=10)
        
        # 添加状态标签
        self.mini_status_label = tk.Label(self.mini_window, text="录屏中...", 
                                        font=('Arial', 10),  # 增大字体
                                        bg="#1a1a1a", fg='green')
        self.mini_status_label.pack(pady=15)
        
        # 确保窗口显示在最前面
        self.mini_window.update_idletasks()  # 强制更新窗口任务
        self.mini_window.update()  # 强制更新窗口
        self.mini_window.lift()
        self.mini_window.focus_force()
        self.mini_window.deiconify()
        
        # 重写窗口关闭行为，确保点击关闭按钮时只是隐藏窗口，而不是销毁
        def on_close():
            self.mini_window.withdraw()
        
        self.mini_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def close_mini_control(self):
        """关闭缩略功能区"""
        if hasattr(self, 'mini_window') and self.mini_window:
            try:
                self.mini_window.destroy()
                self.mini_window = None
            except:
                pass
    
    def show_time_tooltip(self, x, y, time_seconds):
        """显示时间提示"""
        # 销毁之前的提示窗口
        if hasattr(self, 'time_tooltip') and self.time_tooltip:
            try:
                self.time_tooltip.destroy()
            except:
                pass
        
        # 创建新的提示窗口
        self.time_tooltip = tk.Toplevel(self.root)
        self.time_tooltip.title("")
        self.time_tooltip.geometry("80x30")
        self.time_tooltip.transient(self.root)
        self.time_tooltip.overrideredirect(True)  # 无标题栏
        self.time_tooltip.attributes('-topmost', True)
        self.time_tooltip.configure(bg="#333", relief="solid", borderwidth=1)
        
        # 格式化时间
        time_str = self.format_time(time_seconds)
        
        # 创建标签
        label = tk.Label(self.time_tooltip, text=time_str, 
                        font=('Arial', 10), 
                        bg="#333", fg="#fff")
        label.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        
        # 计算提示窗口位置
        # 将坐标从canvas转换为屏幕坐标
        canvas_x = self.progress_canvas.winfo_rootx() + x
        canvas_y = self.progress_canvas.winfo_rooty() + y
        
        # 调整位置，使提示窗口显示在鼠标上方
        tooltip_width = 80
        tooltip_height = 30
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 确保提示窗口在屏幕内
        tooltip_x = canvas_x - tooltip_width // 2
        tooltip_y = canvas_y - tooltip_height - 10
        
        if tooltip_x < 0:
            tooltip_x = 0
        elif tooltip_x + tooltip_width > screen_width:
            tooltip_x = screen_width - tooltip_width
        
        if tooltip_y < 0:
            tooltip_y = canvas_y + 10
        
        self.time_tooltip.geometry(f"{tooltip_width}x{tooltip_height}+{tooltip_x}+{tooltip_y}")
    
    def save_recording_path(self):
        """保存录制路径到文件"""
        if self.video_file:
            try:
                with open(self.recordings_file, 'a', encoding='utf-8') as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {self.video_file}\n")
            except Exception as e:
                print(f"保存录制路径失败: {e}")
    
    def format_time(self, seconds):
        """格式化时间为 MM:SS 格式"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

if __name__ == "__main__":
    from PIL import Image, ImageTk
    root = tk.Tk()
    app = ScreenRecorder(root)
    root.mainloop()