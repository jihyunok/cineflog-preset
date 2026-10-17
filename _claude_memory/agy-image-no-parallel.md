---
name: agy-image-no-parallel
description: agy_image.py 를 동시에 여러 개 돌리면 모두 같은 그림(가장 최근 것)으로 저장된다 — 차례로 돌리거나 brain 폴더에서 이름으로 다시 찾는다
metadata:
  type: feedback
---

10-14 시니어사이다 인물 4명 그림을 `agy_image.py` 4개 동시에 돌렸더니 네 파일이 md5 까지 같은 한 장으로 저장됐다. 스크립트가 `~/.gemini/antigravity-cli/brain/*/` 에서 «시작 뒤 가장 최근 그림»을 집어 오기 때문(다른 세션의 agy 그림도 섞일 수 있다).

**Why:** 각자 만든 그림은 brain/<대화ID>/<설명>_<시각>.jpg 로 따로 남아 있었다 — 이름(malsoon_character_reference_…)으로 찾아 바로잡았다.
**How to apply:** agy 그림 여러 장은 **차례로** 돌린다. 동시에 돌렸으면 md5 로 같은지 먼저 보고, 같으면 brain 폴더에서 -size +300k·이름으로 다시 찾는다. [[blog-images-agy-only]]
