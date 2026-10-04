# SEO 글 페이지: 계획

2026-10-05 원식 승인. 노션 진행 현황 "SEO 단계별 할 일"의 3단계(기술 항목 16~25번)를 한 PR로 만든다.

## 목표
노션 "사이트 글 초안 v3"를 `/notes/pdrn-cream-reviews` 페이지로 올리고, 검색 엔진이 읽고 등록할 수 있게 기술 항목을 갖춘다.

## 지키는 조건
- `/concept`(`landing/concept.html`)는 수정하지 않는다. 광고가 10/9 17:00까지 돈다
- 글 페이지에는 메타 픽셀을 넣지 않는다
- 브랜치 → PR → 미리보기 확인 → 원식 "머지"

## 만들 것
1. `landing/notes/pdrn-cream-reviews.html`: v3 본문(글자가 HTML에 그대로), 콘셉트 페이지와 같은 글꼴과 색
2. 같은 파일 head: title, description, canonical, og 태그, 구조화 데이터(Article, WebSite, Organization). 검색 허용
3. `landing/robots.txt`: 전체 허용 + sitemap 위치
4. `landing/sitemap.xml`: 새 글 주소 하나
5. `landing/favicon.ico`: 로고로 만듦
6. og 이미지 1200x630
7. 계측: `note_view`, `note_link_click`(속성 `target`)
8. 택소노미: events.csv 행, README 4.2 예외와 변경 기록
9. `scripts/check_taxonomy.py`: `landing/` 하위 폴더 페이지도 검사(테스트 먼저)
10. `landing/privacy.html`: 수집 항목에 글 페이지 조회와 링크 클릭 추가

## 결정 (2026-10-05, 원식 "추천대로")
- A. 콘셉트 링크: `?utm_source=notes&utm_medium=owned&utm_campaign=organic&utm_content=n01`
- B. 새 이벤트 `note_view`, `note_link_click`. README 4.2에 "페이지 종류가 다르면 view를 따로 둔다" 예외
- C. `/`는 지금처럼 `/concept`로 넘김
- D. 글 페이지에 메타 픽셀 없음

## 순서
1. dev docs
2. 점검 스크립트 테스트 → 수정
3. 택소노미 문서 → 글 페이지 → robots, sitemap, favicon, og 이미지 → 처리방침
4. 로컬 점검, 코드 리뷰 에이전트
5. PR, 미리보기에서 `&debug=1`, 모바일, 구조화 데이터 확인
6. 원식 머지
7. 머지 뒤 Amplitude 트래킹 플랜 동기화, 서치 콘솔과 서치어드바이저 등록(원식 로그인), 소유 확인 파일 PR
