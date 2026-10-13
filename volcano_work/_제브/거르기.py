# -*- coding: utf-8 -*-
"""제브(Jev) 대량 판정 도구 — 부록_제브_세팅.md 3-3 사양.

  py -3.12 거르기.py --spec 소재거르기.json --in 항목.jsonl --out 결과.jsonl [--topic "채널 주제"]

항목.jsonl: 한 줄에 JSON 하나, id 칸 필수(text 칸에 판정할 글). 결과.jsonl: {"id": …, "answers": {질문 이름: 답}}.
- 항목 하나 = 요청 하나, 그 항목의 질문은 전부 한 요청에. state 는 이름 붙은 칸(spec 의 state_fields)으로 보낸다.
- 동시 8. 거부(429·529)가 한 번이라도 나면 전부 멈추고 그 사실을 출력한다(SDK 자동 재시도 끔).
- 이어하기: --out 에 이미 있는 id 는 건너뛴다.
- 모델 jev-1.13.0 고정. 열쇠는 환경 변수 TYPESAFE_API_KEY (윈도우: 없으면 ~/.volcano/keys/typesafe). 값을 출력하지 않는다.
종료코드: 0 다 됨 · 1 일부 실패 · 2 거부로 멈춤 · 3 열쇠 없음·잘못된 입력.
"""
import argparse, asyncio, json, os, sys, time

for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass

MODEL = "jev-1.13.0"


def load_key():
    k = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if not k:
        p = os.path.join(os.path.expanduser("~"), ".volcano", "keys", "typesafe")
        if os.path.exists(p):
            k = open(p, encoding="utf-8").read().strip()
    return k


def build_questions(spec):
    from typesafe_sdk import Choice, Noul, Score
    qs = {}
    for name, q in spec["questions"].items():
        t = q["type"]
        kw = {"instructions": q["instructions"]}
        if "criteria" in q:
            kw["criteria"] = q["criteria"]
        qs[name] = {"noul": Noul, "choice": Choice, "score": Score}[t](**kw)
    return qs


def read_answers(spec, r):
    out = {}
    for name, q in spec["questions"].items():
        t = q["type"]
        if t == "noul":
            out[name] = round(r.nouls[name].noul, 4)
        elif t == "choice":
            a = r.choices[name]
            out[name] = {"choice": a.choice, "confidence": round(getattr(a, "confidence", 0) or 0, 4)}
        else:
            a = r.scores[name]
            out[name] = {"score": round(a.score, 4), "confidence": round(getattr(a, "confidence", 0) or 0, 4)}
    return out


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--topic", default="")
    a = ap.parse_args()
    key = load_key()
    if not key:
        print("열쇠 없음: TYPESAFE_API_KEY 를 등록하세요"); return 3
    try:
        spec = json.load(open(a.spec, encoding="utf-8"))
        items = [json.loads(l) for l in open(a.inp, encoding="utf-8") if l.strip()]
        assert all("id" in it for it in items), "id 칸이 없는 항목이 있다"
        qs = build_questions(spec)
    except Exception as e:
        print("잘못된 입력:", e); return 3
    done = set()
    if os.path.exists(a.out):
        for l in open(a.out, encoding="utf-8"):
            if l.strip():
                done.add(json.loads(l)["id"])
    todo = [it for it in items if it["id"] not in done]
    from typesafe_sdk import AsyncTypeSafeClient, RetryPolicy, TypeSafeAPIError
    sem = asyncio.Semaphore(8)
    state = {"stop": False, "fail": 0, "ok": 0}
    lock = asyncio.Lock()
    t0 = time.time()
    with open(a.out, "a", encoding="utf-8") as f:
        async with AsyncTypeSafeClient(api_key=key, model=MODEL, retry=RetryPolicy(max_retries=0)) as c:
            async def one(it):
                if state["stop"]:
                    return
                async with sem:
                    if state["stop"]:
                        return
                    st = {k: it.get(k, "") for k in spec.get("state_fields", ["text"])}
                    if "channel_topic" in st and a.topic:
                        st["channel_topic"] = a.topic
                    try:
                        r = await c.system_one(state=st, questions=qs)
                        row = {"id": it["id"], "answers": read_answers(spec, r)}
                        async with lock:
                            f.write(json.dumps(row, ensure_ascii=False) + "\n"); f.flush()
                        state["ok"] += 1
                    except TypeSafeAPIError as e:
                        if getattr(e, "status", None) in (429, 529):
                            state["stop"] = True
                        state["fail"] += 1
                        print(f"[실패] {it['id']}: {getattr(e, 'status', '')}")
                    except Exception as e:
                        state["fail"] += 1
                        print(f"[실패] {it['id']}: {str(e)[:200]}")
            await asyncio.gather(*(one(it) for it in todo))
    print(f"{state['ok']}건 판정 · 건너뜀 {len(done)} · 실패 {state['fail']} · {time.time()-t0:.1f}초 · 거부로 멈춤 {'예' if state['stop'] else '아니오'} → {a.out}")
    return 2 if state["stop"] else (1 if state["fail"] else 0)


sys.exit(asyncio.run(main()))
