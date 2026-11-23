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

---

## Длинные записи (faster-whisper, Colab T4)

- `pipeline/transcribe.py` — `large-v3` кусками по 1200 с (весь файл сразу падает по памяти), VAD
- `pipeline/clean_hallucinations.py` — убирает «Продолжение следует», «Субтитры сделал…» и т.п.
- `tests/` — тесты чистилки: `python -m unittest discover -s tests`

```bash
pip install -q faster-whisper nvidia-cublas-cu12 nvidia-cudnn-cu12
python pipeline/transcribe.py lecture.mp4 out.txt --prompt "тема и термины"
python pipeline/clean_hallucinations.py out.txt -o out.clean.txt
```

### Проблема: Whisper выдумывает текст на тишине

На пустом окне (тишина, шум, музыка) Whisper пишет «Продолжение следует», «Субтитры сделал DimaTorzok», «Спасибо за просмотр»: так заканчивались видео в его обучающих данных. Датчик «речи нет» срабатывает, но кусок отбрасывается, только если текст ещё и неуверенный, а выдумка пишется уверенно.

Что сделано:
- VAD (`vad_filter=True`): в тишину и шум модель не попадает
- `condition_on_previous_text=False`: выдумка и повторы не тянутся дальше по тексту
- `clean_hallucinations.py`: вырезает известные подписи целой строкой, показывает повторы подряд

В коротком тесте (`small`, CPU, клип лекции + тишина + шум) VAD дал 0 вставок в тишину, без него была одна. Отключение проверки уверенности (`log_prob_threshold=None`) ничего не изменило. На `large-v3` не проверено.
