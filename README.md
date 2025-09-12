# TikTok Video Maker

A comprehensive Python application for creating TikTok-ready videos from text scripts with automated speech synthesis, subtitle generation, and video processing. Features three distinct modes: Simple, Advanced, and Bulk Production.

## Features

### Core Functionality
- **Text-to-Speech**: Converts text files to natural speech using Google Text-to-Speech (gTTS)
- **Content Censorship**: Automatically replaces potentially flagged words with platform-friendly alternatives
- **Video Processing**: Formats videos to TikTok specifications (1080x1920, 30fps) or preserves original format for YouTube
- **YouTube Mode**: Automatically preserves original video format for videos longer than 3 minutes
- **Subtitle Generation**: Creates synchronized subtitles using OpenAI Whisper transcription
- **Audio Processing**: Speed adjustment and background music mixing
- **Drag & Drop Interface**: User-friendly GUI built with Tkinter

### Operating Modes

#### 1. Simple Mode
Basic video creation with minimal configuration:
- Text file input
- Background video
- Optional background music
- YouTube Mode toggle for longer videos
- One-click processing

#### 2. Advanced Mode
Full control over video parameters:
- Custom narration speed adjustment
- Background music speed control
- Subtitle customization (frequency, font, size, color)
- Support for pre-recorded MP3 narration
- YouTube Mode toggle for longer videos

#### 3. Bulk Production Mode
Automated batch processing:
- Process multiple text files simultaneously
- Random video and music selection
- YouTube Mode toggle for longer videos
- Comprehensive logging system
- Performance metrics tracking

## Installation

### Prerequisites
- Python 3.7+
- FFmpeg (must be in system PATH)

### System Dependencies

**Windows:**
```cmd
winget install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

### Python Dependencies
```bash
pip install tkinterdnd2 openai-whisper gtts torch
```

## Usage

### Quick Start
1. Run the application:
   ```bash
   python main.py
   ```

2. Choose your mode (Simple/Advanced/Bulk Production)

3. Drag and drop your files into the designated areas

4. Click "Start" to begin processing

### File Structure
The application creates the following directories:
- `intermediate/` - Temporary processing files
- `video/` - Final output videos
- `logs/` - Processing logs (bulk mode only)

### Content Censorship
The application automatically censors potentially problematic words to improve platform compatibility:
- Violence-related terms → "unalive" variations
- Profanity → Mild alternatives
- Sensitive content → Platform-friendly replacements

## Advanced Configuration

### YouTube Mode
YouTube Mode is automatically enabled when:
- The YouTube Mode checkbox is selected in any mode
- The processed audio (after speed adjustment) is longer than 3 minutes

When YouTube Mode is active:
- Original video dimensions and aspect ratio are preserved
- Frame rate remains unchanged from source video
- Subtitles are positioned appropriately for horizontal formats
- Output filename includes "youtube" for easy identification

This ensures videos longer than 3 minutes maintain their original format for better YouTube compatibility, while shorter videos can still be optimized for TikTok's vertical format.

### Subtitle Customization
- **Frequency**: Words per subtitle chunk (1-10)
- **Font**: Any system font (default: Impact)
- **Size**: Font size in pixels (default: 72)
- **Color**: Hex color code (default: #00FFFF)

### Speed Controls
- **Narration Speed**: 0.5x to 3.0x (default: 1.5x)
- **Music Speed**: 0.5x to 2.0x (default: 1.0x)

### Bulk Production
For processing multiple videos:
1. Organize text files in one directory
2. Place background videos in another directory
3. (Optional) Add background music to a third directory
4. The system will randomly pair files for variety

## Technical Details

### Video Processing Pipeline
1. **Text Processing**: Censorship and TTS conversion
2. **Audio Enhancement**: Speed adjustment and optimization
3. **Video Preparation**: Format conversion and cropping
4. **Transcription**: Whisper-based subtitle generation
5. **Final Assembly**: Subtitle burning and audio mixing

### Performance Features
- Automatic video duration matching
- Random start time selection for background videos
- Optimized encoding settings for TikTok
- Comprehensive error handling and logging

## File Formats

### Supported Input Formats
- **Text**: .txt files (UTF-8 encoding)
- **Video**: Most common formats (MP4, AVI, MOV, etc.)
- **Audio**: MP3, WAV, M4A for background music
- **Narration**: MP3 files for pre-recorded audio

### Output Format
- **TikTok Mode**: MP4 (H.264, 1080x1920, 30fps)
- **YouTube Mode**: MP4 (H.264, preserves original dimensions and framerate)
- **Audio**: AAC, 192kbps (128kbps without background music)

## Troubleshooting

### Common Issues
- **FFmpeg not found**: Ensure FFmpeg is installed and in system PATH
- **Whisper model download**: First run downloads the transcription model
- **Memory issues**: Large video files may require more RAM
- **Audio sync problems**: Check input audio quality and format

### Log Files
Bulk production mode creates detailed logs in the `logs/` directory with:
- Processing timestamps
- Performance metrics
- Error details
- Success/failure statistics

## Contributing

The codebase is modular with clear separation of concerns:
- `main.py` - GUI and application logic
- `utils.py` - Core utility functions
- `video_processor.py` - Video processing pipeline
- `text_censor.py` - Content filtering system
- `logger_manager.py` - Logging and monitoring

## License

This project is open source. Please ensure you have proper rights to any content you process and comply with platform guidelines when uploading generated videos.