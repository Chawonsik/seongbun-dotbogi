# 광고 이름과 UTM 규칙 변경: 맥락

Last Updated: 2026-10-02

## 핵심 파일
- `landing/concept.html`: 머리의 `HERO`(그림 값으로 사진 고르기), `COMMON`(utm_term 추가), utm_content 정규식(round, variant)
- `docs/taxonomy/events.csv`: utm_term 행 추가, utm_campaign, utm_content, round, variant, landing_page 값 예시와 메모
- `ads/README.md`: 이름 규칙, 낱말 뜻, 광고 관리자에 넣을 값과 링크
- `docs/tracking-plan-draft.md`: 노션 계측 설계의 사본. UTM 절

## 결정
- 광고 이름은 요소별로 적는다: `img_그림_text_글_차수_버전`. 구분은 모두 밑줄. 영상을 쓰게 되면 맨 앞이 `vid`
- 차수 표기는 `r1`, `r2` 그대로. 글은 `copy` 가 아니라 `text`
- 나라(`kr`)는 넣지 않는다. 한국만 한다. `ua`(신규 유입)는 강사님 예시에 있어 남긴다
- 캠페인 이름 끝에 시작일(YYMMDD). 버전은 광고 이름에만 둔다
- variant는 A와 B가 다른 쪽의 값: 글이 `common` 이면 그림 값(1차), 아니면 글 값(2차)
- 광고 세트 이름은 `utm_term` 으로 받는다(광고 세트를 구분하는 자리로 쓴다)
- 예전 값으로 쌓인 Amplitude 데이터는 테스트뿐이라 옮기지 않는다. 분석은 캠페인 기간만 본다

## 의존
- 코드는 UTM 값을 소문자로 바꾸고 60자에서 자른다. 가장 긴 이름은 35자
- 택소노미 점검(`scripts/check_taxonomy.py`)은 COMMON 키와 events.csv를 대조한다. 값 목록은 대조하지 않아 사람이 맞춘다
- 게시일이 바뀌면 캠페인 이름과 링크의 utm_campaign을 같이 바꾼다
