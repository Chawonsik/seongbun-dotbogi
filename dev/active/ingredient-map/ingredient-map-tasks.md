# ingredient-map tasks

## 설계
- [x] 1판 스펙 작성, 원식 차 님 댓글 10건 수신 (2026-09-28)
- [x] 2판 스펙: 댓글과 "크롤링 전 결정" 반영
- [x] 실측: 검색 API 익명 헤더, pageNum 규칙, WAF 범위, 제품 페이지 키
- [x] 크롤러 구현 계획 작성

## 크롤러 (docs/superpowers/plans/2026-09-28-crawler.md, 브랜치 feat/crawler)
- [ ] Task 1 브랜치, 환경, config 18개
- [ ] Task 2 match.py
- [ ] Task 3 hwahae_api.py
- [ ] Task 4 search.py
- [ ] Task 5 select.py
- [ ] Task 6 product.py (Playwright)
- [ ] Task 7 trend.py
- [ ] Task 8 derive.py
- [ ] Task 9 run.py, README, 소규모 파일럿, PR
- [ ] Task 10 파일럿 본 실행 (search 약 2시간, products 약 20분)

## 성분 선정
- [ ] trend.csv 검토, 기준과 8~10개 확정, selected 표시, derive

## 랜딩 (계획 별도 작성 예정, 브랜치 feat/landing-v2)
- [ ] 계획 작성
- [ ] 재스타일, 칩 확장, 초성 자동완성, 문구 중립화, 관찰 글 정리
- [ ] 로컬 검증(375px, 검색, 붙여넣기, 콘솔 0), PR, 배포 확인

## 광고 (계획 별도 작성 예정, 브랜치 feat/ads)
- [ ] 계획 작성 (확정 숫자 나온 뒤)
- [ ] 공통 이미지 3규격, copy.json, 렌더
