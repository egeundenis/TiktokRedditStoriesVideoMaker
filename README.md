🎥 TRSVM (TikTok Reddit Story Videos Maker)

TRSVM allows you to automatically generate TikTok-ready videos from a text file.
It takes text input, converts it to speech, synchronizes it with a background video, transcribes the audio into subtitles, and (optionally) mixes background music. The result is a vertical 1080x1920 video optimized for TikTok.

✨ Features

📝 Text-to-Speech (TTS) using gTTS
🎙️ Audio Speed Control with FFmpeg
🎬 Background Video Processing in TikTok format (1080x1920, 30fps)
💬 Automatic Subtitles with OpenAI Whisper
🎼 Background Music Mixing (optional)
🖥️ Drag & Drop GUI built with Tkinter

📦 Dependencies

Before running the app, install the required Python packages manually:

pip install tkinterdnd2 whisper gTTS torch

⚠️ tkinter is included with most Python installations (except minimal builds).
If missing, install via your system’s package manager.

System Requirements

FFmpeg (must be installed and available in your PATH)

Download FFmpeg

On Linux:

sudo apt install ffmpeg


On macOS:

brew install ffmpeg


On Windows:

winget install ffmpeg
.

🚀 Usage

Clone the repository:

git clone https://github.com/yourusername/trsvm.git
cd trsvm


Install dependencies manually as shown above.

Run the app:

python app.py


Use the GUI:

📄 Drag & drop a .txt file containing your script.

🎬 Drag & drop a background video.

🎼 (Optional) Drag & drop a background music file.

🚀 Click Start to generate your TikTok video.

The final video will be saved as:

final_tiktok.mp4

📝 Example Workflow

Create a script.txt with your content:

Did you know?
Honey never spoils.
Archaeologists found 3000-year-old honey in Egypt that was still edible!


Add a stock video as background (background.mp4).

(Optional) Add background music (music.mp3).

Run TRSVM, drag the files, and press Start.

Get your ready-to-post TikTok video! 🎉

⚡ Notes

Subtitles are styled with .ass (Advanced SubStation Alpha). You can edit the style in transcribe_and_chunk() if desired.

You can adjust audio speed in speed_up_audio() by changing the factor parameter.

The app uses Whisper’s base model by default. For faster/better results, replace "base" with "tiny", "small", "medium", or "large".

🛠 Troubleshooting

Error: ffmpeg not found
→ Make sure FFmpeg is installed and added to your PATH.

Torch not installed or GPU errors
→ Install PyTorch:

pip install torch torchvision torchaudio


See PyTorch installation guide
.

No audio output
→ Check your .txt file is not empty and the selected language is supported by gTTS.

📜 License

MIT License – free to use, modify, and distribute.
