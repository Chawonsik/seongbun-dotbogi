# SEO 글 페이지: 할 일

- [x] 계획 승인 (2026-10-05)
- [x] 브랜치 `feat/seo-notes-page`
- [x] 점검 스크립트: 하위 폴더 테스트 먼저, 그다음 수정. 숨김 폴더(.vercel 등) 제외 테스트와 수정
- [x] events.csv에 note_view, note_link_click(note, target) 행. 공통 속성 값 예시와 Note. README 4.2 예외, 이벤트 패스, 6절, 변경 기록
- [x] 글 페이지 HTML (본문 v3, head, 구조화 데이터, 계측)
- [x] robots.txt, sitemap.xml
- [x] favicon.ico, og 이미지
- [x] 처리방침 1절, 2절, 11절
- [x] landing/README.md 파일 목록
- [x] 로컬 점검(check_taxonomy, 단위 테스트 26개), 브라우저로 데스크톱과 모바일 화면, debug 이벤트 확인
- [x] 코드 리뷰 에이전트: HIGH 없음. MEDIUM 3개(본문 회색 글자 대비, 처리방침 11절 누락, 이전 페이지 주소 수집 누락)와 LOW 대부분 반영
- [ ] PR, 미리보기 확인
- [ ] 머지 (원식)
- [ ] Amplitude 트래킹 플랜 동기화 (note_view, note_link_click, note, target. 값 예시 notes, owned, n01)
- [ ] 서치 콘솔, 서치어드바이저 등록(원식), 소유 확인 파일 PR

## 반영하지 않은 리뷰 의견
- 홈(`/`)이 noindex인 /concept로 넘어가서 사이트 이름과 파비콘 신호가 약함. 광고가 끝난 10/9 뒤에 첫 화면을 다시 볼 것
- 여러 페이지 코드를 합쳐서 대조하므로 한 페이지가 공통 속성 하나를 빠뜨려도 점검이 못 잡음(기존 설계)
- 크롤러가 JS를 실행하면 note_view가 부풀 수 있음. Amplitude 봇 차단 설정 확인
