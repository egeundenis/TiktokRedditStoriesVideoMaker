import os
import random
import subprocess
import whisper
from utils import get_video_duration, get_audio_duration, speed_up_audio

# Ensure intermediate and video folders exist
os.makedirs("intermediate", exist_ok=True)
os.makedirs("video", exist_ok=True)

def prepare_video(video_path, audio_path, output_path="intermediate/tiktok_video.mp4"):
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

def transcribe_and_chunk(audio_path, ass_path="intermediate/output.ass", chunk_size=3):
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

def burn_subtitles(video_path, ass_path, bg_music=None, bg_speed=1.0, output_path="video/final_tiktok.mp4"):
    if bg_music:
        # Adjust background music speed
        tmp_music = "intermediate/bg_temp.mp3"
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