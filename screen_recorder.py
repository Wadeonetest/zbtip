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
        self.root.title("灞忓箷褰曞埗宸ュ叿")
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

        self.create_ui()

    def create_ui(self):
        self.control_frame = ttk.Frame(self.root, padding=10)
        self.control_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Label(self.control_frame, text="灞忓箷褰曞埗宸ュ叿", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

        self.button_frame = ttk.Frame(self.control_frame)
        self.button_frame.pack(side=tk.RIGHT)

        self.start_btn = ttk.Button(self.button_frame, text="寮€濮嬪綍灞?, command=self.start_recording)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = ttk.Button(self.button_frame, text="鏆傚仠褰曞睆", command=self.pause_recording, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(self.button_frame, text="缁撴潫褰曞睆", command=self.stop_recording, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.mark_btn = ttk.Button(self.button_frame, text="鏍囪杩涘害", command=self.mark_progress, state=tk.DISABLED)
        self.mark_btn.pack(side=tk.LEFT, padx=5)

        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.area_frame = ttk.LabelFrame(self.left_frame, text="褰曞睆鍖哄煙璁剧疆", padding=10)
        self.area_frame.pack(fill=tk.X, padx=5, pady=5)

        area_grid = ttk.Frame(self.area_frame)
        area_grid.pack(fill=tk.X)

        ttk.Label(area_grid, text="X鍧愭爣:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.x_entry = ttk.Entry(area_grid, width=10)
        self.x_entry.insert(0, "0")
        self.x_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(area_grid, text="Y鍧愭爣:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.y_entry = ttk.Entry(area_grid, width=10)
        self.y_entry.insert(0, "0")
        self.y_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(area_grid, text="瀹藉害:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.width_entry = ttk.Entry(area_grid, width=10)
        self.width_entry.insert(0, "1080")
        self.width_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(area_grid, text="楂樺害:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.height_entry = ttk.Entry(area_grid, width=10)
        self.height_entry.insert(0, "608")
        self.height_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(area_grid, text="鎷栨嫿閫夋嫨鍖哄煙", command=self.start_drag_selection).grid(row=2, column=0, columnspan=4, pady=10)

        self.video_frame = ttk.LabelFrame(self.left_frame, text="瑙嗛棰勮", padding=10)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(self.video_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        video_controls = ttk.Frame(self.video_frame, padding=5)
        video_controls.pack(fill=tk.X, pady=5)

        self.play_btn = ttk.Button(video_controls, text="鎾斁", command=self.play_video, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=5)

        self.pause_video_btn = ttk.Button(video_controls, text="鏆傚仠", command=self.pause_video, state=tk.DISABLED)
        self.pause_video_btn.pack(side=tk.LEFT, padx=5)

        self.progress_frame = ttk.Frame(self.left_frame, padding=10)
        self.progress_frame.pack(fill=tk.X, padx=5, pady=5)

        self.progress_canvas = tk.Canvas(self.progress_frame, height=20, bg="#333", cursor="hand1")
        self.progress_canvas.pack(fill=tk.X, padx=5)

        self.progress_canvas.bind('<Button-1>', self.on_progress_click)
        self.progress_canvas.bind('<B1-Motion>', self.on_progress_drag)
        self.progress_canvas.bind('<ButtonRelease-1>', self.on_progress_release)

        self.time_label = ttk.Label(self.progress_frame, text="00:00 / 00:00")
        self.time_label.pack(side=tk.RIGHT, padx=5)

        self.right_frame = ttk.LabelFrame(self.main_frame, text="瑙嗛鐗囨", padding=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        self.clip_listbox = tk.Listbox(self.right_frame, height=20)
        self.clip_listbox.pack(fill=tk.BOTH, expand=True)

        clip_buttons = ttk.Frame(self.right_frame)
        clip_buttons.pack(fill=tk.X, pady=10)

        ttk.Button(clip_buttons, text="鎾斁閫変腑鐗囨", command=self.play_selected_clip).pack(side=tk.LEFT, padx=5)
        ttk.Button(clip_buttons, text="鍒犻櫎閫変腑鐗囨", command=self.delete_selected_clip).pack(side=tk.LEFT, padx=5)

        self.notification = tk.Toplevel(self.root)
        self.notification.title("閫氱煡")
        self.notification.geometry("300x100")
        self.notification.transient(self.root)
        self.notification.withdraw()

        self.notification_label = ttk.Label(self.notification, text="")
        self.notification_label.pack(pady=10)

        notification_buttons = ttk.Frame(self.notification)
        notification_buttons.pack(pady=10)

        ttk.Button(notification_buttons, text="缂栬緫", command=self.open_marker_edit).pack(side=tk.LEFT, padx=5)
        ttk.Button(notification_buttons, text="纭畾", command=self.notification.withdraw).pack(side=tk.LEFT, padx=5)

        self.marker_edit_window = tk.Toplevel(self.root)
        self.marker_edit_window.title("缂栬緫鏍囪")
        self.marker_edit_window.geometry("400x200")
        self.marker_edit_window.transient(self.root)
        self.marker_edit_window.withdraw()

        ttk.Label(self.marker_edit_window, text="鏍囪鍚嶇О:").pack(pady=5)
        self.marker_name_var = tk.StringVar()
        ttk.Entry(self.marker_edit_window, textvariable=self.marker_name_var).pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.marker_edit_window, text="澶囨敞:").pack(pady=5)
        self.marker_note_var = tk.StringVar()
        ttk.Entry(self.marker_edit_window, textvariable=self.marker_note_var).pack(fill=tk.X, padx=10, pady=5)

        edit_buttons = ttk.Frame(self.marker_edit_window)
        edit_buttons.pack(pady=10)

        ttk.Button(edit_buttons, text="淇濆瓨", command=self.save_marker_edit).pack(side=tk.LEFT, padx=5)
        ttk.Button(edit_buttons, text="鍙栨秷", command=self.marker_edit_window.withdraw).pack(side=tk.LEFT, padx=5)

        self.current_marker_index = -1

        self.drag_thread = None
        self.drag_running = False

    def start_drag_selection(self):
        messagebox.showinfo("鎻愮ず", "璇峰湪灞忓箷涓婃嫋鎷介€夋嫨褰曞埗鍖哄煙锛屾寜Esc閿彇娑?)

        self.drag_window = tk.Toplevel(self.root)
        self.drag_window.attributes('-alpha', 0.3)
        self.drag_window.attributes('-fullscreen', True)
        self.drag_window.attributes('-topmost', True)

        self.drag_canvas = tk.Canvas(self.drag_window, bg='black', cursor='cross')
        self.drag_canvas.pack(fill=tk.BOTH, expand=True)

        self.drag_canvas.bind('<Button-1>', self.on_drag_start)
        self.drag_canvas.bind('<B1-Motion>', self.on_drag_motion)
        self.drag_canvas.bind('<ButtonRelease-1>', self.on_drag_end)
        self.drag_window.bind('<Escape>', lambda e: self.drag_window.destroy())

    def on_drag_start(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.selection_rect = self.drag_canvas.create_rectangle(
            self.drag_start_x, self.drag_start_y,
            self.drag_start_x, self.drag_start_y,
            outline='red', width=2
        )

    def on_drag_motion(self, event):
        self.drag_canvas.coords(
            self.selection_rect,
            self.drag_start_x, self.drag_start_y,
            event.x, event.y
        )

    def on_drag_end(self, event):
        x = min(self.drag_start_x, event.x)
        y = min(self.drag_start_y, event.y)
        width = abs(event.x - self.drag_start_x)
        height = abs(event.y - self.drag_start_y)

        if width > 0 and height > 0:
            self.x_entry.delete(0, tk.END)
            self.x_entry.insert(0, str(x))

            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, str(y))

            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(width))

            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(height))

        self.drag_window.destroy()

    def start_recording(self):
        try:
            self.x = int(self.x_entry.get())
            self.y = int(self.y_entry.get())
            self.width = int(self.width_entry.get())
            self.height = int(self.height_entry.get())

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_file = f"recording_{int(time.time())}.mp4"
            self.recorder = cv2.VideoWriter(self.video_file, fourcc, 20.0, (self.width, self.height))

            self.recording_start_time = time.time()
            self.recorded_frames = 0

            self.recording = True
            self.paused = False
            self.recording_thread = threading.Thread(target=self.record_screen)
            self.recording_thread.daemon = True
            self.recording_thread.start()

            self.stop_update = False
            self.update_thread = threading.Thread(target=self.update_progress)
            self.update_thread.daemon = True
            self.update_thread.start()

            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.mark_btn.config(state=tk.NORMAL)

            messagebox.showinfo("鎻愮ず", "寮€濮嬪綍灞?)
        except Exception as e:
            messagebox.showerror("閿欒", f"寮€濮嬪綍灞忓け璐? {str(e)}")

    def record_screen(self):
        target_fps = 20.0
        frame_duration = 1.0 / target_fps

        while self.recording:
            if not self.paused:
                frame_start = time.time()

                screenshot = pyautogui.screenshot(region=(self.x, self.y, self.width, self.height))
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                self.recorder.write(frame)
                self.recorded_frames += 1

                frame_time = time.time() - frame_start
                sleep_time = frame_duration - frame_time
                if sleep_time > 0:
                    time.sleep(sleep_time)

    def pause_recording(self):
        if self.recording:
            self.paused = not self.paused
            if self.paused:
                self.pause_btn.config(text="缁х画褰曞睆")
            else:
                self.pause_btn.config(text="鏆傚仠褰曞睆")

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.recording_thread.join()

            if self.recorder:
                self.recorder.release()

            self.video_duration = self.recorded_frames / 20.0

            self.save_recording_path()

            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED, text="鏆傚仠褰曞睆")
            self.stop_btn.config(state=tk.DISABLED)

            self.markers = []
            self.marker_count = 0
            self.clips = []
            self.clip_start = None
            self.current_time = 0
            self.video_paused = False
            self.video_playing = False

            self.update_time_label()
            self.update_progress_bar()

            self.play_btn.config(state=tk.NORMAL)

            messagebox.showinfo("鎻愮ず", f"褰曞睆宸蹭繚瀛樹负: {self.video_file}")

    def save_recording_path(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            recordings_file_path = os.path.join(current_dir, self.recordings_file)

            with open(recordings_file_path, 'a', encoding='utf-8') as f:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp} - {os.path.join(current_dir, self.video_file)}\n")
        except Exception as e:
            print(f"[ERROR] 淇濆瓨褰曞睆璺緞澶辫触: {str(e)}", file=sys.stderr)

    def on_progress_click(self, event):
        if self.video_duration > 0:
            self.progress_bar_dragging = True
            width = self.progress_canvas.winfo_width()
            if width > 0:
                position = max(0, min(1, event.x / width))
                self.current_time = position * self.video_duration
                self.update_progress_bar()
                self.update_time_label()

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
            elif not self.video_playing and self.video_duration > 0:
                if self.clip_start is None:
                    self.clip_start = self.current_time
                else:
                    clip_end = self.current_time
                    if self.clip_start < clip_end:
                        clip = {
                            "id": len(self.clips) + 1, "start": self.clip_start, "end": clip_end, "duration": clip_end - self.clip_start
                        }
                        self.clips.append(clip)
                        self.update_clips()
                    self.clip_start = None

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
                        self.progress_canvas.tag_bind(marker_id, '<Button-1>', lambda e, idx=self.markers.index(marker): self.jump_to_marker_and_play(idx))

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

            self.show_notification(f"宸插畬鎴愭爣璁帮細{self.marker_count}")

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
            self.clip_listbox.insert(tk.END, f"鐗囨 {clip['id']}: {start} - {end} ({duration})")

    def play_selected_clip(self):
        selection = self.clip_listbox.curselection()
        if selection and self.video_file:
            index = selection[0]
            if 0 <= index < len(self.clips):
                if self.video_playing:
                    self.pause_video()
                    if self.video_thread:
                        self.video_thread.join(timeout=0.5)

                clip = self.clips[index]
                self.current_time = clip["start"]
                self.update_progress_bar()
                self.update_time_label()

                self.play_video()

    def delete_selected_clip(self):
        selection = self.clip_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.clips):
                self.clips.pop(index)
                self.update_clips()

    def play_video(self):
        if self.video_file:
            if self.video_playing:
                self.pause_video()
                if self.video_thread:
                    self.video_thread.join(timeout=0.5)

            try:
                self.video_capture = cv2.VideoCapture(self.video_file)

                if not self.video_capture.isOpened():
                    messagebox.showerror("閿欒", "鏃犳硶鎵撳紑瑙嗛鏂囦欢")
                    return

                if self.current_time > 0:
                    self.video_capture.set(cv2.CAP_PROP_POS_MSEC, self.current_time * 1000)

                self.video_playing = True
                self.video_paused = False
                self.stop_video = False
                self.video_thread = threading.Thread(target=self.play_video_thread)
                self.video_thread.daemon = True
                self.video_thread.start()

                self.play_btn.config(state=tk.DISABLED)
                self.pause_video_btn.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("閿欒", f"鎾斁瑙嗛澶辫触: {str(e)}")
                self.video_playing = False
                self.play_btn.config(state=tk.NORMAL)
                self.pause_video_btn.config(state=tk.DISABLED)

    def play_video_thread(self):
        while self.video_playing and not self.stop_video:
            try:
                if self.video_paused:
                    time.sleep(0.05)
                    continue

                ret, frame = self.video_capture.read()

                if not ret:
                    self.video_playing = False
                    break

                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()

                if canvas_width > 0 and canvas_height > 0:
                    frame_height, frame_width = frame.shape[:2]
                    aspect_ratio = frame_width / frame_height

                    if canvas_width / canvas_height > aspect_ratio:
                        new_height = canvas_height
                        new_width = int(new_height * aspect_ratio)
                    else:
                        new_width = canvas_width
                        new_height = int(new_width / aspect_ratio)

                    resized_frame = cv2.resize(frame, (new_width, new_height))

                    rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

                    from PIL import Image, ImageTk
                    image = Image.fromarray(rgb_frame)
                    photo = ImageTk.PhotoImage(image=image)

                    self.canvas.create_image(
                        canvas_width // 2, canvas_height // 2, image=photo, anchor=tk.CENTER
                    )
                    self.canvas.image = photo

                if not self.progress_bar_dragging:
                    current_time = self.video_capture.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                    self.current_time = current_time
                    self.update_progress_bar()
                    self.update_time_label()

                time.sleep(1/30)
            except Exception as e:
                self.video_playing = False
                break

        try:
            if self.video_capture:
                self.video_capture.release()
                self.video_capture = None
        except:
            pass

        self.play_btn.config(state=tk.NORMAL)
        self.pause_video_btn.config(state=tk.DISABLED)
        self.video_playing = False

    def pause_video(self):
        self.video_paused = not self.video_paused
        if self.video_paused:
            self.pause_video_btn.config(text="缁х画")
        else:
            self.pause_video_btn.config(text="鏆傚仠")

    def show_notification(self, message):
        self.notification_label.config(text=message)
        self.notification.deiconify()
        self.root.after(3000, self.notification.withdraw)

    def open_marker_edit(self):
        if self.markers:
            last_marker = self.markers[-1]
            self.current_marker_index = len(self.markers) - 1
            self.marker_name_var.set(last_marker["name"])
            self.marker_note_var.set(last_marker["note"])
            self.marker_edit_window.deiconify()

    def save_marker_edit(self):
        if 0 <= self.current_marker_index < len(self.markers):
            self.markers[self.current_marker_index]["name"] = self.marker_name_var.get() or self.markers[self.current_marker_index]["name"]
            self.markers[self.current_marker_index]["note"] = self.marker_note_var.get()
            self.update_progress_bar()
            self.marker_edit_window.withdraw()

    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def on_closing(self):
        self.stop_update = True
        self.stop_video = True
        if self.update_thread:
            self.update_thread.join(timeout=1)
        if self.video_thread:
            self.video_thread.join(timeout=1)
        if self.video_capture:
            try:
                self.video_capture.release()
            except:
                pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorder(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()