🎥 TRSVM (TikTok Reddit Stories Video Maker)

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

Before running the app, these are the required Python packages. They can be installed with pip:

tkinterdnd2 
whisper 
gTTS 
torch

System Requirements:

FFmpeg (must be installed and available in your PATH)

On Linux: sudo apt install ffmpeg

On macOS: brew install ffmpeg

On Windows: winget install ffmpeg
.

🚀 Usage

Clone the repository:

git clone https://github.com/egeundenis/TiktokRedditStoriesVideoMaker.git

cd TiktokRedditStoriesVideoMaker

... or you know, just download the .py file and put it in a directory lol

Install dependencies:

in terminal: 

pip tkinterdnd2 whisper gTTS torch

.... install ffmpeg

Run the app:

trsvm.py


Use the GUI:

📄 Drag & drop a .txt file containing your script.

🎬 Drag & drop a background video.

🎼 (Optional) Drag & drop a background music file.

🚀 Click Start to generate your TikTok video.

The final video will be saved as:

final_tiktok.mp4

Lots of other intermediate files will be created as well, if you want to use them!

📝 Example Workflow

Create a script.txt with your content: Basically, go to Reddit, r/nosleep or r/horrorrules, and take some stories there. Please credit them btw...

Add a stock video as background (background.mp4): Use https://amp4.cc/ and download some cool Minecraft parkour videos, better the quality... the better!

(Optional) Add background music (music.mp3). Again, use https://amp4.cc/ and download some chilling indie music. I personally love Fallen Down.

Run TRSVM, drag the files on their places, and press Start.

Wait and get your ready-to-post TikTok video! 🎉

⚡ Notes

Subtitles are styled with .ass (Advanced SubStation Alpha). You can edit the style in transcribe_and_chunk() if desired.

You can adjust audio speed in speed_up_audio() by changing the factor parameter.

The app uses Whisper’s base model by default. For faster/better results, replace "base" with "tiny", "small", "medium", or "large".

🛠 Troubleshooting

Error: ffmpeg not found
→ Make sure FFmpeg is installed and added to your PATH!

Torch not installed or GPU errors
→ Install PyTorch:

pip install torch torchvision torchaudio


See PyTorch installation guide
.

No audio output
→ Check your .txt file is not empty and the selected language is supported by gTTS!

📜 License

MIT License – free to use, modify, and distribute.
