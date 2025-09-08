TRSVM (TikTok Reddit Stories Video Maker)

TRSVM is a tool that helps you automatically create TikTok-ready videos from a text file. It converts text to speech, synchronizes it with a background video, generates subtitles, and optionally mixes background music. The final output is a vertical 1080x1920 video optimized for TikTok.

Features:

Text-to-Speech (TTS) using gTTS
Audio speed adjustment with FFmpeg
Background video formatting for TikTok (1080x1920, 30fps)
Automatic subtitle generation using OpenAI Whisper
Optional background music mixing
Drag-and-drop GUI built with Tkinter
Dependencies: You need the following Python packages, which can be installed with pip:

tkinterdnd2
whisper
gTTS
torch
You also need FFmpeg installed and added to your system PATH:

On Linux: sudo apt install ffmpeg
On macOS: brew install ffmpeg
On Windows: winget install ffmpeg
How to Use:

Clone the repository: git clone https://github.com/egeundenis/TiktokRedditStoriesVideoMaker.git cd TiktokRedditStoriesVideoMaker

Alternatively, download the trsvm.py file and place it in a directory.

Install dependencies: pip install tkinterdnd2 whisper gTTS torch

Run the app: python trsvm.py

Use the GUI:

Drag and drop a .txt file containing your script.
Drag and drop a background video.
(Optional) Drag and drop a background music file.
Click "Start" to generate your TikTok video.
The final video will be saved as final_tiktok.mp4. Intermediate files will also be created if you want to use them.

Example Workflow:

Create a script.txt file with your content. For example, find a story on Reddit (e.g., r/nosleep) and credit the author.
Add a stock video as the background (e.g., Minecraft parkour). You can download videos from websites like amp4.cc.
(Optional) Add background music (e.g., indie tracks). Again, amp4.cc is a good source.
Run TRSVM, drag and drop the files into their respective fields, and click "Start."
Wait for the process to complete and get your ready-to-post TikTok video!