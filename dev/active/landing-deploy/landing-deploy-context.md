# landing-deploy context
Last Updated: 2026-09-23 16:55 KST

## 핵심 파일
- landing/index.html: 랜딩 본체. window.SD_CONFIG에 ga4, pixel ID를 넣으면 계측 활성화
- landing/privacy.html: 개인정보 처리방침
- landing/data.json: 제품별 파생 지표(id, brand, name, chip, total, pos, boundary, families, price_per_ml, registered)
- landing/vercel.json: cleanUrls

## 의사결정
- 전성분 원문은 JSON에 넣지 않는다(화해 상업적 활용 문구 대비). 붙여넣기 뒷문은 브라우저 안에서만 계산
- 1% 경계는 페녹시에탄올·카보머·잔탄검·향료·이디티에이·토코페롤·에틸헥실글리세린·하이드록시아세토페논·카프릴릴글라이콜 첫 등장 위치
- 결과 카드 문장은 관찰만 쓴다("몇 번째에 있다"). 효능·품질 판단 문구 없음
- 브랜드 실명은 랜딩의 제품 검색 결과에는 표시(사실 표기). 광고 소재에는 넣지 않음(노션 6절)

## 의존성
- Vercel MCP 커넥터(wonsikcha12@gmail.com), 프로젝트명 ingredient-lens, 운영 주소 https://seongbun-dotbogi.vercel.app
- 데이터 원본: 세션 트랜스크립트에서 복구한 PDRN 7개 레코드 (scratch pdrn_ing_recovered.jsonl)

## 미결
- GA4 측정 ID, 픽셀 ID (사용자)
- 유행 성분 목록 8~10개(채울 것 1번) → 칩 확장
- 도메인 구매 여부(D-2 전)
