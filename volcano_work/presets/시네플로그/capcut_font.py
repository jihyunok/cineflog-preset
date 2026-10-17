# -*- coding: utf-8 -*-
"""캡컷 드래프트의 나레이션·대사 자막 글꼴을 편 ep.json 대로 바꾼다 — capcut_style04.py 다음에 돌린다.
2026-10-16 04v2 위드아웃 리모스: 사용자 "글자체들은 원래프리셋대로해줘" / "시네플로그말고" → 영화리뷰롱폼 프리셋 글꼴(나레 카페24당당해 · 대사 광화문=Yeonil_TM).
capcut_style04 는 사용자 04 꼴(캡컷 내장 글꼴·기울임 10도)을 옮기므로, 그 뒤에 글꼴 파일·기울임만 덮는다(테두리·위치는 04 꼴 그대로).
★같은 날 사용자 "큰글자도있고 색깔있는글자도 있고 다양한데 넌 그걸안지켰네?" → ep.json "capstyle": "jimovie" 면 자막마다 subs.ass 의 같은 줄
  (시작 0.06초 안 · 글자 같음)을 찾아 꼴(NP 일반 나레 · NE 강조 나레 · DJ 대사 · DY 노랑 대사)과 ASS 꾸밈(\\fn \\fs \\c \\i)을 캡컷 글자 구간(styles range)으로 옮긴다.
  크기는 시네플로그 04 꼴 기준(ASS 100 = 캡컷 8.0). 글꼴 파일은 작업 폴더 fonts/ (이름 바꾼 청도읍성체 사본 포함).
사용(캡컷에서 그 드래프트를 닫은 뒤, 작업 폴더에서): python capcut_font.py <드래프트폴더>"""
import copy, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "v9"))
FONT_DIR = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts").replace("\\", "/")
BAK = os.path.expanduser("~/volcano_work/시네플로그/_capcut_bak")
CFG = json.load(open("ep.json", encoding="utf-8"))
ROLE = {"나레이션 자막": CFG.get("nfont"), "대사 자막": CFG.get("dfont")}
JM = CFG.get("capstyle") == "jimovie"
CC_PER_ASS = 8.0 / 100            # 04 꼴 나레 캡컷 8.0 = ASS 100


def font_file(spec):
    p = f"{FONT_DIR}/{spec[1]}"
    if not os.path.exists(p): raise SystemExit(f"글꼴 파일 없음: {p}")
    return p


def apply(d):
    M = {m["id"]: m for m in d["materials"]["texts"]}; n = 0
    for t in d["tracks"]:
        spec = ROLE.get(t.get("name")) if t["type"] == "text" else None
        if not spec: continue
        path = font_file(spec); italic = bool(spec[2])
        for s in t["segments"]:
            m = M[s["material_id"]]
            m.update({"font_path": path, "fonts": [], "font_resource_id": "", "font_source_platform": 0, "font_id": "",
                      "italic_degree": 10 if italic else 0})
            c = json.loads(m["content"])
            for st in c.get("styles", []):
                st["font"] = {"id": "", "path": path}; st["italic"] = italic
            m["content"] = json.dumps(c, ensure_ascii=False); n += 1
    return n


# ── 지무비식: subs.ass → 줄마다 [(글자, 글꼴 파일, ASS 크기, RGB, 기울임)]
def _t(x):
    h, m, s = x.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)


def ass_runs():
    from jm_style import JM_NAME2FILE
    fdir = os.path.abspath(CFG.get("fonts", "fonts")).replace("\\", "/")
    def ffile(name):           # 캡컷은 파일 경로로 읽으니 이 컴퓨터에 깐 글꼴 자리를 먼저(작업 폴더를 지워도 열리게) · 이름 바꾼 청도 사본 대신 원본 파일
        fn = "CHEONGDOM-Medium.ttf" if JM_NAME2FILE[name] == "CheongdoM-renamed.ttf" else JM_NAME2FILE[name]
        return f"{FONT_DIR}/{fn}" if os.path.exists(f"{FONT_DIR}/{fn}") else f"{fdir}/{JM_NAME2FILE[name]}"
    def rgb(c): c = c.strip("&H").strip("&"); c = c[-6:]; return (int(c[4:6], 16), int(c[2:4], 16), int(c[0:2], 16))
    styles, rows = {}, []
    for l in open("subs.ass", encoding="utf-8"):
        if l.startswith("Style:"):
            f = l[6:].strip().split(","); styles[f[0]] = (f[1], float(f[2]), rgb(f[3]), f[8] == "-1" or f[8] == "1")
        elif l.startswith("Dialogue:"):
            f = l.rstrip("\n").split(",", 9); sty = f[3]
            if sty not in ("NP", "NE", "DJ", "DY"): continue
            name, size, col, ital = styles[sty]; runs = []
            for tags, txt in re.findall(r"\{([^}]*)\}([^{]*)", "{}" + f[9]):
                for k, v in re.findall(r"\\(fn|fs|c|i)([^\\]*)", tags):
                    if k == "fn": name = v
                    elif k == "fs" and not v.startswith("c"): size = float(v)
                    elif k == "c": col = rgb(v)
                    elif k == "i": ital = v.strip() == "1"
                if txt: runs.append((txt, ffile(name), size, col, ital))
            rows.append((_t(f[1]), "".join(r[0] for r in runs), sty, runs))
    return rows


def apply_jm(d, rows):
    M = {m["id"]: m for m in d["materials"]["texts"]}; n = miss = 0
    for t in d["tracks"]:
        if t["type"] != "text" or t.get("name") not in ROLE: continue
        for s in t["segments"]:
            m = M[s["material_id"]]; c = json.loads(m["content"]); a = s["target_timerange"]["start"] / 1e6
            hit = next((r for r in rows if r[1] == c["text"] and abs(r[0] - a) < 0.06), None)
            if not hit: miss += 1; continue
            base = c["styles"][0]; out = []; pos = 0
            for txt, path, size, col, ital in hit[3]:
                st = copy.deepcopy(base); st["range"] = [pos, pos + len(txt)]; pos += len(txt)
                st["font"] = {"id": "", "path": path}; st["size"] = round(size * CC_PER_ASS, 2); st["italic"] = ital
                st["fill"] = {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": [col[0] / 255, col[1] / 255, col[2] / 255]}}}
                out.append(st)
            c["styles"] = out
            r0 = hit[3][0]
            m.update({"font_path": r0[1], "fonts": [], "font_resource_id": "", "font_source_platform": 0, "font_id": "", "italic_degree": 0,
                      "font_size": max(r[2] for r in hit[3]) * CC_PER_ASS, "text_color": "#%02X%02X%02X" % r0[3],
                      "content": json.dumps(c, ensure_ascii=False)})
            n += 1
    return n, miss


if __name__ == "__main__":
    if not JM and not any(ROLE.values()): raise SystemExit("ep.json 에 nfont·dfont·capstyle 이 없다 — 이 편은 04 꼴 글꼴 그대로")
    rows = ass_runs() if JM else None
    for D in sys.argv[1:]:
        if os.path.exists(f"{D}/.locked"): print(os.path.basename(D), "캡컷에서 열려 있음 — 닫고 다시"); continue
        tl = json.load(open(f"{D}/timeline_layout.json", encoding="utf-8"))["dockItems"][0]["timelineIds"][0]
        b = f"{BAK}/{os.path.basename(D)}"; os.makedirs(b, exist_ok=True)
        for p in (f"{D}/draft_content.json", f"{D}/Timelines/{tl}/draft_content.json"):
            if not os.path.exists(p): continue
            shutil.copy(p, f"{b}/{os.path.relpath(p, D).replace(os.sep, '__').replace('/', '__')}.before_font")
            d = json.load(open(p, encoding="utf-8"))
            if JM:
                n, miss = apply_jm(d, rows)
                print(os.path.basename(D), os.path.relpath(p, D), "지무비식 자막", n, "개 · 못 맞춘 줄", miss)
            else:
                n = apply(d); print(os.path.basename(D), os.path.relpath(p, D), "자막 글꼴", n, "개 →", ROLE["나레이션 자막"][0], "·", ROLE["대사 자막"][0])
            json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
