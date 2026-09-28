# ingredient-map context
Last Updated: 2026-09-28 22:10 KST

## 핵심 파일
- `docs/superpowers/specs/2026-09-28-ingredient-map-design.md`: 2차 설계 스펙(댓글 반영본)
- `docs/superpowers/plans/2026-09-28-crawler.md`: 크롤러 구현 계획(Task 1~10)
- `landing/index.html`: 운영 랜딩. `window.SD_CONFIG` 에 GA4 `G-6N4SF70RFR`, 픽셀 `1547670487046797`. 저장소 main 과 배포본이 같음(2026-09-28 확인)
- `landing/data.json`: 현재 PDRN 6개 파일럿. 스키마 키는 유지하고 확장
- `assets/logo.webp`: 성분돋보기 로고(크림 배경, 차콜 돋보기, 분홍 용기, 세이지 잎)
- `config/ingredients.json`: 후보 18개(크롤러 Task 1 에서 생성)

## 실측으로 확인한 사실 (2026-09-28)
- 검색 API `GET https://gateway.hwahae.co.kr/v14/search/products/text?orderType=ranking&pageNum={n}&query={term}` 은 헤더 `hwahae-user-id: anonymous`, `hwahae-device-id: anonymous`, `Authorization: Bearer ` 세 개가 모두 있으면 브라우저 밖 `requests` 로도 200. 하나라도 없으면 401 code 2100. `pageNum=n` 은 `offset=20n`. 응답 항목의 `product_ingredients` 는 앞 6개뿐이라 전성분으로 못 씀
- `/search` 서버 렌더링은 offset, page, limit 파라미터를 모두 무시(항상 첫 20개)
- 제품 상세 `/products/{id}`, `/goods/{id}`, `/_next/data/...` 는 모두 AWS WAF 챌린지(202 빈 응답). Playwright 실제 브라우저에서만 통과. 쇼핑 상품이 있으면 `/goods/{goods_id}` 로 리다이렉트되지만 `pageProps.productIngredientInfoData.ingredients` 는 같은 자리. 항목 키 `korean, english, ewg, purposes`
- PDRN 검색 전체 1,813개(2026-09-28)

## 시각 결정 (2026-09-28 비주얼 비교)
- 흐름 A안(단계형 한 흐름), 실험 노트 톤, 강조색은 로고 장미색 `#c9605f`, 선택 칩 `#d98b8b`, 배경 `#fdfbf9`, 글자 `#3d4149`, 본문 Pretendard, 숫자 IBM Plex Mono
- 광고 이미지는 점 띠 분포 구성. 단 원식 차 님 지적으로 특정 성분이 아니라 합산 분포로, 문장은 이미지 밖 Meta 본문에
- 목업 파일: `C:/Users/eldorado/Projects/화해/.superpowers/brainstorm/1206-1790521670/content/`

## 크롤러 계획 검토 반영 (2026-09-28 저녁)
- 250페이지 상한 잘림은 meta `capped`, `capped_terms` 와 trend 표 `*` 로 표시, 정렬에서 뒤로 보내 따로 비교
- 화해 랭킹 05:00 KST 갱신: 04:50~05:20 회피(`schedule.py`), 실행마다 시작과 끝 시각 기록
- 요청 간격 3초(약 2,500회 = 2시간 10분). 401, 403, 429, WAF 202 는 즉시 중단. 상세는 연속 5건 실패면 중단
- 익명 헤더 검색 API 는 코드 작성 전 PDRN 으로 먼저 확인(Task 3 Step 6)
- 매칭 테스트: "1,2-헥산다이올" 첫 이름 보존(구분자 쉼표+공백), 라틴 패턴 단어 경계, 라하와 바하 겹침, 엑소좀 세포배양액 배제. 뼈대(모두에 든 성분)는 화해 성분 번호로 교집합
- 계열 매칭 표 `data/derived/family_matches.csv`: 계열마다 실제 걸린 성분 번호와 이름, 제품 수. 이걸 보고 계열을 번호로 고정
- PR 본문에 PDRN 3개 검증 결과와 수집 시각

## 의존성
- Vercel 프로젝트 `ingredient-lens`, 계정 wonsikcha12@gmail.com (원식 차 님). 이 PC 의 Vercel 연동 계정에는 프로젝트가 없음
- 저장소 `https://github.com/Chawonsik/seongbun-dotbogi`, 로컬 `C:/Users/eldorado/Projects/화해/seongbun-dotbogi`
- Python 3.14, markitdown 0.1.8 설치됨(문서 변환용)

## 미결 (스펙 11장)
1. 선정 기준과 확정 성분 8~10개 (trend.csv 본 뒤)
2. 랜딩 중립 제목 문구
3. B 광고 문구에 숫자를 넣을지
4. C 광고 문구와 리뷰 태그 수집 여부
5. 배포 방식(main 머지 시 자동 배포인지)
