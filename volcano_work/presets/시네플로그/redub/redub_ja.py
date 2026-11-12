# -*- coding: utf-8 -*-
"""다시나레 일본어판. 11-01 텔레그램 사용자 「일본어로 글자바꾸고 나래이선바꿔서 다 만들어줘」·「일본어는 보이스복스 사용하면되니까」
한국어판 폴더 W(redub.py 로 다 만든 곳) 옆에 W_ja 를 만들고, 우리 새 나레(narr_new.json)를 일본어로 옮겨 VOICEVOX 로 읽는다.
화면은 처음부터 끝까지 확대(zoom_args 의 crop) → 옛 한국어 자막·채널 글자가 다 화면 밖. 대사는 원래 소리 + 일본어 대사 자막(받아쓰기 asr.json 옮김).
  python redub_ja.py all W [nodlg]   setup → tr → dlg → tts → subs → vf → mix  (nodlg: 원래 일본어 드라마라 대사 자막 없음)
목소리: 青山龍星 ノーマル(VID 13) 속도 1.12 · 높이 -0.03 (일본어판/README — 10-05 사용자 고름). 크레딧 「VOICEVOX:青山龍星」 설명란에."""
import json, os, re, subprocess, sys, shutil
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "일본어판")); sys.path.insert(0, os.path.join(HERE, "..", "b판"))
import redub as R, vv
VID, SPEED, PITCH = 13, 1.12, -0.03
J = lambda W: W.rstrip("/\\") + "_ja"


def setup(W):
    Wj = J(W); os.makedirs(os.path.join(Wj, "narr"), exist_ok=True)
    for f in ("src.mp4", "narr_blocks.json", "chunks.json", "asr.json", "title.txt", "zoom_args.txt"):
        d = os.path.join(Wj, f)
        if not os.path.exists(d) and os.path.exists(os.path.join(W, f)): os.link(os.path.join(W, f), d)
    for f in ("dm", "sep"):                       # mix 가 쓰는 배경(no_vocals) — 폴더 연결
        d = os.path.join(Wj, f)
        if not os.path.exists(d) and os.path.exists(os.path.join(W, f)):
            subprocess.run(["cmd", "/c", "mklink", "/J", d.replace("/", "\\"), os.path.join(W, f).replace("/", "\\")], check=True, capture_output=True)
    print("setup", Wj)


CPS = 7.0     # 11-01 실측: 青山龍星 1.12 배 = 일본어 7.4자/초. 한국어 글자 수 기준(×0.85)으로 하니 자리의 절반만 채움 → 자리 길이 기준


def tr(W, only=None, k=1.0):
    """우리 한국어 새 나레 → 일본어(글자 수 = 자리 길이 × 7자 × k 의 80~100%). only: 이 번호들만 다시(더 짧게)."""
    import make_b as MB
    Wj = J(W); B = R.blocks(W); KO = json.load(open(os.path.join(W, "narr_new.json"), encoding="utf-8"))
    out = os.path.join(Wj, "narr_new.json"); N = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else {}
    title = open(os.path.join(W, "title.txt"), encoding="utf-8").read().strip()
    if only is not None:
        for i in only: N.pop(str(i), None)
    lim = lambda i: max(4, int((B[i][1] - B[i][0]) * CPS * k))
    def job(part):
        ctx = "\n".join(f"{j}. {KO[str(j)]}" for j in range(max(0, part[0] - 5), min(len(B), part[-1] + 6)))
        req = "\n".join(f"{i}. ({lim(i)}자) {KO[str(i)]}" for i in part)
        p = (f"아래는 한국 드라마 「{title}」 결말까지 몰아보기 유튜브 영상의 한국어 나레이션이다.\n" + ctx +
             "\n\n아래 번호 줄들을 일본 유튜브 드라마 요약(一気見) 나레이션 일본어로 옮겨라. 자연스러운 구어체(〜んです、〜ます、〜でした 섞어서), 뜻·사실은 그대로. "
             "인물 이름은 일본 방영·공식 표기가 있으면 그것, 없으면 가타카나(예: 우영우 → ウ・ヨンウ). 회사·지명도 자연스럽게. "
             "괄호 안 글자 수(일본어 글자 수, 문장부호 포함)는 그 줄이 들어갈 자리 길이다 — 그 글자 수의 80~100% 로 채워라(한국어보다 길어져도 된다: 앞뒤 흐름에 나온 사실·인물 관계를 자연스럽게 보태라. 없는 사실은 지어내지 마라). 넘기면 안 된다. 큰따옴표 대신 「」.\n"
             "출력은 JSON 객체 하나만: {\"번호\": \"일본어 문장\", ...}\n\n" + req)
        r = MB.ask(p); m = re.search(r"\{.*\}", r, re.S)
        try: return part, json.loads(m.group(0)) if m else {}
        except Exception: return part, {}
    for tries in range(6):
        todo = [i for i in range(len(B)) if str(i) not in N]
        if not todo: break
        with ThreadPoolExecutor(4) as ex:
            for part, d in ex.map(job, [todo[x:x + 25] for x in range(0, len(todo), 25)]):
                for i in part:
                    s = (d.get(str(i)) or "").strip()
                    if s and len(s) <= lim(i) + 2 and re.search(r"[぀-ヿ一-鿿]", s) and not re.search(r"[가-힣]", s): N[str(i)] = s
                json.dump(N, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                print("tr", len(N), "/", len(B), flush=True)
    print("못 옮긴 줄", [i for i in range(len(B)) if str(i) not in N])


def dlg(W):
    """대사(받아쓰기 구간 중 나레 덩어리와 거의 안 겹치는 것) → 일본어 대사 자막 W_ja/dlg_ja.json [[a, b, 글자]]."""
    import make_b as MB
    Wj = J(W); B = R.blocks(W); S = json.load(open(os.path.join(W, "asr.json"), encoding="utf-8"))["segments"]
    title = open(os.path.join(W, "title.txt"), encoding="utf-8").read().strip()
    import bisect
    ba = [b[0] for b in B]; D = []
    for s in S:
        a, b, t = s["start"], s["end"], s["text"].strip()
        if not t or b - a < 0.4: continue
        k = bisect.bisect_right(ba, b); ov = 0
        for x, z, _ in B[max(0, k - 3):k + 1]: ov += max(0, min(b, z) - max(a, x))
        if ov < 0.3 * (b - a): D.append([a, b, t])
    out = os.path.join(Wj, "dlg_ja.json"); N = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else {}
    def job(part):
        req = "\n".join(f"{i}. {D[i][2]}" for i in part)
        p = (f"아래는 한국 드라마 「{title}」의 대사 받아쓰기(자동이라 틀린 낱말이 있을 수 있다 — 앞뒤 흐름으로 바로잡아라)다.\n"
             "번호마다 일본어 자막으로 옮겨라. 짧게(최대 32자, 길면 뜻만 살려 줄여라), 자연스러운 일본 드라마 자막 말투. 인물 이름은 가타카나. "
             "의미 없는 소리·받아쓰기 잡음이면 빈 문자열.\n출력은 JSON 객체 하나만: {\"번호\": \"일본어\", ...}\n\n" + req)
        r = MB.ask(p); m = re.search(r"\{.*\}", r, re.S)
        try: return part, json.loads(m.group(0)) if m else {}
        except Exception: return part, {}
    for tries in range(4):
        todo = [i for i in range(len(D)) if str(i) not in N]
        if not todo: break
        with ThreadPoolExecutor(4) as ex:
            for part, d in ex.map(job, [todo[x:x + 40] for x in range(0, len(todo), 40)]):
                for i in part:
                    if str(i) in d: N[str(i)] = str(d[str(i)]).strip()[:40]
                json.dump(N, open(out + ".tmp", "w", encoding="utf-8"), ensure_ascii=False)
                print("dlg", len(N), "/", len(D), flush=True)
    json.dump([[D[i][0], D[i][1], N[str(i)]] for i in range(len(D)) if N.get(str(i))], open(out, "w", encoding="utf-8"), ensure_ascii=False)
    os.path.exists(out + ".tmp") and os.remove(out + ".tmp")
    print("대사 자막", sum(1 for i in range(len(D)) if N.get(str(i))), "/", len(D))


def tts(W, mode=None):
    """VOICEVOX → W_ja/narr/nNNN.wav(1부터) → 자리에 맞춤 bNNN.wav. 넘치면 tr(더 짧게) 다시 → 다시 읽기 (최대 3번).
    mode="noagy": 11-12 agy 금지(구글 계정 정지 위험) — tr 다시 부르지 않고 한 번만 읽어 맞추고 넘친 줄만 알린다.
      줄이기는 클로드가 W_ja/narr_new.json 을 직접 고친 뒤 다시 돌린다(글이 같은 줄은 다시 읽지 않음)."""
    Wj = J(W); B = R.blocks(W); N = json.load(open(os.path.join(Wj, "narr_new.json"), encoding="utf-8"))
    def one(i):
        p = os.path.join(Wj, f"narr/n{i+1:03d}.wav"); js = p + ".txt"
        if os.path.exists(js) and open(js, encoding="utf-8").read() == N[str(i)]: return
        vv.synth(N[str(i)], VID, SPEED, PITCH, out=p); open(js, "w", encoding="utf-8").write(N[str(i)])
    for rnd, k in enumerate((None,) if mode == "noagy" else (None, 0.85, 0.7)):
        if k: tr(W, only=over, k=k); N = json.load(open(os.path.join(Wj, "narr_new.json"), encoding="utf-8"))
        with ThreadPoolExecutor(3) as ex: list(ex.map(one, range(len(B))))
        R.fit(Wj)
        F = json.load(open(os.path.join(Wj, "tts_fit.json"))); over = [i for i, d, room in F if d > room + 0.3]
        print("넘침", len(over), over[:20], flush=True)
        if not over: break


def unlap(W, gap=0.06):
    """11-12 재혼황후: 덩어리 사이 틈이 거의 없는 영상(나레가 처음부터 끝까지 쉬지 않음)은 자리(길이 + PAD×2) 때문에
    앞 녹음 끝이 다음 녹음 처음과 0.3초까지 겹쳤다(28곳). → 겹치는 bNNN.wav 만 조금 더 빠르게(최대 1.08배) 해서
    다음 녹음 시작 gap 초 전에 끝나게. tts_fit.json 길이도 고친다(subs·mix 가 씀). tts(fit) 를 다시 돌리면 그 뒤에 다시 돌린다."""
    Wj = J(W); B = R.blocks(W); fp = os.path.join(Wj, "tts_fit.json"); F = json.load(open(fp)); fixed = []
    for i in range(len(B) - 1):
        a0, n0 = max(0, B[i][0] - 0.05), max(0, B[i + 1][0] - 0.05)
        p = os.path.join(Wj, f"narr/b{i:03d}.wav"); d = R.dur(p); lim = n0 - a0 - gap
        if d > lim + 0.005:
            sp = min(d / lim, 1.08); tmp = p + ".u.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-af", f"atempo={sp:.4f}", "-ar", "48000", "-ac", "2", tmp], check=True)
            os.replace(tmp, p); F[i] = [i, round(R.dur(p), 2), F[i][2]]; fixed.append((i, round(sp, 3)))
    json.dump(F, open(fp, "w"))
    print("겹침 풀기", len(fixed), fixed)


def cut(t, n=20):
    """일본어 자막 나누기: n 자 넘으면 、。！？ 가까운 데서 둘로 → 조각마다 다시(11-01 우영우: 한 번에 k 등분하니 32자 조각이 남아 화면 밖으로 넘침)."""
    if len(t) <= n: return [t]
    tgt = len(t) / 2; ok = lambda c: 3 <= c <= len(t) - 3
    cs = [m.end() for m in re.finditer(r"[、。！？」]", t) if ok(m.end()) and abs(m.end() - tgt) <= tgt * 0.5]
    if not cs:      # 쉼표가 멀면 조사(は·が·を·に·で·と·も·の) 뒤 — 낱말 가운데서 안 끊게
        cs = [m.end() for m in re.finditer(r"[はがをにでとものへ](?=[^぀-ゟ])", t) if ok(m.end()) and abs(m.end() - tgt) <= tgt * 0.5]
    c = min(cs, key=lambda c: abs(c - tgt)) if cs else round(tgt)
    return cut(t[:c], n) + cut(t[c:], n)


def subs(W, y=660, size=58):
    Wj = J(W); B = R.blocks(W); N = json.load(open(os.path.join(Wj, "narr_new.json"), encoding="utf-8"))
    F = {r[0]: r[1] for r in json.load(open(os.path.join(Wj, "tts_fit.json")))}
    ts = lambda t: f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
    L = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1280", "PlayResY: 720", "", "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
         f"Style: N,Noto Sans JP Black,{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3.5,1,2,30,30,{720-y},1",   # 나레
         f"Style: D,Yu Gothic,{size-8},&H0080F0FF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3,1,2,30,30,{720-y},1", "",   # 대사 — 다른 글꼴·연노랑
         "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    SP = []
    for i, (a, b, _) in enumerate(B):
        t = N[str(i)].strip().rstrip("。"); d = F.get(i, b - a); a0 = max(0, a - 0.05); c = a0
        ps = cut(t); tot = sum(len(x) for x in ps) or 1
        for x in ps:
            e = c + d * len(x) / tot; L.append(f"Dialogue: 0,{ts(c)},{ts(e)},N,,0,0,0,,{x.rstrip('、')}"); c = e
        SP.append((a0, a0 + d))
    p = os.path.join(Wj, "dlg_ja.json"); nd = 0
    if os.path.exists(p):
        SP.sort(); import bisect; sa = [s[0] for s in SP]
        for a, b, t in json.load(open(p, encoding="utf-8")):
            k = bisect.bisect_right(sa, b)
            for x, z in SP[max(0, k - 3):k]:
                if x - 0.05 < b and z > a:
                    if x > a: b = min(b, x - 0.05)
                    else: a = max(a, z)
            if b - a > 0.4:
                t = "\\N".join(cut(t, 18)[:2]); L.append(f"Dialogue: 0,{ts(a)},{ts(b)},D,,0,0,0,,{t}"); nd += 1
    open(os.path.join(Wj, "narr.ass"), "w", encoding="utf-8-sig").write("\n".join(L) + "\n")
    print("subs 나레", len(B), "대사", nd)


def vf(W):
    """11-12 재혼황후(아랍어 요약 채널): 박힌 자막·로고가 없고 인물 이름표만 잠깐 뜨는 영상 → crop_ja.txt·zoom_args.txt 둘 다 없으면 확대 안 함.
    W_ja/blur_ja.json [[시작, 끝, x, y, w, h], ...](1280x720 기준) 이 있으면 그 시간에만 그 네모를 흐리게 덮는다(이름표·구독 막대 가리기).
    7번째 칸이 "black" 이면 흐리기 대신 검은 네모(검은 바탕 끝 인사 글자 「سلام」 같은 것)."""
    Wj = J(W); cj = os.path.join(Wj, "crop_ja.txt")      # 11-01 가면의 여왕·우영우: 대사 자막(그림 안 두 줄)이 확대 아래쪽에 걸림 → 일본어판만 더 좁게
    za = os.path.join(W, "zoom_args.txt")
    cr = open(cj if os.path.exists(cj) else za, encoding="utf-8").read().split()[0] if (os.path.exists(cj) or os.path.exists(za)) else None
    esc = lambda p: p.replace("\\", "/").replace(":", "\\:")
    head = (f"crop={cr}," if cr else "") + "scale=1280:720,setsar=1"
    bp = os.path.join(Wj, "blur_ja.json"); BL = json.load(open(bp, encoding="utf-8")) if os.path.exists(bp) else []
    BK = [r for r in BL if len(r) > 6 and r[6] == "black"]; BL = [r[:6] for r in BL if not (len(r) > 6 and r[6] == "black")]
    if BK:
        head += "".join(f",drawbox=x={x}:y={y}:w={w}:h={h}:color=black:t=fill:enable='between(t,{a},{b})'" for a, b, x, y, w, h, _ in BK)
    if BL:
        g = [f"{head},split={len(BL) + 1}[v0]" + "".join(f"[c{k}]" for k in range(len(BL)))]
        for k, (a, b, x, y, w, h) in enumerate(BL):
            r = max(2, min(24, min(w, h) // 4))
            g.append(f"[c{k}]crop={w}:{h}:{x}:{y},boxblur={r}:3[k{k}]")
        for k, (a, b, x, y, w, h) in enumerate(BL):
            g.append(f"[v{k}][k{k}]overlay={x}:{y}:enable='between(t,{a},{b})'[v{k + 1}]")
        g.append(f"[v{len(BL)}]subtitles='{esc(os.path.join(Wj, 'narr.ass'))}'")
        s = ";".join(g)
    else:
        s = f"{head},subtitles='{esc(os.path.join(Wj, 'narr.ass'))}'"
    open(os.path.join(Wj, "vf.txt"), "w", encoding="utf-8").write(s)
    print("vf", "전체 확대 " + cr if cr else "확대 없음", "· 흐리기", len(BL), "· 검은 네모", len(BK))


def mix(W):
    """W_ja/bg_only.json [[a, b], ...] 이 있으면 그 구간도 원음 대신 배경(no_vocals)만 쓴다.
    11-12 재혼황후: 드라마 소리 없이 아랍어 나레만 있는 영상(배경 −57 LUFS)인데, 받아쓰기 낱말 구간이 끝 인사 꼬리(1800.7초)를 못 덮어 원래 나레가 0.15초 샜다 → [[0, 영상 끝]]."""
    bp = os.path.join(J(W), "bg_only.json")
    if os.path.exists(bp):
        X = json.load(open(bp, encoding="utf-8")); sp0 = R.spans
        R.spans = lambda w: sp0(w) + [[list(x) for x in X]]
    R.mix(J(W), os.path.join(W, "src720.mp4"), "@" + os.path.join(J(W), "vf.txt"))


def all_(W, nodlg=None):
    setup(W); tr(W)
    if not nodlg: dlg(W)
    tts(W); unlap(W); subs(W); vf(W); mix(W)


if __name__ == "__main__":
    c = sys.argv[1]; f = {"setup": setup, "tr": tr, "dlg": dlg, "tts": tts, "unlap": unlap, "subs": subs, "vf": vf, "mix": mix, "all": all_}[c]
    f(*sys.argv[2:])
