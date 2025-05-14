# Video to Text: Audio Transcription with Whisper

Automatically convert video audio tracks into text transcripts using OpenAI's Whisper speech recognition model.

## 📝 Description
This project provides a simple pipeline to extract audio from video files and transcribe it into text using state-of-the-art speech recognition technology. Perfect for:
- Creating video subtitles
- Content analysis
- Lecture/podcast transcription
- Media accessibility

## ✨ Features
- 🎥 Audio extraction from video (supports MP4, AVI, MOV etc.)
- 🔊 Automatic transcription using Whisper (base model)
- 📄 UTF-8 text output
- ⚡ Easy Python integration
- 🏷️ Supports multiple Whisper model sizes

## ⚙️ Installation
1. Ensure Python 3.7+ is installed
2. Install dependencies:
```bash
pip install openai-whisper moviepy
```
3. Install ![FFmpeg][https://ffmpeg.org/] (required for media processing) 


🚀 Usage
1. Place your video file in the project directory
2. Update the file path in the code:
```
video_path = "your_video.mp4"
```
3. Run the script:
```
python video_to_text.py
```
4. Find your transcript in transcript.txt

## Available Whisper Models

| Model   | Parameters | Disk Size | RAM Usage | Relative Speed | Languages | Best For                   |
|---------|------------|-----------|-----------|----------------|------------|----------------------------|
| tiny    | 39M        | ~75MB     | ~1GB      | 32x            | English    | Quick tests, low-resource   |
| base    | 74M        | ~140MB    | ~1.5GB    | 16x            | English    | Balanced speed/accuracy    |
| small   | 244M       | ~460MB    | ~2GB      | 6x             | English    | Better accuracy            |
| medium  | 769M       | ~1.5GB    | ~5GB      | 2x             | English    | High accuracy              |
| large   | 1550M      | ~3GB      | ~10GB     | 1x             | Multilingual | Professional transcription |
| large-v2| 1550M      | ~3GB      | ~10GB     | 1x             | Multilingual | Latest best accuracy       |

### Key:
- **Relative Speed**: Compared to large model (lower is faster)
- **RAM Usage**: Approximate during transcription
- **Disk Size**: Storage space needed for model
- **Languages**: "Multilingual" supports 99 languages


Advanced Options
Specify Language
```
result = model.transcribe("audio.wav", language="ru")
```
Temperature Control
```
result = model.transcribe("audio.wav", temperature=0.2)
```
Word-level Timestamps
```
result = model.transcribe("audio.wav", word_timestamps=True)
```
Performance Tips
* For English transcription, use English-only models (add english=True to load_model)
* On low-RAM systems, use smaller models (tiny/base)
* For long videos (>30 mins), consider splitting into chunks

Troubleshooting
Problem: FFmpeg not found
Solution: Install FFmpeg and ensure it's in your PATH

Problem: CUDA out of memory
Solution: Use a smaller model or split audio into chunks
