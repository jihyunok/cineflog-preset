# 시네플로그 새 편 견본 (11-03 확정 방식 — 다른 PC 38 노벰버 맨에서 가져옴, 11-04)
새 편 폴더(D:/cine_work/epNN_제목)에 이 파일들을 복사한 뒤 고친다. 규칙은 프리셋 README 맨 앞 「11-04 대본 흐름」.
- `ep.json` — src·srclen·orig·h·burn·title·bench·ctx·places·who·who_ko·name_alias 를 그 영화로. **`"d_fill": 3.0`·`"min_total": 1500` 은 그대로.**
- `_대본지시.md` — 영화 설명·예시 이름·큰 사건·감정 장면 줄을 그 영화로. 규칙은 그대로.
- `_merge.py`·`_split_parts.py`·`_post_merge.py` 등 — 머리 주석의 편 번호·제목만 바꾼다. `hook_outro.py` 는 편집자가 새로 쓴다(지금 내용은 노벰버 맨 본보기).
- 시네플로그는 이름표를 쓰지 않으므로 `_tagsheet.py` 는 가져오지 않았다.
