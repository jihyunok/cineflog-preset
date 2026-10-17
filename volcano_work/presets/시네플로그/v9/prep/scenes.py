# -*- coding: utf-8 -*-
"""장면 전환 시각 → scenes.txt (줄마다 초). 작업 폴더 ep.json 의 src. 사용: python scenes.py [문턱=0.28]"""
import json, re, subprocess, sys
CFG = json.load(open("ep.json", encoding="utf-8")); th = float(sys.argv[1]) if len(sys.argv) > 1 else 0.28
p = subprocess.run(["ffmpeg", "-v", "info", "-threads", "8", "-i", CFG["src"], "-an", "-vf", f"scale=480:-2,select='gt(scene,{th})',showinfo", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
ts = [float(x) for x in re.findall(r"pts_time:(\d+\.?\d*)", p.stderr)]
open("scenes.txt", "w").write("".join(f"{t:.6f}\n" for t in ts))
print("scenes.txt 전환", len(ts))
