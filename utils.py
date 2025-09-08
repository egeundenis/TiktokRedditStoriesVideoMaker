import subprocess
import json
from gtts import gTTS

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