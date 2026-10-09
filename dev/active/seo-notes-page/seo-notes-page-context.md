# SEO 글 페이지: 맥락

Last Updated: 2026-10-08 (스레드 글 4개 게시, 링크 위치 관찰, 말투 변경, AI 검색 기준선, PageSpeed 수정)

## 운영 상태
- 글: https://seongbun-dotbogi.vercel.app/notes/pdrn-cream-reviews (2026-10-05 PR #27). 검색 허용
- 구글 서치 콘솔(URL 접두어 속성)과 네이버 서치어드바이저 등록, sitemap 제출, 색인 요청 끝(2026-10-05)
- 소유 확인 파일: `landing/google2e9047ca9cc0e9f7.html`, `landing/naver8ad44ea19e0d116fef037d4373ef854e.html`(지우면 소유 확인이 풀림)

## 핵심 파일
- 글 페이지: `landing/notes/pdrn-cream-reviews.html`
- `landing/vercel.json`: cleanUrls false(2026-10-05, 소유 확인 파일 때문), rewrites로 `/concept`, `/privacy`, `/notes/:slug` 연결, trailingSlash false, `/` → `/concept` 리다이렉트. 새 페이지를 만들면 rewrites에 주소를 더함
- 참고만 하는 파일: `landing/concept.html`. 광고가 10/9 17:00까지 돌아 수정하지 않음
- `scripts/check_taxonomy.py`: `landing/**/*.html`(숨김 폴더 제외)을 합쳐서 events.csv와 대조
- `docs/taxonomy/events.csv`, `docs/taxonomy/README.md`(4.2 예외: 페이지 종류가 다르면 view를 따로 둠)
- `landing/privacy.html` 1, 2, 11절(2026-10-05 개정)

## 글 원본과 근거
- 노션 진행 현황 → "SEO 단계별 할 일" → "사이트 글 원고 (/notes/pdrn-cream-reviews)". 숫자와 표현은 최종 기획안 "공통 사실 표"를 따름. 지원 님 숫자 대조는 아직
- 키워드 시트: 같은 행 안 "키워드 시트 (SEO 1단계)". 사이트 대표 검색어 "pdrn 크림 후기"(구글), 블로그 "화장품 성분표"(네이버)
- 리뷰토픽 비교: PDRN 10개 대 일반 20개(2026-10-04 비교군 확장). PDRN 쪽은 기준에 맞는 제품이 10개뿐이었음
- 글 말투: v1 습니다체 → v2 해요체 → v3 -다체 블로그 말투(원식 피드백 "감정이 없다"). 감정은 지어내지 않고 원식이 고른 두 문장만 넣음

## 계측 설계
- 글 페이지 공통 속성은 콘셉트와 같은 키: UTM 다섯 개, round, variant, landing_page는 `(none)`, debug일 때 is_test
- `note_view`: 글 페이지 조회(1회). 글로 온 사람 수의 분모
- `note_link_click`: 콘셉트 링크 클릭. 속성 `note`, `target`(지금은 `concept`). 같은 탭 이동은 beacon으로 보내고 flush 뒤 이동, 가운데 클릭은 auxclick으로 잡음
- 콘셉트 링크 값: `utm_source=notes&utm_medium=owned&utm_campaign=organic&utm_content=n01`. 스레드 → 글 → 콘셉트로 간 사람은 콘셉트에서 notes로 보이므로 스레드 출처는 앞의 note_view로 이어 봄
- 글 페이지에는 메타 픽셀 없음
- 글 페이지의 글꼴 CSS는 preload와 media=print 전환으로 화면을 막지 않게 불러온다(PR #43, 2026-10-07). /concept는 예전 방식 그대로

## 스레드 운영 (2026-10-05 결정)
- 계정: 성분돋보기 인스타그램 계정을 새로 만들어 스레드 프로필. 가입은 새 구글 계정 이메일로(개인 번호로 가입하면 연락처 추천에 엮임). 10/9까지 페이스북 페이지와 광고에 연결하지 않음
- 스레드 글은 사이트 글로 보냄. 콘셉트 반응은 기대하지 않음(원식). 글 쪽에서 볼 것은 note_view와 색인 여부
- 공개 스레드 글을 보고 정한 방식: 반말 음슴체, 한 줄을 짧게, 첫 줄로 멈추게, 본문은 글만 쓰고 링크는 작성자 댓글, 끝은 질문으로 댓글 유도
- 초안 세 개(수수께끼형, 공감형, 대결형)는 대화에서 원식에게 전달함. 첫 글은 수수께끼형으로 2026-10-05 오전 4시쯤 게시(t01)
- 계정 @seongbun.dotbogi, 소개에는 "개인 학습 프로젝트"를 넣지 않음(원식). 공통 사실 표 "우리를 소개하는 말"을 "브랜드처럼 쓰지 않는 것만 지키고 스레드 소개에는 넣지 않아도 됨"으로 고침. 사이트 글과 콘셉트에는 그대로 밝힘
- 프로필 링크는 사이트 글에 utm_content=bio, 글마다 이어 글 링크는 t01, t02 순서

## 스레드에서 바뀐 것 (2026-10-07~08)
- 링크는 본문이 아니라 작성자 이어 글(댓글)에 둔다. 본문에 넣은 글 3만 조회가 7에 머물렀다
- 조회수는 글을 연 횟수가 아니라 피드에 보인 횟수에 가깝다(메타 도움말 기준, 정확한 세는 기준은 비공개). 결과에는 "노출"로 적는다. 팔로워 0명이라 조회는 전부 추천 피드에서 나오고 올린 직후에 몰린 뒤 거의 늘지 않는다
- 말투: 음슴체가 스레드에서는 AI 글처럼 보인다는 원식 의견으로 말하듯 쓰는 반말(~했어, ~더라, ~거든)로 바꿈. 실제 스레드 글 15개쯤을 원식 크롬으로 읽고 확인함. 원식 본인의 피부나 사용 경험은 지어내지 않는다
- 사이트 유입(Amplitude, 10/8 12시): t01 2명, t02 1명, t03 0명, t04 0명. 프로필 링크(bio)는 첫 글 전에 우리가 확인한 것으로 봄

## 정해진 값
- 사이트 주소: https://seongbun-dotbogi.vercel.app
- Amplitude 키는 공개 브라우저 키(concept.html과 같은 값)
