# 텔레그램으로 보낼 영상 준비 — 정치 롱폼 tools/tg_preview.py 사본(10-20 대작 텔레그램 "이거 완성되면 텔레그램 연결해서 보내줘")
# 텔레그램 봇은 파일 하나에 50MB까지라 그보다 크면(롱폼) 확인용으로 줄인 사본을 만든다. 원본은 건드리지 않는다.
# 사용: python -X utf8 tools/tg_preview.py <영상.mp4> [...]   → 보낼 파일 경로를 한 줄씩 출력
# 사본은 작업 폴더(지금 폴더) _tg/ 에 만든다. 너무 길면 화질이 떨어지지 않게 여러 개로 나눈다(26분 롱폼 = 2개).
import math, os, subprocess, sys, tempfile

OUT = os.path.join(os.getcwd(), "_tg")
LIMIT = 49 * 1024 * 1024          # 이 크기 이하면 원본 그대로 보냄
BUDGET = 46 * 1024 * 1024         # 줄인 사본 목표 크기(넘침 여유 3MB)
AUDIO = 128_000                    # 오디오 비트레이트(2026-10-15 64k → 128k: 사용자 "나레이션도 잡음이 심해" — 64k AAC 는 확인용 사본에서 쉬익 소리가 남)
MIN_TOTAL = 300_000                # 이보다 낮아지면 나눠서 보냄


def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True, check=True).stdout.strip())


def encode(src, dst, t0, t1, vbit):
    h = 720 if vbit >= 900_000 else 540 if vbit >= 450_000 else 480
    vf = f"scale=-2:{h}"
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "pass")
        base = ["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}", "-i", src, "-vf", vf,
                "-c:v", "libx264", "-preset", "medium", "-b:v", str(vbit), "-passlogfile", log]
        subprocess.run(base + ["-pass", "1", "-an", "-f", "null", os.devnull], check=True)
        subprocess.run(base + ["-pass", "2", "-c:a", "aac", "-b:a", str(AUDIO), "-ac", "2",
                               "-movflags", "+faststart", dst], check=True)
    return h


def prep(src):
    if os.path.getsize(src) <= LIMIT:
        return [src]
    os.makedirs(OUT, exist_ok=True)
    d = dur(src)
    parts = max(1, math.ceil(d * MIN_TOTAL / (BUDGET * 8)))
    seg = d / parts
    name = os.path.splitext(os.path.basename(src))[0]
    outs = []
    for i in range(parts):
        t0, t1 = i * seg, min(d, (i + 1) * seg)
        vbit = int(BUDGET * 8 / (t1 - t0) * 0.97) - AUDIO
        tag = "" if parts == 1 else f"_{i + 1}of{parts}"
        dst = os.path.join(OUT, f"{name}_텔레그램{tag}.mp4")
        h = encode(src, dst, t0, t1, vbit)
        size = os.path.getsize(dst)
        if size > LIMIT:
            sys.exit(f"[tg_preview] 50MB 넘음: {dst} {size / 1048576:.1f}MB")
        print(f"[tg_preview] {os.path.basename(dst)} {h}p {size / 1048576:.1f}MB", file=sys.stderr)
        outs.append(dst)
    return outs


if __name__ == "__main__":
    for p in sys.argv[1:]:
        for o in prep(os.path.abspath(p)):
            print(o)
