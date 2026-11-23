#!/usr/bin/env python3
"""Вырезает строки-выдумки Whisper («Продолжение следует», «Субтитры сделал…») и показывает повторы подряд."""
import argparse
import re
import sys

TS = re.compile(r"^(\[\d{2}:\d{2}:\d{2}\])\s*(.*)$")

FULL_LINE = [
    r"продолжение следует",
    r"спасибо за (просмотр|внимание)( видео)?",
    r"спасибо что (досмотрели|смотрели)",
    r"до новых встреч",
    r"thank(s| you) for watching",
    r"thank you",
    r"thanks",
    r"большое спасибо за просмотр( видео)?",
]
SIGNATURE = [
    r"(редактор|корректор) субтитров.*",
    r"субтитры\s+(сделал|создал|делал|подготовил|добавил|предоставил)\w*.*",
    r"субтитры\s+.*(dimatorzok|amara).*",
    r"субтитры\s+и\s+чь[её]-то\s+(имя|ник)",
    r"subtitles?\s+by\b.*",
    r"amara\.org.*",
    r"dimatorzok.*",
    r"altyazı\b.*",
    r"titulky\s+vytvořil\b.*",
]
SIGNATURE_MAX_LEN = 90


def norm(text: str) -> str:
    t = text.strip().lower().replace("ё", "е")
    t = re.sub(r"^[\s\-–—«»\"'.,!?…:;()]+|[\s\-–—«»\"'.,!?…:;()]+$", "", t)
    return re.sub(r"\s+", " ", t)


def is_hallucination(text: str, extra: list[str]) -> bool:
    t = norm(text)
    if not t:
        return False
    for p in FULL_LINE:
        if re.fullmatch(p.replace("ё", "е"), t):
            return True
    if len(t) <= SIGNATURE_MAX_LEN:
        for p in SIGNATURE:
            if re.fullmatch(p, t):
                return True
    for e in extra:
        if norm(e) and norm(e) == t:
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("-o", "--out", help="куда записать очищенный текст")
    ap.add_argument("--extra", action="append", default=[], help="своя фраза целой строкой (можно несколько)")
    ap.add_argument("--repeat", type=int, default=3, help="сколько одинаковых строк подряд считать подозрительным")
    a = ap.parse_args()

    lines = open(a.src, encoding="utf-8").read().splitlines()
    kept, removed = [], []
    for ln in lines:
        m = TS.match(ln)
        ts, text = (m.group(1), m.group(2)) if m else ("", ln)
        if is_hallucination(text, a.extra):
            removed.append((ts, text))
        else:
            kept.append(ln)

    # повторы подряд (в уже очищенном тексте)
    reps, i = [], 0
    bodies = [norm(TS.sub(r"\2", l)) for l in kept]
    while i < len(kept):
        j = i
        while j + 1 < len(kept) and bodies[j + 1] == bodies[i] and bodies[i]:
            j += 1
        if j - i + 1 >= a.repeat:
            reps.append((TS.match(kept[i]).group(1) if TS.match(kept[i]) else "?", j - i + 1, bodies[i][:60]))
        i = j + 1

    print(f"строк всего: {len(lines)}, вырезано фраз-выдумок: {len(removed)}, осталось: {len(kept)}")
    for ts, text in removed:
        print(f"  вырезано {ts} {text}")
    if reps:
        print(f"подозрительные повторы (>= {a.repeat} подряд), НЕ удалены, проверить вручную:")
        for ts, n, body in reps:
            print(f"  {ts} x{n}: {body}")
    else:
        print("повторов подряд не найдено")

    if a.out:
        open(a.out, "w", encoding="utf-8").write("\n".join(kept) + "\n")
        print("записано:", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
