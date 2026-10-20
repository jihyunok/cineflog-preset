# -*- coding: utf-8 -*-
"""벤치 한국어 받아쓰기 줄마다 「리뷰어 나레인가(원본 영어 대사를 한국어처럼 잘못 받아쓴 것 말고)」를 제브로 → jev_bn_out.jsonl
제브 스펙 _제브/벤치나레_가르기_영화.json (그레이하운드 전용 스펙을 영화 가리지 않게). 사용: python jev_bench.py"""
import json, os, subprocess
JEV = os.path.expanduser(r"~/volcano_work/_제브")
B = json.load(open("bench/asr_sm.json", encoding="utf-8"))["segments"]
with open("jev_bn_in.jsonl", "w", encoding="utf-8") as f:
    for i, s in enumerate(B):
        f.write(json.dumps({"id": f"b{i:03d}", "text": s["text"], "before": B[i - 1]["text"] if i else "", "after": B[i + 1]["text"] if i + 1 < len(B) else ""}, ensure_ascii=False) + "\n")
if os.path.exists("jev_bn_out.jsonl"): os.remove("jev_bn_out.jsonl")
subprocess.run(["py", "-3.12", rf"{JEV}\거르기.py", "--spec", rf"{JEV}\벤치나레_가르기_영화.json", "--in", "jev_bn_in.jsonl", "--out", "jev_bn_out.jsonl"], check=True)
A = [json.loads(l) for l in open("jev_bn_out.jsonl", encoding="utf-8")]
print("줄", len(A), "· 나레 0.7+", sum(a["answers"]["is_narration"] >= 0.7 for a in A), "· 0.5 안", sum(a["answers"]["is_narration"] < 0.5 for a in A))
