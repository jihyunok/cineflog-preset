---
name: character-name-consistency
description: "★11-03 영상 속 등장인물 이름 한 번 더 확인 — 한 인물 한 표기, 대사 자막의 실제 이름·별명도 그 표기로 (영화·드라마, name_check.py)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: de3950af-0899-4344-a3a2-c0b42fdaf23e
  modified: 2026-11-03T05:07:19.327Z
---

사용자(11-03 텔레그램): 「이름 안바뀌게 잘 획인해」 「영상 속 등장인물 이름 다시 한번 확인하는 규칙 넣어」. 38 노벰버 맨에서 나레·이름표는 「데버로」「메이슨」인데 대사 자막에 「피터」 6곳·「데이빗」 2곳이 섞였음(사용자 「지금꺼는 다시 안구워도돼」 — 38 은 그대로, 수정용엔 고친 대본).

**Why:** 처음 보는 시청자가 같은 사람을 다른 사람으로 헷갈림.
**How to apply:** 한 인물 = `_줄기.md` 「## 인물 표기」 한 표기. 대사가 성·이름·별명으로 불러도 D 자막은 그 표기(「피터 데버로」처럼 같이 부르면 그대로). 정체가 바뀌는 이름(앨리스=미라)은 나레가 짚은 뒤 새 이름. 줄기 작업자가 ep.json `name_alias` 채우고, 편집자 통독 뒤·넘기기 전에 `v9/prep/name_check.py` 문제 0. 저장소 영화리뷰 README 「11-03 등장인물 이름」, drama_kit SKILL. [[movie-smooth-flow]]
