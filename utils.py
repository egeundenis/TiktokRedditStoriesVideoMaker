import os
import subprocess
import json
from gtts import gTTS
from text_censor import default_censor

# Ensure intermediate and video folders exist
os.makedirs("intermediate", exist_ok=True)
os.makedirs("video", exist_ok=True)

def text_to_speech(txt_file, output_audio="intermediate/input_audio.mp3", lang="en"):
    with open(txt_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Apply censorship to the text
    censored_text = default_censor.censor_text(text)
    
    # Check if any words were censored and log if needed
    flagged_words = default_censor.find_flagged_words(text)
    if flagged_words:
        print(f"Censored words found: {', '.join(flagged_words)}")
    
    tts = gTTS(text=censored_text, lang=lang)
    tts.save(output_audio)
    return output_audio

def speed_up_audio(input_audio, output_audio="intermediate/fast_audio.mp3", factor=1.5):
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

def create_censored_text_file(input_file, output_file=None):
    """Create a censored version of a text file.
    
    Args:
        input_file: Path to original text file
        output_file: Path for censored file (optional, defaults to input_file with _censored suffix)
    
    Returns:
        Path to the censored file
    """
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_censored{ext}"
    
    with open(input_file, "r", encoding="utf-8") as f:
        original_text = f.read()
    
    # Apply censorship
    censored_text = default_censor.censor_text(original_text)
    
    # Write censored version
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(censored_text)
    
    # Log censored words if any
    flagged_words = default_censor.find_flagged_words(original_text)
    if flagged_words:
        print(f"Censored in {os.path.basename(input_file)}: {', '.join(flagged_words)}")
    
    return output_file