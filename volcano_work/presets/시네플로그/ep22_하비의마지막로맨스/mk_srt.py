# -*- coding: utf-8 -*-
# 하비 영어 대사 → 한국어 자막(srt.txt: id\ts\te\tko) — agy 로 250줄씩, 3개 동시
import json, subprocess, sys, os, re, concurrent.futures as cf
W = "D:/cine_work/ep22_하비의마지막로맨스"
AGY = os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe")
L = json.load(open(f"{W}/lines.json", encoding="utf-8"))
CTX = "영화 「하비의 마지막 로맨스」(Last Chance Harvey, 2008). 하비(뉴욕의 60대 광고 음악 작곡가, 이혼남)가 딸 수전의 런던 결혼식에 갔다가, 공항 설문 조사원인 40대 독신 영국 여성 케이트를 만나는 로맨스. 케이트의 엄마 매기, 하비의 전 부인 진, 진의 새 남편 브라이언, 하비의 사장 마빈."
def job(k, part):
    body = "\n".join(f"{x['id']}\t{x['en'].strip()}" for x in part)
    p = (f"{CTX}\n아래는 이 영화의 영어 대사 받아쓰기(번호\t영어)다. 받아쓰기라 틀린 낱말·끊긴 문장이 섞여 있다. "
         "줄마다 한국 극장 자막처럼 짧고 자연스러운 한국어로 옮겨라(앞뒤 줄 맥락을 보고, 존댓말·반말은 인물 관계에 맞게, 한 줄 18자 안팎). "
         "노래 가사·뜻 없는 소리는 그대로 짧게. 출력은 줄마다 `번호\t한국어` 만, 설명·머리말 없이. 도구를 쓰지 말고 답해줘.\n\n" + body)
    for t in range(3):
        r = subprocess.run([AGY, "-p", p, "--print-timeout", "600s"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        got = dict((int(m.group(1)), m.group(2).strip()) for m in re.finditer(r"^(\d+)\t(.+)$", r.stdout, re.M))
        if len(got) >= len(part) * 0.9: return got
        print("retry", k, len(got), r.stderr[-200:], flush=True)
    return got
parts = [L[i:i + 250] for i in range(0, len(L), 250)]
res = {}
with cf.ThreadPoolExecutor(3) as ex:
    for got in ex.map(lambda a: job(*a), enumerate(parts)): res.update(got)
with open(f"{W}/srt.txt", "w", encoding="utf-8") as f:
    for x in L:
        if x["id"] in res: f.write(f"{x['id']}\t{x['s']:.1f}\t{x['e']:.1f}\t{res[x['id']]}\n")
print("done", len(res), "/", len(L))
