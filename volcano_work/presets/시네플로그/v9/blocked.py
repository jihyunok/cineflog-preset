# -*- coding: utf-8 -*-
"""금지 작품 검사 (11-02 워너 · 11-03 사용자 「같이 막고」「영화 원본 주면 안되는거는 시작도 하지마」).
../blocked_studios.txt [작품] 의 한국어 이름(띄어쓰기 무시)·영어 이름을 작업 폴더 이름·원본 경로·업로드 제목과 맞춰 본다.
plan_v9.py 첫 줄(시작 전)과 title_name.py(넘기기 전)가 부른다. 걸리면 그 자리에서 멈춘다.
사용: python blocked.py "<폴더나 제목>"  → 걸리면 exit 1"""
import os, re, sys

LIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blocked_studios.txt")

def works():
    out, sec = [], None
    if not os.path.exists(LIST): return out
    for l in open(LIST, encoding="utf-8").read().splitlines():
        l = l.strip()
        if l.startswith("["): sec = l; continue
        if sec != "[작품]" or not l or l.startswith("#"): continue
        ko = re.sub(r"\s*\(.*", "", l).replace(" ", "")
        m = re.search(r"\(([^,)]+)", l)
        en = re.sub(r"[^a-z0-9]", "", m.group(1).lower()) if m else ""
        out.append((l, ko, en))
    return out

# 이름이 겹쳐 잘못 걸리는 허용 작품(11-03 셔터 아일랜드(파라마운트)가 「아일랜드」에 걸림) — 이 이름은 먼저 지우고 맞춘다
ALLOW = ["셔터아일랜드", "shutterisland"]

def hits(*texts):
    hay = "".join(texts)
    for a in ALLOW:
        hay = re.sub(r"[\s_.]*".join(map(re.escape, a)), "", hay, flags=re.I)
    ko_hay = hay.replace(" ", "").replace("_", "").replace(".", "")
    en_hay = re.sub(r"[^a-z0-9]", "", hay.lower())
    return [l for l, ko, en in works() if (len(ko) >= 2 and ko in ko_hay) or (len(en) >= 5 and en in en_hay)]

def stop_if_blocked(*texts):
    h = hits(*texts)
    if h:
        sys.exit("⛔ 금지 작품 — 만들지도 올리지도 않음(blocked_studios.txt, 11-03 「영화 원본 주면 안되는거는 시작도 하지마」): " + " / ".join(h))

if __name__ == "__main__":
    h = hits(*sys.argv[1:])
    print("\n".join("⛔ " + x for x in h) or "통과")
    sys.exit(1 if h else 0)
