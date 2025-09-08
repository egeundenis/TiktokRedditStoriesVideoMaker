import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
from utils import text_to_speech, speed_up_audio
from video_processor import prepare_video, transcribe_and_chunk, burn_subtitles

# -------------------------------
# GUI
# -------------------------------
class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("TikTok Video Maker")
        self.geometry("650x700")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # ---------------- Simple Mode ----------------
        self.simple_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.simple_frame, text="Simple Mode")
        self.build_simple_ui()

        # ---------------- Advanced Mode ----------------
        self.advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_frame, text="Advanced Mode")
        self.build_advanced_ui()

    # ---------------- Simple Mode UI ----------------
    def build_simple_ui(self):
        self.text_file = None
        self.video_file = None
        self.bg_music_file = None

        ttk.Label(self.simple_frame, text="📄 Drag & Drop Text File (.txt)").pack(pady=10)
        self.audio_drop = tk.Text(self.simple_frame, height=2, width=60)
        self.audio_drop.pack()
        self.audio_drop.drop_target_register(DND_FILES)
        self.audio_drop.dnd_bind("<<Drop>>", self.set_text)

        ttk.Label(self.simple_frame, text="🎬 Drag & Drop Background Video").pack(pady=10)
        self.video_drop = tk.Text(self.simple_frame, height=2, width=60)
        self.video_drop.pack()
        self.video_drop.drop_target_register(DND_FILES)
        self.video_drop.dnd_bind("<<Drop>>", self.set_video)

        ttk.Label(self.simple_frame, text="🎼 Drag & Drop Background Music (optional)").pack(pady=10)
        self.music_drop = tk.Text(self.simple_frame, height=2, width=60)
        self.music_drop.pack()
        self.music_drop.drop_target_register(DND_FILES)
        self.music_drop.dnd_bind("<<Drop>>", self.set_music)

        self.start_btn = ttk.Button(self.simple_frame, text="🚀 Start", command=self.start_process)
        self.start_btn.pack(pady=20)

        ttk.Label(self.simple_frame, text="Process Log:").pack(pady=5)
        self.log_box = tk.Text(self.simple_frame, height=10, width=70, state="disabled", wrap="word")
        self.log_box.pack(pady=5)

    # ---------------- Advanced Mode UI ----------------
    def build_advanced_ui(self):
        self.adv_text_file = None
        self.adv_video_file = None
        self.adv_music_file = None
        self.adv_narration_file = None

        ttk.Label(self.advanced_frame, text="📄 Drag & Drop Text File (.txt) OR Narration MP3").pack(pady=10)
        self.adv_text_drop = tk.Text(self.advanced_frame, height=2, width=60)
        self.adv_text_drop.pack()
        self.adv_text_drop.drop_target_register(DND_FILES)
        self.adv_text_drop.dnd_bind("<<Drop>>", self.set_adv_text_or_audio)

        ttk.Label(self.advanced_frame, text="🎬 Drag & Drop Background Video").pack(pady=10)
        self.adv_video_drop = tk.Text(self.advanced_frame, height=2, width=60)
        self.adv_video_drop.pack()
        self.adv_video_drop.drop_target_register(DND_FILES)
        self.adv_video_drop.dnd_bind("<<Drop>>", self.set_adv_video)

        ttk.Label(self.advanced_frame, text="🎼 Drag & Drop Background Music (optional)").pack(pady=10)
        self.adv_music_drop = tk.Text(self.advanced_frame, height=2, width=60)
        self.adv_music_drop.pack()
        self.adv_music_drop.drop_target_register(DND_FILES)
        self.adv_music_drop.dnd_bind("<<Drop>>", self.set_adv_music)

        ttk.Label(self.advanced_frame, text="🎚 Narration Speed (default 1.5)").pack(pady=5)
        self.narration_speed = tk.DoubleVar(value=1.5)
        tk.Entry(self.advanced_frame, textvariable=self.narration_speed).pack(pady=5)

        ttk.Label(self.advanced_frame, text="🎚 Background Music Speed (default 1.0)").pack(pady=5)
        self.music_speed = tk.DoubleVar(value=1.0)
        tk.Entry(self.advanced_frame, textvariable=self.music_speed).pack(pady=5)

        self.adv_start_btn = ttk.Button(self.advanced_frame, text="🚀 Start Advanced", command=self.start_process_advanced)
        self.adv_start_btn.pack(pady=20)

        ttk.Label(self.advanced_frame, text="Process Log:").pack(pady=5)
        self.adv_log_box = tk.Text(self.advanced_frame, height=10, width=70, state="disabled", wrap="word")
        self.adv_log_box.pack(pady=5)

    # ---------------- Log Helper ----------------
    def log(self, message, advanced=False):
        box = self.adv_log_box if advanced else self.log_box
        box.config(state="normal")
        box.insert(tk.END, message + "\n")
        box.see(tk.END)
        box.config(state="disabled")
        self.update_idletasks()

    # ---------------- File Handlers ----------------
    def set_text(self, event):
        self.text_file = event.data.strip("{}").strip()
        self.audio_drop.delete("1.0", tk.END)
        self.audio_drop.insert(tk.END, self.text_file)

    def set_video(self, event):
        self.video_file = event.data.strip("{}").strip()
        self.video_drop.delete("1.0", tk.END)
        self.video_drop.insert(tk.END, self.video_file)

    def set_music(self, event):
        self.bg_music_file = event.data.strip("{}").strip()
        self.music_drop.delete("1.0", tk.END)
        self.music_drop.insert(tk.END, self.bg_music_file)

    def set_adv_text_or_audio(self, event):
        path = event.data.strip("{}").strip()
        if path.lower().endswith(".mp3"):
            self.adv_narration_file = path
        else:
            self.adv_text_file = path
        self.adv_text_drop.delete("1.0", tk.END)
        self.adv_text_drop.insert(tk.END, path)

    def set_adv_video(self, event):
        self.adv_video_file = event.data.strip("{}").strip()
        self.adv_video_drop.delete("1.0", tk.END)
        self.adv_video_drop.insert(tk.END, self.adv_video_file)

    def set_adv_music(self, event):
        self.adv_music_file = event.data.strip("{}").strip()
        self.adv_music_drop.delete("1.0", tk.END)
        self.adv_music_drop.insert(tk.END, self.adv_music_file)

    # ---------------- Processes ----------------
    def start_process(self):
        if not self.text_file or not self.video_file:
            messagebox.showerror("Error", "You must select a text file and a video file!")
            return

        try:
            self.log("[1/5] Converting text to speech (gTTS)...")
            input_audio = text_to_speech(self.text_file, "intermediate/input_audio.mp3")

            self.log("[2/5] Speeding up audio...")
            fast_audio = speed_up_audio(input_audio, "intermediate/fast_input.mp3", factor=1.5)

            self.log("[3/5] Preparing video (TikTok format)...")
            tiktok_video = prepare_video(self.video_file, fast_audio, "intermediate/tiktok_video.mp4")

            self.log("[4/5] Transcribing audio...")
            ass_file = transcribe_and_chunk(fast_audio, "intermediate/output.ass", chunk_size=3)

            self.log("[5/5] Adding subtitles and background music...")
            final = burn_subtitles(tiktok_video, ass_file, bg_music=self.bg_music_file, output_path="video/final_tiktok.mp4")

            self.log(f"✅ Process complete! Output: {os.path.abspath(final)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log("❌ An error occurred.")

    def start_process_advanced(self):
        if (not self.adv_text_file and not self.adv_narration_file) or not self.adv_video_file:
            messagebox.showerror("Error", "You must select text/mp3 narration and a video file!")
            return

        try:
            self.log("[1/5] Obtaining the narration", advanced=True)
            input_audio = self.adv_narration_file or text_to_speech(self.adv_text_file, "intermediate/input_audio.mp3")

            self.log("[2/5] Adjusting narration speed...", advanced=True)
            fast_audio = speed_up_audio(input_audio, "intermediate/fast_input.mp3", factor=self.narration_speed.get())

            self.log("[3/5] Preparing video (TikTok format)...", advanced=True)
            tiktok_video = prepare_video(self.adv_video_file, fast_audio, "intermediate/tiktok_video.mp4")

            self.log("[4/5] Transcribing audio...", advanced=True)
            ass_file = transcribe_and_chunk(fast_audio, "intermediate/output.ass", chunk_size=3)

            self.log("[5/5] Adding subtitles and background music...", advanced=True)
            final = burn_subtitles(tiktok_video, ass_file, bg_music=self.adv_music_file, bg_speed=self.music_speed.get(), output_path="video/final_tiktok.mp4")

            self.log(f"✅ Process complete! Output: {os.path.abspath(final)}", advanced=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log("❌ An error occurred.", advanced=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()