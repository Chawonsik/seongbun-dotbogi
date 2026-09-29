# 성분돋보기 2차 설계 스펙 (유행 성분 지도)

작성 2026-09-28, 2026-09-29 3판. 1판에 원식 차 님 검토 댓글 10건과 "크롤링 전 결정" 댓글을 반영한 2판에서, 상세 수집 방식을 Playwright 자동화에서 **사람이 여는 반자동(북마클릿)** 으로 바꿨다(3판, 2026-09-29 결정).
원 기획: 노션 "성분 이름 마케팅은 실제로 통하는가 (피드백 요청)" (2026-09-23). 설계와 결정의 기준은 노션 결정 로그다.

## 1. 기준선: 이미 운영 중인 것

저장소 `github.com/Chawonsik/seongbun-dotbogi`, 운영 주소 `https://seongbun-dotbogi.vercel.app` (Vercel 프로젝트 `ingredient-lens`, 계정 wonsikcha12@gmail.com). 광고 심사를 통과했고 저장소 `main` 과 배포본이 같다(2026-09-28 확인).

현재 랜딩(`landing/index.html`, 정적 한 장 + `data.json` fetch)이 이미 갖춘 것:

- 성분 칩 → 큰 숫자("N개 중 k개가 뒤쪽 절반") → 점 띠(상대 위치) → 제품 검색(부분 문자열 자동완성, 6개) → 결과 카드 → 규칙 칩 3개 → 접힌 설명 → 푸터
- 전성분 붙여넣기(브라우저 안 계산, 계열 사전 `FAM` 11개, 1% 경계 사전 `ONE`)
- 계측: `window.SD_CONFIG` 의 GA4 `G-6N4SF70RFR`, 픽셀 `1547670487046797`. 이벤트 `chip_click`, `product_select{found}`, `paste_run`, `engaged_60s`, 모든 이벤트에 `frame`(utm_content). 60초 체류는 보이는 시간만 누적, "못 찾음"은 blur 시 1회. 픽셀 `ProductSelect` 는 found=1 만
- `/privacy` 페이지, 문의 이메일, "개인 학습 프로젝트" 고지
- 데이터: 2026-09-18 PDRN 파일럿 6개(`version: 2026-09-23-pilot`)

이번 작업은 **이 랜딩을 같은 주소에 덮어쓰는 것**이다. 위 항목 중 계측 ID, 이벤트 이름, 두 계측 수정, `/privacy` 는 그대로 가져간다.

## 2. 이번 범위

1. 검색 수집(자동): 후보 성분 18개의 검색 결과 전체. 제품 수, 등록 시점, 앞 6개 성분이 들어 있어 성분 확정과 "이름 성분이 앞 6개 안에 있나" 계산에 쓴다. 상세 페이지 불필요
2. 유행 성분 확정: 기준은 숫자를 보기 전에 고정. 제품명에 성분 이름을 단 제품 수(단종 제외) 상위 9개 + 히알루론산(비교 기준). 이름 단 제품이 15개 미만인 성분은 제외. 등록 증가율은 설명용
3. 전성분 수집(반자동): 확정 성분 10개 x 성분당 20~50개(총 200~500개)를 팀원 둘이 나눠 브라우저에서 연다. 북마클릿이 페이지의 전성분을 브라우저에 모았다가 마지막에 한 번 JSON 으로 내보내고, 스크립트가 그 파일을 raw 형식으로 들여온다. 북마클릿 점검은 PDRN 3개로 먼저
4. 파생 데이터: 기존 `data.json` 스키마를 유지하며 채움. 위치 지표는 상대 위치 기준. 지금 랜딩의 PDRN 6개도 새 방식으로 다시 확인
5. 랜딩 갱신: 실험 노트 톤 + 로고 팔레트로 재스타일, 칩 확장, 초성 자동완성, 문구 중립화. 계측과 privacy 유지
6. 광고 소재: 성분을 특정하지 않는 공통 이미지 3규격. 문장은 Meta 본문에 넣으므로 이미지에는 넣지 않음. 제작은 수집이 끝나 숫자가 확정된 뒤

범위 밖: 광고 집행, 도메인 구매, 리뷰 태그 수집. 화해 데이터 제공 요청은 병행해서 보내되 결과를 기다리지 않는다.

## 3. 확정된 결정

| 항목 | 결정 | 근거 |
|------|------|------|
| 제품 선정 | 성분별 검색 결과의 **기본 정렬(랭킹) 상위**. 전성분 수집은 확정 성분당 20~50개 | 리뷰 수 상위는 오래된 인기 제품에 치우침 |
| 수집 규모 | 검색은 18개 전체. 전성분은 확정 10개 x 20~50개. 북마클릿 점검은 PDRN 3개 | 사람이 여는 규모 |
| 상세 수집 방식 | **사람이 브라우저에서 열고 북마클릿으로 모음.** Playwright 등 자동 조작과 봇 감지 우회는 쓰지 않음 | 화해 WAF 가 자동 접근을 막고 있고, 위장해서 넘는 것은 하지 않기로 결정(2026-09-29) |
| 성분 확정 기준 | 이름 단 제품 수(단종 제외) 상위 9개 + 히알루론산. 15개 미만 제외. 증가율은 설명용 | 숫자 보기 전에 고정(2026-09-29) |
| 수집 날짜 | 검색과 상세 모두 수집 시각을 기록 | 랭킹은 날마다 바뀜 |
| 단종 기록 | `obsolete` 표시 제품 제외 | 옛 기록은 성분이 절반쯤 비어 있음 |
| 후보 성분 | 아래 4.1 의 18개. 알로에와 녹차는 제외 | 선정 기준은 수집 뒤 결정 |
| 각질 산 묶음 | 아하, 바하, 파하, 라하를 한 후보로. 성분표에서 처음 나오는 산이 이름 성분. 제품명의 산 종류는 따로 기록 | 라하(카프릴로일살리실릭애씨드)가 바하와 글자가 겹치지만 한 묶음이라 무방 |
| 작업 방식 | 저장소에서 브랜치로 작업하고 PR 로 `main` 에 합침 | 원식 차 님 결정 |
| 위치 지표 | 상대 위치 = (순번 - 1) / (전체 성분 수 - 1). 기존 코드의 `pct()` 와 같음 | 성분 수가 제품마다 달라 절대 순번은 비교 불가 |
| 공개 파일 | 리뷰 수, 평점 미수록 | 파생값 이상을 공개하지 않음. 평점은 제품 비교로 읽힘 |
| 광고 문장 위치 | Meta 기본 문구(본문)에 A/B/C. 이미지와 헤드라인은 세 프레임 동일 | 문장만 비교됨. 문장 수정에 이미지 재제작 불필요 |
| 광고 이미지 | 성분을 특정하지 않는 중립 그림 1종 x 3규격. "화해" 미표기 | 강사 피드백, 결정 로그, Meta 제3자 상표 |
| 화해 표기 | 랜딩 본문과 광고에서 "화해" 미언급. 출처는 푸터에만 | 결정 로그 |
| 시각 톤 | 실험 노트: 크림 `#fdfbf9`, 차콜 `#3d4149`, 강조 장미 `#c9605f`, 선택 칩 `#d98b8b`, 보조 분홍 `#f3c9c4`, 세이지 `#a9b8a0`. 본문 Pretendard, 숫자 IBM Plex Mono. 로고 `assets/logo.webp` | 2026-09-28 시각 비교로 선택 |
| 이벤트 이름 | 기존 유지(`chip_click`, `product_select`, `paste_run`, `engaged_60s`) | Meta 전환 설정을 안 건드림 |
| 1% 경계 | 기존 `ONE` 목록 유지, "추정" 표기 | |

## 4. 크롤러

### 4.1 후보 성분 `config/ingredients.json`

```json
[
  {
    "key": "PDRN", "label": "PDRN", "family": "PDRN 계열",
    "search_terms": ["PDRN"],
    "name_patterns": ["pdrn", "피디알엔"],
    "inci_patterns": ["디엔에이", "폴리데옥시리보뉴클레오타이드", "sodium dna"]
  }
]
```

| key | label | name_patterns(제품명) | inci_patterns(전성분) | 비고 |
|-----|-------|------|------|------|
| PDRN | PDRN | pdrn, 피디알엔 | 디엔에이, 폴리데옥시리보뉴클레오타이드 | "소듐디엔에이" 대신 "디엔에이"로 누락 감소 |
| retinoid | 레티놀 계열 | 레티놀, 레티날, 레티닐 | 레티놀, 레티날, 레티닐, 하이드록시피나콜론레티노에이트 | 결과를 말할 땐 "레티노이드 계열" |
| niacinamide | 나이아신아마이드 | 나이아신아마이드, 나이아신 | 나이아신아마이드 | |
| exosome | 엑소좀 | 엑소좀 | 엑소좀 | "세포배양액" 제외(범위 과대). 못 찾은 제품은 수동 확인 목록 |
| peptide | 펩타이드 | 펩타이드, 펩티드 | 펩타이드 | |
| glutathione | 글루타치온 | 글루타치온, 글루타티온 | 글루타치온, 글루타티온 | |
| panthenol | 판테놀 | 판테놀 | 판테놀 | |
| cica | 시카 계열 | 시카, 센텔라, 병풀 | 병풀, 센텔라, 아시아티코사이드, 마데카소사이드, 아시아틱애씨드, 마데카식애씨드 | |
| vitc | 비타민C 유도체 | 비타민c, 비타민씨 | 아스코빅, 아스코빌, 아스코르빌 | |
| collagen | 콜라겐 | 콜라겐 | 콜라겐 | |
| ceramide | 세라마이드 | 세라마이드 | 세라마이드 | |
| houttuynia | 어성초 | 어성초 | 약모밀, 어성초 | 성분표 이름은 약모밀추출물 |
| tranexamic | 트라넥사믹애씨드 | 트라넥사믹, 트라넥삼 | 트라넥사믹, 트라넥삼 | |
| azelaic | 아젤라익애씨드 | 아젤라익, 아젤라산 | 아젤라익, 아젤라 | |
| bakuchiol | 바쿠치올 | 바쿠치올 | 바쿠치올 | |
| spicule | 스피큐 | 스피큐, 스피큘 | 스피큘, 해면, 스펀지 | 하이드롤라이즈드스펀지 등. 파일럿에서 확인 |
| acids | 각질 산(아하, 바하, 파하, 라하) | 아하, 바하, 파하, 라하, aha, bha, pha, lha | 글라이콜릭애씨드, 락틱애씨드, 만델릭애씨드, 살리실릭애씨드, 베타인살리실레이트, 글루코노락톤, 락토바이오닉애씨드, 카프릴로일살리실릭애씨드 | 처음 나오는 산이 이름 성분. `acid_in_name`(제품명의 산 종류)을 따로 기록 |
| ha | 히알루론산 | 히알루론, 하이알루론 | 하이알루로, 히알루로 | 비교 기준(늘 있던 성분) |

패턴은 소문자, 공백 제거 후 부분 문자열 비교. 파일럿 결과를 보고 보정한다. 검색어가 여러 개인 성분은 검색어별 랭킹을 번갈아 합쳐 후보 순위를 매긴다(2026-09-29 결정). 기존 `index.html` 의 `FAM` 사전은 이 파일에서 생성해 `data.json` 최상위 `family_dict` 로 싣고, 클라이언트는 그것을 읽는다(사전을 한 곳에만 둔다).

### 4.2 검색 수집 `crawler/search.py`

- 2026-09-18 실측에서 검색 API가 브라우저 밖에서 인증 오류(code 2100)를 낸 원인은 헤더 누락이었다. 2026-09-28 확인: 사이트가 비로그인 상태에서 보내는 세 헤더를 그대로 붙이면 `requests` 로도 200 이 온다
  - `GET https://gateway.hwahae.co.kr/v14/search/products/text?orderType=ranking&pageNum={n}&query={term}`
  - 헤더 `hwahae-user-id: anonymous`, `hwahae-device-id: anonymous`, `Authorization: Bearer ` (값이 빈 Bearer). 셋 중 하나라도 빠지면 401
  - 위 익명 헤더 세 개에 프로젝트를 밝히는 정직한 User-Agent(`seongbun-dotbogi-research/0.1 (...)`)만 보낸다. 브라우저 UA 와 Origin, Referer 는 보내지 않는다(2026-09-29 결정)
  - `pageNum` 은 0부터, 페이지당 20개, `pageNum=n` 이 `offset=20n`. 응답 `meta.pagination.total_count` 가 전체 결과 수
  - 항목 필드: `id`, `brand`(표시명), `brand_name`, `productName`, `obsolete`, `sale`, `updateTime`(epoch 초), `reviewCount`, `rankOrder`, `product_capacity`, `product_price`, `product_ingredients`(앞 6개만이라 전성분으로 쓸 수 없음)
- 따라서 **Playwright 없이 `requests` 로 페이지를 순서대로 받는다.** 결과 순서가 랭킹이므로 목록 안의 순번을 `rank_index` 로 저장한다
- 각 후보 성분마다 `total_count` 까지 받는다(등록 시점 분포에 필요). 상한 250페이지(5,000개). 상한에 걸리면 `capped: true`. 요청 간격 3초, 5xx 나 연결 오류는 10초 후 재시도 2회
- 출력 `data/raw/search/{key}.jsonl`: 응답 원문 한 줄씩(페이지 번호, 수신 시각 포함). `data/raw/search/{key}.meta.json`: 검색어, 전체 결과 수, 페이지 수, capped, 수집 시각
- 멱등: meta 파일이 있고 `--force` 가 없으면 건너뜀

요청 수 추정(댓글 10 반영): 페이지당 20개. PDRN 1,813개 → 91회, 레티놀 약 3,400개 → 170회. 18개 성분 합계 약 2,500회(상한 250페이지 적용), 3초 간격이면 약 2시간. 한 번만 하면 된다. 상세 수집은 별도로 최대 270회.

### 4.3 유행 성분 확정 `crawler/trend.py`

기준은 숫자를 보기 전에 고정했다(2026-09-29). 스크립트는 표와 제안을 만들고 사용자가 `config/ingredients.json` 의 `selected` 로 확정한다.

- 성분마다 검색 결과에서 `name_patterns` 에 맞고 `obsolete` 가 아닌 제품을 센다: `named_total`, `recent_24m`, `prior_24m`, `growth = recent_24m / max(prior_24m, 5)`, `capped`, `incomplete`
- 검색 응답의 `product_ingredients`(앞 6개 성분, 표기 순서)로 `top6_hit` = 이름 성분의 `inci_patterns` 이 앞 6개 안에 있는 제품 수, `top6_rate = top6_hit / named_total`. 상세 페이지 없이 수천 개 전체에서 잰다
- 제안 규칙 `propose_selection`: `named_total >= 15` 인 성분을 `named_total` 내림차순으로 9개 + `ha`(히알루론산, 비교 기준). 잘린(`capped`) 성분은 `named_total` 이 상한 안에서 센 값이라 표에 `*` 로 표시
- 출력 `data/derived/trend.csv` 와 콘솔 표. `proposed` 열에 제안 여부

### 4.4 전성분 수집(반자동): 링크 페이지, 북마클릿, 들여오기

Playwright 로 제품 페이지를 여는 방식은 쓰지 않는다. 화해 WAF 가 자동 조작 브라우저를 막고, 그것을 위장해서 넘는 것은 하지 않는다.

- `python crawler/run.py links --top-n 30`: 확정 성분마다 검색 결과에서 `select_candidates` 로 상위 N 개를 고르고 `data/derived/candidates.json`(key 별 후보 목록)과 `data/derived/collect-links.html` 을 만든다. HTML 에는 (1) 북마클릿 두 개를 북마크바로 끌어다 놓는 설치 칸, (2) 성분별 제품 링크(새 탭, 브랜드와 제품명, 랭킹 순번), (3) "검증" 묶음으로 지금 랜딩 `data.json` 의 제품 6개. `--only PDRN --top-n 3` 이면 점검용 3개만
- 북마클릿 "성분 수집" (`tools/bookmarklet/collect.js`): 제품 페이지에서 `#__NEXT_DATA__` 를 읽어 `productIngredientInfoData.ingredients` (id, korean, english, ewg, purposes) 와 제품 번호(`productReviewSummaryData.productMetaData.productIndex`, 없으면 JSON 안의 `productIndex` 또는 `product_id`, 그리고 URL 의 goods 번호)를 뽑아 그 사이트의 `localStorage["sd_collect"]` 에 제품 번호를 키로 모은다. 화면 구석에 "저장 n개" 를 띄우고 **다음 페이지로 이동하지 않는다**. 같은 제품을 다시 누르면 덮어쓴다
- 북마클릿 "수집 내보내기" (`tools/bookmarklet/export.js`): `localStorage["sd_collect"]` 전체를 `sd-collect-YYYYMMDD-HHMM.json` 으로 내려받는다. 내려받은 뒤 비울지 묻는다
- `python crawler/run.py ingest 파일.json`: 내보낸 JSON 을 읽어 각 레코드를 `data/derived/candidates.json` 과 대조해 `key` 와 `candidate` 를 붙이고 `data/raw/products/{key}__{id}.json` 으로 저장한다(형식은 아래). 제품 번호가 없으면 goods 번호를 검색 결과의 `goods[].id` 로 맞춘다. 후보 목록에 없는 제품은 `key: "verify"` 로 저장(랜딩 검증용). 같은 제품이 두 성분의 후보이면 각각 저장
- raw 형식: `{"id", "key", "candidate", "ingredients": [{"id","korean","english","ewg","purposes"}], "final_url", "collected_at"}`. 전성분 원문은 여기에만

작업 분담: 링크 페이지의 성분별 묶음을 둘이 나눠 연다. 성분당 20~30개면 한 명당 100~150 페이지, 페이지당 10초 안팎.

### 4.5 파생 계산 `crawler/derive.py`

제품마다(기존 스키마 유지):

- `pos`: `inci_patterns` 이 처음 맞는 성분의 순번(1부터). 각질 산 묶음은 어느 산이든 처음 나오는 것. 없으면 제품을 `data/derived/unmatched.csv` 로 보내고 공개 파일에서 제외(기존 규칙 "확인 전이라 뺐습니다")
- `total`: 전성분 개수
- `boundary`: `config/one-percent-markers.json`(기존 `ONE` 목록) 중 첫 등장 순번, 없으면 null
- `families`: 모든 후보 성분 사전으로 찾은 `{name, pos, top}`. `top` 은 `boundary` 앞이면 true
- `price_per_ml`: 가격 / 용량(ml). 용량이 ml 나 g 가 아니면 null
- `registered`: `updateTime` 을 YYYY-MM-DD 로
- `collected_at`: 북마클릿이 기록한 수집 시각(YYYY-MM-DD)

성분마다: `key, label, category, n_products, common`(전부에 든 성분, 화해 성분 번호로 교집합), `note`, `median_rel`, `back_half`, `low_zone`. `top6_rate` 는 검색 전체 기준으로 `trend.csv` 에서 가져와 함께 싣는다.

전체: `version`, `source`, `family_dict`(계열 사전), `one_percent_markers`.

출력: `landing/data.json`, `data/derived/unmatched.csv`, `data/derived/family_matches.csv`(계열별 실제 걸린 성분 번호와 이름). 리뷰 수, 평점, 전성분 원문은 넣지 않는다. `key: "verify"` 레코드는 공개 파일에 넣지 않고 `data/derived/verify.csv` 로 지금 랜딩 값과 비교표만 만든다.

### 4.6 실행 순서

```bash
python crawler/run.py search                 # 후보 18개 검색 전체 (약 2시간, 1회, 05:00 KST 회피)
python crawler/run.py trend                  # trend.csv + 제안 → 사용자가 selected 표시
python crawler/run.py links --only PDRN --top-n 3   # 북마클릿 점검용 3개
#   사람이 열고 북마클릿으로 모아 내보낸 뒤
python crawler/run.py ingest sd-collect-....json
python crawler/run.py derive                 # 매칭 점검. 이상 없으면
python crawler/run.py links --top-n 30       # 확정 10개 x 30개 링크 페이지 → 둘이 나눠 수집
python crawler/run.py ingest ...; python crawler/run.py derive
```

## 5. 랜딩 변경

기존 `landing/index.html` 을 고친다. 새로 만들지 않는다.

### 5.1 유지

- `SD_CONFIG` 두 ID, 계측 로더, `track()`, 60초 체류 누적 방식, blur 시 "못 찾음" 1회, 이벤트 이름
- `/privacy`, 푸터 문의와 고지, `vercel.json`
- 큰 숫자 방식("N개 중 k개가 뒤쪽 절반"), 점 띠 상대 위치, 접근성 처리(aria, 히트 영역, 포커스 유지)
- 붙여넣기 뒷문 로직. 단 `FAM` 과 `ONE` 은 `data.json` 에서 읽도록 교체

### 5.2 바꾸는 것

- 스타일: CSS 변수를 실험 노트 팔레트로 교체(다크 모드 변수도 같이). 서체 Noto → Pretendard + IBM Plex Mono(숫자). 헤더에 로고 이미지. 레이아웃 폭과 구조는 유지
- 칩: 확정 성분 8~10개 전부. "다른 성분은 곧 추가됩니다" 문구 제거. 기본 선택은 URL `ing` 파라미터, 없으면 첫 번째
- 제목: `h1` 을 "{성분} {카테고리}, 이름값은 몇 번째?" 에서 세 광고 프레임에 중립인 문장으로. 후보 "{성분} 제품 {k}개, 이름 성분은 어디에 있을까". 문구 최종안은 사용자 확인
- 태그 줄: "전성분 표기 순서 기준" 유지. 본문 어디에도 "화해" 없음. 출처 문구는 푸터 `#source` 만
- 자동완성: 기존 부분 문자열 매칭에 **초성 매칭** 추가(입력이 전부 자음이면 초성으로 비교). 최대 8개. 선택 성분 제품을 먼저, 다른 성분 제품은 성분 라벨과 함께 아래
- 관찰 글: "가격과 위치", "리뷰 수의 함정" 은 PDRN 6개 기준 문장이라 새 데이터와 맞지 않으므로 제거. "어떻게 셌나" 와 "모두에 든 성분" 은 유지. 새 관찰 글은 수집 결과를 본 뒤 별도 결정
- 규칙 칩 3개 중 "리뷰 수엔 리뉴얼 전 것이 섞임" 은 리뷰 수를 더는 다루지 않으므로 제거

### 5.3 작업 방식과 배포

- 모든 작업은 브랜치에서 하고 PR 로 `main` 에 합친다. 크롤러, 랜딩, 광고를 각각 별도 PR 로 나눈다
- 사용자(또는 원식 차 님)가 `main` 에 머지하면 Vercel 이 자동 배포한다고 가정. 자동 배포가 아니면 Vercel CLI 로 같은 프로젝트에 배포. 배포 전 로컬 확인은 `python -m http.server` 로 `landing/` 을 띄워 375px 첫 화면, 검색, 붙여넣기, 콘솔 오류 0 을 본다
- 배포 후 `data.json` 200, `/privacy` 200, GA4 실시간에 `chip_click` 이 잡히는지 확인

## 6. 광고 소재

### 6.1 구성

Meta 광고 한 개 = 이미지 + 기본 문구(본문) + 헤드라인. 세 프레임은 **본문만** 다르다.

- 이미지(공통 1종 x 3규격): 로고, 태그 "전성분 실측", 점 띠. 점 띠는 **확정 성분 전체의 상대 위치를 합친 분포**(성분과 제품을 특정하지 않음)와 장미색 점 하나. 글자는 태그와 축 라벨("앞쪽", "맨 끝")뿐. 브랜드, 제품명, 성분명, "화해" 없음
- 헤드라인(공통): "내 제품은 몇 번째?"
- 버튼(공통): 더 알아보기
- 본문(프레임별): `ads/copy.json` 의 A/B/C

### 6.2 문구 `ads/copy.json`

원 문서 예시를 자리로 두되, **광고는 수집이 끝나 확정 숫자가 나온 뒤에만 만든다**. 예시값으로 렌더한 소재는 제출 후 못 고친다.

- A(성분 이름): "유행 성분 {n}가지, 제품 {N}개를 뜯어봤습니다" → n, N 은 `data.json` 에서
- B(함량 위치): "이름에 넣은 성분이 성분표 몇 번째인지 세어봤습니다" → 숫자가 없어 세기가 다르다는 지적. "{N}개 제품에서 이름 성분이 성분표 몇 번째인지 세어봤습니다" 처럼 같은 숫자를 넣을지 사용자 결정
- C(리뷰 언어): "'흘러내려요' 1,665건" 은 한 제품의 태그 수라 층이 다르고 이번 수집에 리뷰 태그가 없다. **[미정]**. 여러 제품을 합친 수치가 필요하며 별도 수집 결정 후 채운다
- 세 문장의 세기 맞추기(수강생 설문)는 원 문서의 [미정] 그대로

### 6.3 템플릿과 렌더

- `ads/template.html?size=square|feed|story`: `../landing/data.json` 을 fetch 하지 못하므로(`file://`) 렌더 스크립트가 `data.json` 을 읽어 `window.SD_DATA` 로 주입한 뒤 캡처한다
- `ads/render.py`: Playwright 로 1080x1080, 1080x1350, 1080x1920 캡처 → `ads/out/common_{size}.png`. 폰트는 `document.fonts.ready` 대기
- 색과 서체는 랜딩과 동일

## 7. 폴더 구조(저장소 안)

```
seongbun-dotbogi/
  config/ingredients.json          후보 18개, selected 표시
  config/one-percent-markers.json  기존 ONE 목록
  crawler/
    config.py  schedule.py  match.py  hwahae_api.py  search.py  select.py
    trend.py  links.py  ingest.py  derive.py  run.py
    requirements.txt  tests/
  tools/bookmarklet/collect.js  export.js   북마클릿 원본(읽기 쉬운 형태)
  data/raw/search/{key}.jsonl      git 제외
  data/raw/products/{key}__{id}.json  git 제외 (북마클릿 내보내기를 ingest 로 변환)
  data/raw/errors.log              git 제외
  data/derived/trend.csv  candidates.json  collect-links.html  unmatched.csv  family_matches.csv  verify.csv
  landing/index.html  privacy.html  data.json  vercel.json  README.md
  ads/template.html  copy.json  render.py  out/(git 제외)
  assets/logo.webp
  docs/superpowers/specs/          이 문서
  dev/active/                      작업 기록
```

`.gitignore` 는 이미 `data/raw/`, `ads/out/`, `.superpowers/` 를 제외한다.

## 8. 오류 처리

- 검색 수집: 응답 가로채기가 60초 동안 새 페이지를 못 받으면 그 성분을 끝난 것으로 보고 다음으로. 페이지 수와 마지막 상태를 로그
- 들여오기: 레코드에 전성분이 없거나 제품 번호를 못 맞추면 건너뛰고 `data/derived/ingest-skipped.csv` 에 남김. 끝에 저장/건너뜀 개수 출력
- 북마클릿: 제품 페이지가 아니거나 전성분이 없으면 화면에 이유를 띄우고 저장하지 않음
- derive: 필수 키가 없는 raw 파일은 건너뛰고 경고. `unmatched.csv` 개수 출력
- 랜딩: 기존 실패 문구 유지("데이터를 불러오지 못했습니다")
- 광고 렌더: 데이터 주입 실패 시 중단

## 9. 테스트

- `crawler/tests/`: 이름 패턴 필터, 단종 제외, 위치 매칭, 1% 경계, 상대 위치와 중앙값, 증가율과 top6 계산, 선정 제안 규칙, 검색 응답 파싱(저장한 응답 픽스처), 링크 페이지 생성, 내보내기 JSON 들여오기(픽스처)
- 랜딩: 초성 변환과 자동완성 매칭을 순수 함수로 두고 Node 로 실행하는 `landing/tests/`. 화면은 Playwright 로 칩 선택, 검색, 붙여넣기 시나리오 1개씩과 콘솔 오류 0
- 광고: 3장 파일 존재와 크기

## 10. 약관과 원칙

- 전성분 원문은 `data/raw/` 에만. git, 랜딩, 광고 어디에도 없음
- 공개 파일에는 파생값과 검색용 제품명, 브랜드만. 리뷰 수와 평점 없음
- 광고 이미지에 브랜드, 제품명, 성분명, "화해" 없음. 랜딩 본문에도 "화해" 없음. 출처는 푸터
- 요청 간격 3초 이상. 검색 약 2,500회(1회성). 제품 페이지는 사람이 연다. 자동 조작 브라우저와 봇 감지 우회는 쓰지 않는다
- 결과 카드 문장은 관찰만("몇 번째에 있다"). 효능과 품질 판단 없음

## 11. 사용자 확인이 필요한 것(구현 중)

1. trend 표의 제안(이름 단 제품 수 상위 9 + 히알루론산)을 보고 확정 성분 10개 승인
2. 중립 제목 문구
3. B 문구에 숫자를 넣을지
4. C 문구와 리뷰 태그 수집 여부
5. 배포 방식(자동 배포인지)
6. 성분당 전성분 수집 개수(20~50 사이)
