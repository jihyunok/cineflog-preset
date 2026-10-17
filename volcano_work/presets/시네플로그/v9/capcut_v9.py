# -*- coding: utf-8 -*-
"""build_v9.py 결과로 캡컷 프로젝트(드래프트)를 만든다(16 핀치 capcut_v8.py 복사 — 파일 이름만 v9: all.txt·org.wav·subs.ass, 음원은 ep.json "music", 표지 thumb_A.jpg).
모든 확인이 끝난 완성본에서 한 번만(10-13 "모든게 완성이되면캡컷파일만들어 자꾸만들지말고"). 뒤에 capfix.py → capcut_style04.py → capcut_to_final.py.
트랙: 영상(컷 + 원본 소리) / 나레이션 / 음악 / 자막(한 줄) / CINEFLOG
틀: 사용자의 가로 드래프트 'D:/다운로드/CapCut Drafts/0826 (2)'(영상·자막) + '0826 (8)'(오디오)."""
import copy, json, os, re, shutil, subprocess, time, uuid

ROOT = "D:/다운로드/CapCut Drafts"
NAME = os.environ.get("CC_NAME", "시네플로그07")
TPL, TPL_A = (f"{ROOT}/0826 (2)" if os.path.exists(f"{ROOT}/0826 (2)") else os.path.expanduser("~/영화롱폼_이식팩/캡컷틀/0826 (2)")), f"{ROOT}/0826 (8)"  # 0826 (2) 가 캡컷 폴더에서 빠짐(10-04) → 이식팩 사본
OUT = f"{ROOT}/{NAME}"; MED = f"{OUT}/media"
FONT = os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts/Pretendard-Bold.otf").replace("\\", "/")
US = 1_000_000

def nid(): return str(uuid.uuid4()).upper()
def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)

tpl = json.load(open(f"{TPL}/draft_content.json", encoding="utf-8"))
tpa = json.load(open(f"{TPL_A}/draft_content.json", encoding="utf-8"))
def first_seg(d, typ): return [s for t in d["tracks"] if t["type"] == typ for s in t["segments"]][0]
def find_mat(d, mid):
    for k, v in d["materials"].items():
        if isinstance(v, list):
            for x in v:
                if isinstance(x, dict) and x.get("id") == mid: return k, x
    return None, None
TV, TT, TA = first_seg(tpl, "video"), first_seg(tpl, "text"), first_seg(tpa, "audio")

d = copy.deepcopy(tpl)
for k, v in d["materials"].items():
    if isinstance(v, list): d["materials"][k] = []
d["tracks"] = []
d["canvas_config"] = {"ratio": "original", "width": 1920, "height": 1080, "background": None}
d["fps"] = 30.0

def extras(src_doc, seg, skip=("loudnesses",)):
    refs = []
    for r in seg["extra_material_refs"]:
        k, m = find_mat(src_doc, r)
        if not m or k in skip: continue
        m = copy.deepcopy(m); m["id"] = nid(); d["materials"].setdefault(k, []).append(m); refs.append(m["id"])
    return refs

def track(typ, name=""):
    t = {"id": nid(), "type": typ, "flag": 0, "attribute": 0, "name": name, "is_default_name": not name, "segments": []}
    d["tracks"].append(t); return t

mat_cache = {}
def video_mat(path, du):
    if path in mat_cache: return mat_cache[path]
    k, m = find_mat(tpl, TV["material_id"]); m = copy.deepcopy(m)
    m.update({"id": nid(), "path": path, "duration": du, "width": 1920, "height": 1080, "has_audio": True,
              "material_name": os.path.basename(path), "media_path": "", "local_id": ""})
    d["materials"]["videos"].append(m); mat_cache[path] = m["id"]; return m["id"]

def add_video(tr, path, t0, du, idx):
    s = copy.deepcopy(TV); s.update({"id": nid(), "material_id": video_mat(path, du), "extra_material_refs": extras(tpl, TV),
        "source_timerange": {"start": 0, "duration": du}, "target_timerange": {"start": t0, "duration": du},
        "volume": 1.0, "last_nonzero_volume": 1.0, "render_index": 0, "track_render_index": 0, "speed": 1.0})
    s["clip"] = {"scale": {"x": 1.0, "y": 1.0}, "rotation": 0.0, "transform": {"x": 0.0, "y": 0.0},
                 "flip": {"vertical": False, "horizontal": False}, "alpha": 1.0}
    tr["segments"].append(s)

def add_audio(tr, path, t0, du, vol=1.0, tri=1, src0=0):
    k, m = find_mat(tpa, TA["material_id"]); m = copy.deepcopy(m)
    m.update({"id": nid(), "path": path, "name": os.path.basename(path), "duration": int(dur(path) * US), "type": "extract_music"})
    d["materials"]["audios"].append(m)
    s = copy.deepcopy(TA); s.update({"id": nid(), "material_id": m["id"], "extra_material_refs": extras(tpa, TA),
        "source_timerange": {"start": src0, "duration": du}, "target_timerange": {"start": t0, "duration": du},
        "volume": vol, "last_nonzero_volume": vol, "track_render_index": tri})
    tr["segments"].append(s)

def add_text(tr, text, t0, du, y, size=5.0, color=(1.0, 1.0, 1.0), x=0.0, tri=3, align=1):
    k, m = find_mat(tpl, TT["material_id"]); m = copy.deepcopy(m)
    hexc = "#%02X%02X%02X" % tuple(int(c * 255) for c in color)
    m.update({"id": nid(), "type": "text", "font_path": FONT, "font_size": size, "text_color": hexc,
              "border_color": "#000000", "border_width": 0.08, "alignment": align, "font_id": "", "font_resource_id": "",
              "content": json.dumps({"styles": [{"fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": list(color)}}},
                                      "font": {"id": "", "path": FONT}, "range": [0, len(text)], "size": size,
                                      "strokes": [{"content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": [0.0, 0.0, 0.0]}}, "width": 0.08}]}],
                                     "text": text}, ensure_ascii=False)})
    d["materials"]["texts"].append(m)
    s = copy.deepcopy(TT); s.update({"id": nid(), "material_id": m["id"], "extra_material_refs": extras(tpl, TT),
        "target_timerange": {"start": t0, "duration": du}, "track_render_index": tri, "render_index": 14000 + tri})
    s["clip"] = {"scale": {"x": 1.0, "y": 1.0}, "rotation": 0.0, "transform": {"x": x, "y": y},
                 "flip": {"vertical": False, "horizontal": False}, "alpha": 1.0}
    tr["segments"].append(s)

# ── 새 드래프트 폴더
if os.path.exists(OUT): shutil.rmtree(OUT)
shutil.copytree(TPL, OUT, ignore=shutil.ignore_patterns("*.bak", "*.tmp", "Resources", "draft_cover.jpg", "crypto_key_store.dat", "draft.extra"))
os.makedirs(MED, exist_ok=True); os.makedirs(f"{OUT}/Resources", exist_ok=True)

# ── 순서: v5 — 벤치 편집표 컷(clips_v5, 소리 끔) + 원본 소리 트랙(나레 자리 낮춤) + 나레 조각을 벤치 나레 자리에
order = [l.split("'")[1] for l in open("all.txt", encoding="utf-8") if l.startswith("file")]
vt = track("video"); ot = track("audio", "원본 소리"); nt = track("audio", "나레이션"); mt = track("audio", "음악")
t0 = 0
for k, p in enumerate(order):
    L = dur(p); Lu = int(round(L * US)); out = f"{MED}/{k:03d}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-c:v", "copy", "-an", out], check=True)
    add_video(vt, out, t0, Lu, k); vt["segments"][-1]["volume"] = 0.0; vt["segments"][-1]["last_nonzero_volume"] = 1.0
    t0 += Lu
BODY = t0
ow = f"{MED}/original_sound.wav"; shutil.copy("org.wav", ow)
add_audio(ot, ow, 0, min(BODY, int(dur(ow) * US)), 1.0, 1)
for q in json.load(open("narr_place.json")):
    nw = f"narr/n{q['ni']:03d}.wav"; nw2 = f"{MED}/narr_{q['ni']:03d}.wav"; shutil.copy(nw, nw2)
    add_audio(nt, nw2, int(q["t"] * US), int(dur(nw2) * US), 1.0, 2)
# ── 자막: subs.ass 그대로 (한 줄)
st = track("text", "자막"); top = track("text", "로고")
def tsec(x):
    h, m, s = x.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
for l in open("subs.ass", encoding="utf-8"):
    if not l.startswith("Dialogue"): continue
    f = l.rstrip("\n").split(",", 9); a, b, sty, txt = tsec(f[1]), tsec(f[2]), f[3], re.sub(r"\{[^}]*\}", "", f[9])   # ★10-16 지무비식 자막의 ASS 꾸밈 기호는 빼고 글자만(색·글꼴은 ../capcut_font.py 가 다시 칠함)
    if sty == "TOP": add_text(top, txt, 0, d.get("duration", BODY), 0.87, 3.2, (0.71, 0.71, 0.71), -0.86, 4, 0)
    else: add_text(st, txt, int(a * US), int((b - a) * US), -0.875, 5.0)

# ── 음악: 끝 비평 아래 + 끝까지
music = os.path.expanduser(json.load(open("ep.json", encoding="utf-8")).get("music", r"~/volcano_work/달빛롱폼/bgm/Healing.mp3"))
mp = f"{MED}/music.mp3"; shutil.copy(music, mp)
pl = json.load(open("narr_place.json")); t_out = int((pl[-1]["t"] - 1.0) * US)
END = max(BODY, int((pl[-1]["t"] + pl[-1]["d"] + 1.5) * US))
add_audio(mt, mp, t_out, END - t_out, 0.12, 3)
d["duration"] = END

# ── 저장 (루트 + 타임라인 폴더)
tl_old = os.listdir(f"{OUT}/Timelines")[0]; tl = d["id"] = nid()
os.rename(f"{OUT}/Timelines/{tl_old}", f"{OUT}/Timelines/{tl}")
for p in (f"{OUT}/draft_content.json", f"{OUT}/Timelines/{tl}/draft_content.json"):
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
for p in (f"{OUT}/Timelines/{tl}/draft_cover.jpg", f"{OUT}/draft_cover.jpg"):
    if os.path.exists("thumb_A.jpg"): shutil.copy("thumb_A.jpg", p)
lay = json.load(open(f"{OUT}/timeline_layout.json", encoding="utf-8"))
lay["dockItems"][0]["timelineIds"] = [tl]; json.dump(lay, open(f"{OUT}/timeline_layout.json", "w", encoding="utf-8"), ensure_ascii=False)
now = int(time.time() * 1e6); did = nid()
CLEAN = {"cloud_package_completed_time": "", "tm_draft_cloud_completed": "", "tm_draft_cloud_entry_id": -1, "tm_draft_cloud_modified": 0,
         "tm_draft_cloud_parent_entry_id": -1, "tm_draft_cloud_space_id": -1, "tm_draft_cloud_user_id": -1}   # 틀의 클라우드 연결 끊기(복제 막힘)
meta = json.load(open(f"{OUT}/draft_meta_info.json", encoding="utf-8"))
meta.update({"draft_id": did, "draft_fold_path": OUT, "draft_name": NAME, "draft_root_path": ROOT.replace("/", "\\"),
             "tm_duration": d["duration"], "tm_draft_create": now, "tm_draft_modified": now, "draft_cover": "draft_cover.jpg", **CLEAN})
for g in meta.get("draft_materials", []): g["value"] = []
json.dump(meta, open(f"{OUT}/draft_meta_info.json", "w", encoding="utf-8"), ensure_ascii=False)

# ── 캡컷 목록(root_meta_info)에 등록 — 원본은 .bak 로 보관
RM = os.path.expanduser(r"~/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/root_meta_info.json")
shutil.copy(RM, RM + ".cineflog.bak")
r = json.load(open(RM, encoding="utf-8"))
r["all_draft_store"] = [e for e in r["all_draft_store"] if e.get("draft_name") != NAME]
e = copy.deepcopy(r["all_draft_store"][0])
e.update({"draft_cover": f"{OUT}\\draft_cover.jpg", "draft_fold_path": OUT, "draft_id": did, "draft_json_file": f"{OUT}\\draft_content.json",
          "draft_name": NAME, "draft_root_path": ROOT.replace("/", "\\"), "tm_duration": d["duration"],
          "tm_draft_create": now, "tm_draft_modified": now, "draft_timeline_materials_size": 0, **CLEAN})
r["all_draft_store"].insert(0, e)
json.dump(r, open(RM, "w", encoding="utf-8"), ensure_ascii=False)
# 타임라인 번호(project.json) 맞추고 틀 찌꺼기 정리 — 안 하면 캡컷에서 안 열린다
subprocess.run(["python", os.path.expanduser("~/volcano_work/presets/시네플로그/capcut_fixtl.py"), OUT], check=True)
subprocess.run(["python", os.path.expanduser("~/volcano_work/presets/시네플로그/capcut_split_subs.py"), OUT], check=True)  # 나레/대사 자막 트랙 나누기
print("캡컷 드래프트:", OUT, "·", round(d["duration"] / US / 60, 2), "분 · 영상", len(vt["segments"]), "· 나레", len(nt["segments"]),
      "· 자막", len(st["segments"]))
