import json, random, subprocess, sys
sys.path.insert(0, '.')
from asr import asr
IT = [q for q in json.load(open("items.json", encoding="utf-8")) if q["type"] == "D" and q["ko"]]
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
for q in IT:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(q["s"]), "-t", str(q["d"]), "-i", "src.mp4", "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k", "c.mp3"], check=True)
    r = asr("c.mp3")
    print(q["i"], q["s"], q["d"], "|", q["ko"], "|", r["text"].strip())
