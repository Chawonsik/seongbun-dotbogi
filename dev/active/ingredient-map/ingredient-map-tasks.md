# ingredient-map tasks

## 설계
- [x] 1판 스펙 작성, 원식 차 님 댓글 10건 수신 (2026-09-28)
- [x] 2판 스펙: 댓글과 "크롤링 전 결정" 반영
- [x] 실측: 검색 API 익명 헤더, pageNum 규칙, WAF 범위, 제품 페이지 키
- [x] 크롤러 구현 계획 작성

## 크롤러 (docs/superpowers/plans/2026-09-28-crawler.md, 브랜치 feat/crawler)
- [x] Task 1 브랜치, 환경, config 18개
- [x] Task 2 match.py
- [x] Task 3 hwahae_api.py
- [x] Task 4 search.py
- [x] Task 5 select.py
- [x] Task 6 (3판) Playwright 삭제, 북마클릿 2개
- [x] Task 7 (3판) trend.py: 고정 기준 제안, top6_rate
- [x] Task 8 (3판) links.py, ingest.py
- [x] Task 9 (3판) derive.py (verify 표 포함)
- [x] Task 10 (3판) run.py, README, 최종 리뷰 반영, draft PR 생성 (2026-09-29)
- [ ] Task 10 (3판) 사람 점검: PDRN 3개 + 검증 5개 북마클릿 수집 → ingest → derive → verify.csv, top6-check.csv 를 PR 에 추가
- [ ] Task 11 (3판) 본 실행: search 2시간, 성분 확정, 둘이 나눠 200~500 페이지 수집, derive

## 성분 선정
- [ ] trend.csv 검토, 기준과 8~10개 확정, selected 표시, derive

## 랜딩 (계획 별도 작성 예정, 브랜치 feat/landing-v2)
- [ ] 계획 작성
- [ ] 재스타일, 칩 확장, 초성 자동완성, 문구 중립화, 관찰 글 정리
- [ ] 로컬 검증(375px, 검색, 붙여넣기, 콘솔 0), PR, 배포 확인

## 광고 (계획 별도 작성 예정, 브랜치 feat/ads)
- [ ] 계획 작성 (확정 숫자 나온 뒤)
- [ ] 공통 이미지 3규격, copy.json, 렌더
