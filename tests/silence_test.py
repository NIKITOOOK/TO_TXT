"""Тест выдумок на тишине: клип речи + тишина + шум, 4 набора настроек.
python tests/silence_test.py lecture.mp4 --model large-v3 --start 1500 --device cuda --compute-type float16"""
import argparse, subprocess, time
import numpy as np
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("--model", default="large-v3")
ap.add_argument("--start", type=int, default=1500, help="с какой секунды брать речь")
ap.add_argument("--device", default="cuda")
ap.add_argument("--compute-type", default="float16")
a = ap.parse_args()

raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(a.start), "-t", "150", "-i", a.src,
                      "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
sp = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
sr = 16000
noise = (np.random.default_rng(0).standard_normal(35 * sr) * 0.002).astype(np.float32)
audio = np.concatenate([sp[:90 * sr], np.zeros(35 * sr, np.float32), sp[90 * sr:120 * sr], noise])
quiet = [(89, 125), (154, 190)]  # где речи нет

vad = dict(vad_filter=True, vad_parameters=dict(threshold=0.3, min_silence_duration_ms=1000, speech_pad_ms=400))
cfgs = {
    "1 по умолчанию": {},
    "2 vad, без подсказки": dict(**vad, condition_on_previous_text=False, no_speech_threshold=0.5, temperature=[0.0, 0.2, 0.4]),
    "3 без vad, log_prob_threshold=None": dict(log_prob_threshold=None, no_speech_threshold=0.6, condition_on_previous_text=False),
    "4 vad + log_prob_threshold=None": dict(**vad, log_prob_threshold=None, no_speech_threshold=0.6, condition_on_previous_text=False),
}
m = WhisperModel(a.model, device=a.device, compute_type=a.compute_type)
for name, k in cfgs.items():
    t = time.time()
    segs = list(m.transcribe(audio, language="ru", beam_size=5, **k)[0])
    bad = [s for s in segs if any(l <= s.start < h for l, h in quiet)]
    chars = sum(len(s.text) for s in segs if s not in bad)
    print(f"{name}: вставок в тишине {len(bad)}, символов речи {chars}, {time.time() - t:.0f} с")
    for s in bad:
        print(f"   [{s.start:.0f}] {s.text.strip()}")
