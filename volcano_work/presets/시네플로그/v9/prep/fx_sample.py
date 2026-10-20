# -*- coding: utf-8 -*-
"""build_v9.py 의 조각 자르기(cut)를 그대로 불러 30초 견본(지금 효과 끔 / 새 효과)과 나란히 비교본을 굽는다. 10-19 줌 움직임·그레인 견본. 사용: python fx_sample.py <출력폴더> <원본>"""
import json, os, subprocess, sys
P = os.path.expanduser("~/volcano_work/presets/시네플로그/v9/build_v9.py")
OUT, SRC = sys.argv[1], sys.argv[2]
TIMES = [420, 1080, 1740, 2400, 3060, 3720, 4380, 5040, 5700, 6360]
code = open(P, encoding="utf-8").read().split('if MODE == "cut":')[0]
res = {}
for name, fx in (("지금", False), ("새효과", True)):
    d = os.path.join(OUT, "_" + name); os.makedirs(d, exist_ok=True); os.chdir(d)
    json.dump({"src": SRC, "h": 1080, "burn": [860, 220, 360, 1200], "fx": fx}, open("ep.json", "w", encoding="utf-8"))
    wn, t = [], 0.0
    for s in TIMES: wn.append({"kind": "A", "s": s, "a": t, "b": t + 2.9}); t += 2.9
    json.dump(wn, open("windows.json", "w", encoding="utf-8"))
    sys.argv = [P, "cut"]; ns = {"__file__": P, "__name__": "fx_sample"}
    exec(compile(code, P, "exec"), ns)
    ps = [ns["cut"](k) for k in range(len(wn))]
    open("all.txt", "w", encoding="utf-8").write("".join(f"file '{p}'\n" for p in ps))
    res[name] = os.path.join(OUT, f"견본_{name}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "all.txt", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-c:a", "aac", "-b:a", "192k", res[name]], check=True)
os.chdir(OUT)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", res["지금"], "-i", res["새효과"], "-filter_complex",
                "[0:v]scale=960:540,drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='NOW':x=20:y=20:fontsize=36:fontcolor=white:box=1:boxcolor=black@0.6[l];"
                "[1:v]scale=960:540,drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='NEW FX':x=20:y=20:fontsize=36:fontcolor=white:box=1:boxcolor=black@0.6[r];[l][r]hstack[v]",
                "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", os.path.join(OUT, "견본_비교_왼쪽지금_오른쪽새효과.mp4")], check=True)
print("끝:", *res.values())
