# SEO 글 페이지: 맥락

Last Updated: 2026-10-05 (구현과 리뷰 반영 끝, PR 전)

## 핵심 파일
- 새 페이지: `landing/notes/pdrn-cream-reviews.html` (cleanUrls라 주소는 `/notes/pdrn-cream-reviews`)
- 참고만 하는 파일: `landing/concept.html` (글꼴, 색, 계측 코드 모양). 이 PR에서 수정하지 않음
- `landing/vercel.json`: cleanUrls false(2026-10-05, 소유 확인 파일 때문), rewrites로 `/concept`, `/privacy`, `/notes/:slug` 연결, trailingSlash false, `/` → `/concept` 리다이렉트
- `scripts/check_taxonomy.py`: `PAGES_GLOB = "landing/*.html"`이라 하위 폴더를 못 봄. 여러 페이지의 코드를 합쳐서 events.csv와 대조함
- `docs/taxonomy/events.csv`, `docs/taxonomy/README.md`(4.2 view 이벤트 원칙, 6절 5문항)
- `landing/privacy.html` 1절 수집 항목

## 글 원본
노션 진행 현황 → "SEO 단계별 할 일" → "사이트 글 초안 v3". 숫자와 표현은 최종 기획안 "공통 사실 표"를 따름. 지원 님 숫자 대조는 아직

## 계측 설계
- 글 페이지 공통 속성은 콘셉트와 같은 키: UTM 다섯 개, round, variant, landing_page는 `(none)`, debug일 때 is_test
- `note_view`: 글 페이지 조회(1회). 글로 온 사람 수의 분모
- `note_link_click`: 콘셉트 링크 클릭. 속성 `target`(지금은 `concept`)
- 콘셉트로 넘어간 뒤는 `/concept`의 `landing_view`에 `utm_source=notes`로 잡힘

## 정해진 값
- 사이트 주소: https://seongbun-dotbogi.vercel.app
- Amplitude 키는 공개 브라우저 키(concept.html과 같은 값)
- 대표 검색어: pdrn 크림 후기
