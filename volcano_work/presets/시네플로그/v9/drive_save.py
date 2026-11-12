# -*- coding: utf-8 -*-
"""완성된 영화 리뷰를 구글드라이브 영화리뷰/<NN_제목>/ 에 저장한다(11-02 사용자 "앞으로 만드는 영화리뷰를 이렇게 수정용으로까지 만들어주면 좋겠어 그리고이렇게 파일도 정리해주고").
  <NN_제목>/원본/                      원본 영화(같은 크기가 있으면 건너뜀)
  <NN_제목>/<시네플로그|무비세상>/      완성본·업로드 txt·썸네일 + <제목>_캡컷편집용/
캡컷편집용: 00_읽어주세요.txt · 01_영상_자막없음.mp4(나레 밑 줄인 원음+끝 음악) · 02_나레이션.wav · 03_자막_전체/나레/대사.srt · 04_워터마크.png
굽기(build_v9) 뒤 작업 폴더의 body.mkv·org.wav·narr_track.wav·subs.ass·fc.txt 로 만든다. 지우는 것 없음.
사용: python drive_save.py <작업 폴더> [--no-src] [--pack-only]"""
import ctypes, glob, json, os, re, shutil, subprocess, sys, tempfile, time

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
ROOT = "G:/내 드라이브/영화리뷰"
KEEP_C = 12e9   # 드라이브 앱이 C: 에 쌓았다 올리므로 이만큼은 남긴다
NARR = {"N", "NP", "NE"}
DLG = {"D", "DJ", "DY"}


def free_c():
    b = ctypes.c_ulonglong()
    ctypes.windll.kernel32.GetDiskFreeSpaceExW("C:\\", None, None, ctypes.byref(b))
    return b.value


def put(src, dst, move=False):
    """C: 여유를 보며 드라이브로. 같은 크기가 있으면 건너뜀."""
    size = os.path.getsize(src)
    if os.path.exists(dst) and os.path.getsize(dst) == size:
        print("이미 있음", os.path.basename(dst))
        if move:
            os.remove(src)
        return
    while free_c() < size + KEEP_C:
        print(f"C: 여유 {free_c() / 1e9:.0f}GB — 업로드 기다림 ({os.path.basename(dst)})")
        time.sleep(60)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    (shutil.move if move else shutil.copy2)(src, dst)
    print("저장", dst)


def clock(t, sep=","):
    h, m = int(t // 3600), int(t % 3600 // 60)
    return f"{h:02}:{m:02}:{t % 60:06.3f}".replace(".", sep)


def ass_rows(path):
    fmt = None
    rows = []
    for l in open(path, encoding="utf-8-sig"):
        if l.startswith("Format:") and "Text" in l:
            fmt = [x.strip() for x in l[7:].split(",")]
        if not l.startswith("Dialogue:") or not fmt:
            continue
        p = l[9:].rstrip("\n").split(",", len(fmt) - 1)
        d = dict(zip(fmt, [x.strip() if k != len(fmt) - 1 else x for k, x in enumerate(p)]))
        sec = lambda s: sum(float(x) * 60 ** i for i, x in enumerate(reversed(s.split(":"))))
        text = re.sub(r"\{[^}]*\}", "", d["Text"]).replace("\\N", "\n").replace("\\n", "\n").strip()
        if text:
            rows.append((sec(d["Start"]), sec(d["End"]), d["Style"], text))
    return sorted(rows, key=lambda r: r[0])


def write_srt(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, _, t) in enumerate(rows, 1):
            f.write(f"{i}\n{clock(a)} --> {clock(b)}\n{t}\n\n")


def fonts_used(ass, styles):
    out = {}
    for l in open(ass, encoding="utf-8-sig"):
        if l.startswith("Style:"):
            p = l[6:].split(",")
            out[p[0].strip()] = p[1].strip()
    return sorted({out[s] for s in styles if s in out})


def make_watermark(work, fc, tmp):
    """자막의 TOP 글자 → 투명 PNG. 투명 바탕에 바로 그리면 글자도 투명해지므로(11-02 33편) 검정·흰 바탕에 각각 그려 투명도를 계산한다."""
    import numpy as np
    from PIL import Image
    keep = [l for l in open(f"{work}/subs.ass", encoding="utf-8-sig") if not l.startswith("Dialogue") or ",TOP," in l]
    open(f"{tmp}/wm.ass", "w", encoding="utf-8").write("".join(keep))
    fonts = re.search(r"fontsdir=([^\[,]+)", fc)
    rel = os.path.basename(tmp)   # fontsdir 이 작업 폴더 기준 상대 경로라 작업 폴더에서 돌린다
    sub = f"subtitles={rel}/wm.ass" + (f":fontsdir={fonts.group(1).strip()}" if fonts else "")
    shot = {}
    for bg in ("black", "white"):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={bg}:s=1920x1080", "-vf", sub,
                        "-frames:v", "1", f"{rel}/wm_{bg}.png"], check=True, cwd=work)
        shot[bg] = np.asarray(Image.open(f"{tmp}/wm_{bg}.png").convert("RGB"), np.float32)
        os.remove(f"{tmp}/wm_{bg}.png")
    alpha = np.clip(255 - (shot["white"] - shot["black"]).mean(axis=2), 0, 255)
    if alpha.max() < 10:
        sys.exit("워터마크 글자가 안 그려짐 — 글꼴·TOP 줄 확인")
    rgb = np.clip(shot["black"] * 255 / np.maximum(alpha, 1)[..., None], 0, 255)
    Image.fromarray(np.dstack([rgb, alpha]).astype(np.uint8), "RGBA").save(f"{tmp}/04_워터마크.png")
    os.remove(f"{tmp}/wm.ass")


def make_pack(work, title, tmp):
    """자막 없는 영상은 굽기 때 쓴 fc.txt 에서 자막·워터마크만 뺀 그대로 — 그림이 완성본과 같다."""
    fc = open(f"{work}/fc.txt", encoding="utf-8").read()
    cfg = json.load(open(f"{work}/ep.json", encoding="utf-8"))
    video = re.search(r"\[0:v\](.*?)(?:,subtitles=)", fc, re.S).group(1)
    end = float(re.search(r"atrim=0:([\d.]+),(?:alimiter|volume)", fc).group(1))
    m_ = re.search(r"\[2:a\](.*?)\[mus\]", fc, re.S)
    if m_: mus_chain = m_.group(1)
    else:   # ★11-07 build_v9 새 섞기(고정 이득): 끝 음원을 mix.wav 에 미리 섞어 fc.txt 에 음원 줄이 없다 → build_v9 와 같은 규칙(마지막 나레 1초 앞부터 0.12·앞뒤 2초 페이드)으로 다시
        PL = json.load(open(f"{work}/narr_place.json", encoding="utf-8")); t_mus = PL[-1]["t"] - 1.0
        mus_chain = f"aresample=48000,atrim=0:{end - t_mus + 1:.2f},volume=0.12,afade=t=in:d=2,afade=t=out:st={end - t_mus - 2:.2f}:d=2,adelay={int(t_mus * 1000)}|{int(t_mus * 1000)}"
    music = os.path.expanduser(cfg.get("music") or "")   # ★11-12 「배경음은 넣지마」 — 없으면 무음 입력
    graph = f"[0:v]{video}[v];[2:a]{mus_chain}[mus];[1:a][mus]amix=inputs=2:normalize=0:duration=first,atrim=0:{end:.2f}[a]"
    gf = f"{tmp}/fc_pack.txt"
    open(gf, "w", encoding="utf-8").write(graph)
    v = f"{tmp}/01_영상_자막없음.mp4"
    print("자막 없는 영상 굽기…")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{work}/body.mkv", "-i", f"{work}/org.wav", *(["-i", music] if os.path.exists(music) else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]), "-/filter_complex", gf,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", v], check=True)
    shutil.copy2(f"{work}/narr_track.wav", f"{tmp}/02_나레이션.wav")
    rows = [r for r in ass_rows(f"{work}/subs.ass") if r[2] != "TOP" and r[2] != "TAG"]
    write_srt(f"{tmp}/03_자막_전체.srt", rows)
    write_srt(f"{tmp}/03_자막_나레.srt", [r for r in rows if r[2] in NARR])
    write_srt(f"{tmp}/03_자막_대사.srt", [r for r in rows if r[2] in DLG])
    other = sorted({r[2] for r in rows} - NARR - DLG)
    # 04 워터마크: 전용 그림이 있으면 그것, 없으면 자막의 TOP 글자를 투명 바탕에
    wm = cfg.get("brand_png")
    wm = wm if wm and os.path.isabs(wm) else (os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "brand", wm) if wm else None)
    if wm and os.path.exists(wm):
        shutil.copy2(wm, f"{tmp}/04_워터마크.png")
    else:
        make_watermark(work, fc, tmp)
    os.remove(gf)
    mm, ss = int(end // 60), end % 60
    guide = (f"캡컷에서 새 프로젝트(1920x1080 · 30fps)를 만들고 아래 순서로 0초에 맞춰 올리면 완성본과 같아집니다.\n\n"
             f"1. 01_영상_자막없음.mp4   메인 트랙 (나레 밑 원음은 이미 낮췄고 끝 음악까지 들어 있음)\n"
             f"2. 02_나레이션.wav        오디오 트랙 — 0초에 놓기\n"
             f"3. 03_자막_전체.srt       텍스트 > 자막 가져오기 (나레·대사를 따로 고치려면 _나레 / _대사 파일)\n"
             f"   나레 글꼴 {', '.join(fonts_used(work + '/subs.ass', NARR))} / 대사 글꼴 {', '.join(fonts_used(work + '/subs.ass', DLG))}\n"
             f"4. 04_워터마크.png        맨 위 트랙, 0초부터 끝({mm}:{ss:05.2f})까지 늘리기\n\n"
             f"완성본 음량은 -16 LUFS 입니다. 수정 후 내보낼 때 음량을 다시 맞추세요.\n"
             f"영상 그림 자체는 완성본과 같습니다(화질 값만 다름).\n")
    if other:
        guide += f"나레·대사로 나누지 않은 자막 묶음({', '.join(other)})은 _전체 파일에만 있습니다.\n"
    open(f"{tmp}/00_읽어주세요.txt", "w", encoding="utf-8").write(guide)
    print(f"자막 전체 {len(rows)}줄 · 나레 {sum(r[2] in NARR for r in rows)} · 대사 {sum(r[2] in DLG for r in rows)} · 기타 {other}")


def main():
    work = sys.argv[1].rstrip("/\\").replace("\\", "/")
    m = re.match(r"ep(\d+)(b|v\d+)?_(.+)", os.path.basename(work))
    if not m:
        sys.exit("작업 폴더 이름이 epNN_제목 꼴이 아님: " + work)
    num, kind, title = m.groups()
    name = f"{num}_{title}"
    channel = "무비세상" if kind == "b" else "시네플로그"
    VER = bool(kind and kind.startswith("v"))
    out = os.path.expanduser("~/volcano_work/시네플로그/완성본") + ("/무비세상" if kind == "b" else "")
    dest = f"{ROOT}/{name}/{channel}"
    if "--pack-only" not in sys.argv:
        # ★11-07 다시 만든 판(epNNv2_제목)은 옛 파일을 덮지 않게 「NN_제목_v2…」 파일만, 캡컷편집용도 「제목_캡컷편집용_v2」 로(사용자 「지금다시만들어」 — 옛 완성본 그대로)
        files = [f for f in os.listdir(out) if (f.startswith(f"{name}_{kind}") if VER else f.startswith(name)) and os.path.isfile(f"{out}/{f}") and not f.endswith("_캡컷")]
        for f in files:
            put(f"{out}/{f}", f"{dest}/{f}")
        if "--no-src" not in sys.argv:
            cfg = json.load(open(f"{work}/ep.json", encoding="utf-8"))
            base = cfg.get("b_from") or work
            cands = glob.glob(f"{base}/orig.*") + glob.glob(f"{base}/src_full.*") + [cfg.get("src") or f"{base}/src.mp4"]
            src = next((c for c in cands if c.lower().endswith((".mp4", ".mkv", ".avi")) and os.path.exists(c)), None)
            have = glob.glob(f"{ROOT}/{name}/원본/*")
            if have:
                print("원본 이미 있음")
            elif src:
                put(src, f"{ROOT}/{name}/원본/{title}_원본{os.path.splitext(src)[1].lower()}")
            else:
                print("★원본 못 찾음")
    tmp = tempfile.mkdtemp(prefix="_pack_", dir=work)
    make_pack(work, title, tmp)
    for f in sorted(os.listdir(tmp)):
        put(f"{tmp}/{f}", f"{dest}/{title}_캡컷편집용" + (f"_{kind}" if VER else "") + f"/{f}", move=True)
    os.rmdir(tmp)
    print("끝", dest)


if __name__ == "__main__":
    main()
