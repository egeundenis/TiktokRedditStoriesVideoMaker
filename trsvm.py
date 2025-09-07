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
    """Get duration (in seconds) of a video using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json", video_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])

def get_audio_duration(audio_path):
    """Get duration (in seconds) of an audio file using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json", audio_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])

def prepare_video(video_path, audio_path, output_path="tiktok_video.mp4"):
    # Get durations
    video_duration = get_video_duration(video_path)
    audio_duration = get_audio_duration(audio_path)

    # Ensure we have enough video to match audio
    max_start = max(0, video_duration - audio_duration)
    start_time = random.uniform(0, max_start)

    # FFmpeg command with -ss (seek) before -i
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),  # random start time
        "-i", video_path,
        "-i", audio_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
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

def burn_subtitles(video_path, ass_path, bg_music=None, output_path="final_tiktok.mp4"):
    if bg_music:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", bg_music,
            "-vf", f"ass={ass_path}",
            "-filter_complex", "[1:a]volume=0.25[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=3[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
            output_path
        ]
    else:
        cmd = ["ffmpeg", "-y", "-i", video_path, "-vf", f"ass={ass_path}", "-c:v", "libx264", "-c:a", "aac", "-b:a", "128k", output_path]
    subprocess.run(cmd, check=True)
    return output_path

# -------------------------------
# GUI
# -------------------------------
class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("TikTok Video Maker")
        self.geometry("600x600")

        self.text_file = None
        self.video_file = None
        self.bg_music_file = None

        ttk.Label(self, text="📄 Drag & Drop Text File (.txt)", font=("Arial", 12)).pack(pady=10)
        self.audio_drop = tk.Text(self, height=2, width=60)
        self.audio_drop.pack()
        self.audio_drop.drop_target_register(DND_FILES)
        self.audio_drop.dnd_bind("<<Drop>>", self.set_text)

        ttk.Label(self, text="🎬 Drag & Drop Background Video", font=("Arial", 12)).pack(pady=10)
        self.video_drop = tk.Text(self, height=2, width=60)
        self.video_drop.pack()
        self.video_drop.drop_target_register(DND_FILES)
        self.video_drop.dnd_bind("<<Drop>>", self.set_video)

        ttk.Label(self, text="🎼 Drag & Drop Background Music (optional)", font=("Arial", 12)).pack(pady=10)
        self.music_drop = tk.Text(self, height=2, width=60)
        self.music_drop.pack()
        self.music_drop.drop_target_register(DND_FILES)
        self.music_drop.dnd_bind("<<Drop>>", self.set_music)

        self.start_btn = ttk.Button(self, text="🚀 Start", command=self.start_process)
        self.start_btn.pack(pady=20)

        ttk.Label(self, text="Process Log:", font=("Arial", 10, "bold")).pack(pady=5)
        self.log_box = tk.Text(self, height=10, width=70, state="disabled", wrap="word")
        self.log_box.pack(pady=5)

    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")
        self.update_idletasks()

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

if __name__ == "__main__":
    app = App()
    app.mainloop()
