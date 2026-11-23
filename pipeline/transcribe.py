#!/usr/bin/env python3
"""Транскрибация длинной записи кусками (faster-whisper). Вывод: [чч:мм:сс] текст."""
import argparse
import subprocess
import sys
import numpy as np


def load_audio(src: str) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-i", src, "-vn", "-f", "s16le",
         "-ac", "1", "-ar", "16000", "-af", "highpass=f=80", "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="аудио или видео файл")
    ap.add_argument("out", help="выходной .txt")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--lang", default="ru")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--compute-type", default="float16", help="float16 для GPU, int8 для CPU")
    ap.add_argument("--beam", type=int, default=10)
    ap.add_argument("--chunk", type=int, default=1200, help="длина куска, секунд")
    ap.add_argument("--prompt", default="", help="тема + 20-40 терминов предметной области")
    ap.add_argument("--done-marker", default="", help="путь файла-маркера, который создаётся в конце")
    a = ap.parse_args()

    from faster_whisper import WhisperModel

    audio = load_audio(a.src)
    tot = len(audio) / 16000.0
    print("audio ok", tot, flush=True)
    model = WhisperModel(a.model, device=a.device, compute_type=a.compute_type)

    pos = 0.0
    with open(a.out, "w", encoding="utf-8") as f:
        while pos < tot - 1:
            chunk = audio[int(pos * 16000):int((pos + a.chunk) * 16000)]
            fin = pos + a.chunk >= tot
            segs = list(model.transcribe(
                chunk, language=a.lang, beam_size=a.beam,
                initial_prompt=a.prompt or None,
                condition_on_previous_text=False,
                vad_filter=True,
                vad_parameters=dict(threshold=0.3, min_silence_duration_ms=1000, speech_pad_ms=400),
                temperature=[0.0, 0.2, 0.4],
                no_speech_threshold=0.5)[0])
            keep = segs if (fin or len(segs) < 2) else segs[:-1]
            for s in keep:
                t = int(pos + s.start)
                f.write("[%02d:%02d:%02d] %s\n" % (t // 3600, t // 60 % 60, t % 60, s.text.strip()))
            f.flush()
            pos = tot if fin else (pos + keep[-1].end if keep else pos + a.chunk)
            print("pos", round(pos), flush=True)

    if a.done_marker:
        open(a.done_marker, "w").write("1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
