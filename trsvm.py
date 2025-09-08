import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import subprocess
import whisper
import os
from gtts import gTTS
import random
import json

# -------------------------------
# Functions
# -------------------------------
def text_to_speech(txt_file, output_audio="input_audio.mp3", lang="en"):
    with open(txt_file, "r", encoding="utf-8") as f:
        text = f.read()
    tts = gTTS(text=text, lang=lang)
    tts.save(output_audio)
    return output_audio

def speed_up_audio(input_audio, output_audio="fast_audio.mp3", factor=1.5):
    cmd = ["ffmpeg", "-y", "-i", input_audio, "-filter:a", f"atempo={factor}", output_audio]
    subprocess.run(cmd, check=True)
    return output_audio

def get_video_duration(video_path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", video_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])

def get_audio_duration(audio_path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", audio_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])

def prepare_video(video_path, audio_path, output_path="tiktok_video.mp4"):
    video_duration = get_video_duration(video_path)
    audio_duration = get_audio_duration(audio_path)
    max_start = max(0, video_duration - audio_duration)
    start_time = random.uniform(0, max_start) if max_start > 0 else 0

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-ss", str(start_time),
        "-i", video_path,
        "-i", audio_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path

def transcribe_and_chunk(audio_path, ass_path="output.ass", chunk_size=3):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, task="transcribe")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("""[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Centered,Impact,72,&H00FFFF&, &H000000&, &H000000&,1,0,1,4,2,5,50,50,50,0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")

        for seg in result["segments"]:
            words = seg["text"].strip().split()
            start, end = seg["start"], seg["end"]
            total_chunks = max(1, (len(words) + chunk_size - 1) // chunk_size)
            duration = (end - start) / total_chunks

            i = 0
            while i < len(words):
                chunk = " ".join(words[i:i+chunk_size])
                chunk_index = i // chunk_size
                chunk_start = start + chunk_index * duration
                chunk_end = chunk_start + duration

                def fmt(t):
                    h = int(t//3600)
                    m = int((t%3600)//60)
                    s = int(t%60)
                    cs = int((t%1)*100)
                    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"

                f.write(f"Dialogue: 0,{fmt(chunk_start)},{fmt(chunk_end)},Centered,,0,0,0,,{chunk}\n")
                i += chunk_size
    return ass_path

def burn_subtitles(video_path, ass_path, bg_music=None, bg_speed=1.0, output_path="final_tiktok.mp4"):
    if bg_music:
        # Adjust background music speed
        tmp_music = "bg_temp.mp3"
        if bg_speed != 1.0:
            speed_up_audio(bg_music, tmp_music, factor=bg_speed)
            bg_music = tmp_music

        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-stream_loop", "-1", "-i", bg_music,
            "-vf", f"ass={ass_path}",
            "-filter_complex", "[1:a]volume=0.25[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=3[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            output_path
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", f"ass={ass_path}",
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "128k",
            output_path
        ]
    subprocess.run(cmd, check=True)
    return output_path

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
            input_audio = text_to_speech(self.text_file, "input_audio.mp3")

            self.log("[2/5] Speeding up audio...")
            fast_audio = speed_up_audio(input_audio, "fast_input.mp3", factor=1.5)

            self.log("[3/5] Preparing video (TikTok format)...")
            tiktok_video = prepare_video(self.video_file, fast_audio, "tiktok_video.mp4")

            self.log("[4/5] Transcribing audio...")
            ass_file = transcribe_and_chunk(fast_audio, "output.ass", chunk_size=3)

            self.log("[5/5] Adding subtitles and background music...")
            final = burn_subtitles(tiktok_video, ass_file, bg_music=self.bg_music_file, output_path="final_tiktok.mp4")

            self.log(f"✅ Process complete! Output: {os.path.abspath(final)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log("❌ An error occurred.")

    def start_process_advanced(self):
        if (not self.adv_text_file and not self.adv_narration_file) or not self.adv_video_file:
            messagebox.showerror("Error", "You must select text/mp3 narration and a video file!")
            return

        try:
            if self.adv_narration_file:
                self.log("[1/5] Using custom narration MP3...", advanced=True)
                input_audio = self.adv_narration_file
            else:
                self.log("[1/5] Converting text to speech (gTTS)...", advanced=True)
                input_audio = text_to_speech(self.adv_text_file, "input_audio.mp3")

            self.log("[2/5] Adjusting narration speed...", advanced=True)
            fast_audio = speed_up_audio(input_audio, "fast_input.mp3", factor=self.narration_speed.get())

            self.log("[3/5] Preparing video (TikTok format)...", advanced=True)
            tiktok_video = prepare_video(self.adv_video_file, fast_audio, "tiktok_video.mp4")

            self.log("[4/5] Transcribing audio...", advanced=True)
            ass_file = transcribe_and_chunk(fast_audio, "output.ass", chunk_size=3)

            self.log("[5/5] Adding subtitles and background music...", advanced=True)
            final = burn_subtitles(tiktok_video, ass_file, bg_music=self.adv_music_file, bg_speed=self.music_speed.get(), output_path="final_tiktok.mp4")

            self.log(f"✅ Process complete! Output: {os.path.abspath(final)}", advanced=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log("❌ An error occurred.", advanced=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
