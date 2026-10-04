# SEO 글 페이지: 할 일

## 페이지 만들기 (PR #27)
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
- [x] PR #27, 미리보기 확인(응답 200, 글에서 콘셉트로 넘어가는 흐름, debug 전달). 리뷰 뒤 비교 막대그래프 추가(원식 요청: 스레드에서 오는 사람은 훑어봄)
- [x] 머지 (원식, 2026-10-05). 운영에서 글은 검색 허용, /concept는 noindex 그대로 확인
- [x] Amplitude 트래킹 플랜 동기화 (2026-10-05: note_view, note_link_click 추가와 설명, note, target(enum concept), landing_page enum에 (none), utm 설명에 notes, owned, n01)

## 검색 엔진 등록 (PR #28)
- [x] 소유 확인 파일 두 개를 landing/에 추가
- [x] cleanUrls가 확인 파일을 308로 넘기는 문제: cleanUrls를 끄고 rewrites로 /concept, /privacy, /notes/:slug 연결. 미리보기와 운영에서 광고 링크 두 개, 첫 화면 사진, 계측 확인
- [x] 머지 (원식, 2026-10-05)
- [x] 구글 서치 콘솔(URL 접두어 속성), 네이버 서치어드바이저 등록과 소유 확인, sitemap 제출, 색인 요청 (원식, 2026-10-05)

## 다음
- [ ] 스레드 계정 (원식): 성분돋보기 인스타그램 계정을 새 구글 계정 이메일로 가입(2026-10-05 진행 중). 페이스북 연결은 "나중에"
- [ ] 스레드 글 (원식): 본문은 글만, 링크는 작성자 댓글에 `?utm_source=threads&utm_medium=social&utm_campaign=organic&utm_content=t01`부터
- [ ] 네이버 블로그 글 (지원)
- [ ] 올린 날: 리치 결과 테스트, PageSpeed, AI 검색 기준선
- [ ] 10/8~9쯤: 구글과 네이버 색인 확인
- [ ] 광고 종료일(10/9): 블로그, 스레드 조회수와 서치 콘솔 숫자 캡처
- [ ] 10/9 뒤: 첫 화면(`/`)을 어떻게 할지(지금은 /concept로 넘어감)

## 반영하지 않은 리뷰 의견
- 홈(`/`)이 noindex인 /concept로 넘어가서 사이트 이름과 파비콘 신호가 약함. 광고가 끝난 10/9 뒤에 첫 화면을 다시 볼 것
- 여러 페이지 코드를 합쳐서 대조하므로 한 페이지가 공통 속성 하나를 빠뜨려도 점검이 못 잡음(기존 설계)
- 크롤러가 JS를 실행하면 note_view가 부풀 수 있음. Amplitude 봇 차단 설정 확인
