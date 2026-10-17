# -*- coding: utf-8 -*-
"""썸네일 보기를 완성본 폴더 영상 옆에 넣는다 — 10-17 사용자 "잘만들었어 그런데 섬네일은 왜 같은 파일안에 안넣니 찾기힘들어".
보기를 작업 폴더(D:/cine_work/…)에만 두면 사용자가 못 찾는다. 보기를 만들면 바로 이걸 돌려 완성본/ 에 영상과 같은 이름 앞머리로 넣는다.
사용:
  python thumb_deliver.py <보기 폴더> <NN_제목> [한눈에 시트.jpg]   (시트를 안 주면 A·B… 글자를 붙인 시트를 새로 만든다)
     보기 폴더의 A.jpg·B.jpg…(png 도) 와 보기.txt(줄마다 「A … 「문구」 …」)를 읽어
     완성본/NN_제목_썸네일보기_A_문구.jpg … 로 복사, 시트는 NN_제목_썸네일보기_한눈에.jpg.
  python thumb_deliver.py --pick <NN_제목> A [B]
     사용자가 고르면 고른 보기를 NN_제목_썸네일1(·2).jpg 로 복사하고, 남은 보기는 완성본/_옛/썸네일보기/ 로 옮긴다(지우지 않음).
     이미 있는 _썸네일1·2.jpg 는 _옛/ 에 날짜 붙여 옮긴 뒤 넣는다."""
import datetime, glob, os, re, shutil, sys

OUT = os.environ.get("THUMB_OUT") or os.path.expanduser("~/volcano_work/시네플로그/완성본")   # THUMB_OUT = 시험용
OLD = f"{OUT}/_옛"
STAMP = datetime.date.today().strftime("%m%d")


def labels(d):
    p = f"{d}/보기.txt"; lab = {}
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            m = re.match(r"\s*([A-Z])\s", l); q = re.search(r"「([^」]+)」", l)
            if m and q: lab[m.group(1)] = re.sub(r'[\\/:*?"<>|!.,\s]+', "", q.group(1))
    return lab


def deliver(d, name, sheet=None):
    lab = labels(d); n = 0
    for f in sorted(glob.glob(f"{d}/[A-Z].jpg") + glob.glob(f"{d}/[A-Z].png")):
        k, ext = os.path.splitext(os.path.basename(f))
        dst = f"{OUT}/{name}_썸네일보기_{k}" + (f"_{lab[k]}" if k in lab else "") + ext
        shutil.copy2(f, dst); print("→", os.path.basename(dst)); n += 1
    if not n: raise SystemExit(f"보기 그림이 없다: {d}/A.jpg …")
    dst = f"{OUT}/{name}_썸네일보기_한눈에.jpg"
    if sheet: shutil.copy2(sheet, dst)
    else: make_sheet(d, dst)
    print("→", os.path.basename(dst))


def make_sheet(d, dst, cw=640, ch=360, per=3):
    """보기마다 왼쪽 위에 노란 칸 A·B… 를 붙인 한눈에 시트(한 줄 3장, 마지막 줄은 가운데)."""
    from PIL import Image, ImageDraw, ImageFont
    fs = sorted(glob.glob(f"{d}/[A-Z].jpg") + glob.glob(f"{d}/[A-Z].png")); rows = (len(fs) + per - 1) // per
    sh = Image.new("RGB", (cw * per, ch * rows), (24, 24, 24)); f = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 44)
    for i, p in enumerate(fs):
        r, c = divmod(i, per); left = len(fs) - r * per
        x = c * cw + (cw * (per - left) // 2 if left < per else 0)
        sh.paste(Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS), (x, r * ch))
        dr = ImageDraw.Draw(sh); dr.rectangle((x + 8, r * ch + 8, x + 60, r * ch + 62), fill=(255, 220, 0))
        dr.text((x + 34, r * ch + 35), os.path.splitext(os.path.basename(p))[0], font=f, fill=(0, 0, 0), anchor="mm")
    sh.save(dst, quality=92)


def pick(name, keys):
    views = sorted(glob.glob(f"{OUT}/{name}_썸네일보기_*"))
    if not views: raise SystemExit(f"완성본에 {name}_썸네일보기_* 가 없다")
    os.makedirs(f"{OLD}/썸네일보기", exist_ok=True)
    for i, k in enumerate(keys, 1):
        src = next((v for v in views if re.search(rf"_썸네일보기_{k}(_|\.)", v)), None)
        if not src: raise SystemExit(f"보기 {k} 가 없다")
        dst = f"{OUT}/{name}_썸네일{i}.jpg"
        if os.path.exists(dst): shutil.move(dst, f"{OLD}/{name}_썸네일{i}_{STAMP}전.jpg")
        shutil.copy2(src, dst); print(k, "→", os.path.basename(dst))
    for v in views: shutil.move(v, f"{OLD}/썸네일보기/{os.path.basename(v)}")
    print("남은 보기", len(views), "장 → _옛/썸네일보기/")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "--pick": pick(sys.argv[2], sys.argv[3:])
    else: deliver(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
