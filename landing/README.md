# 성분돋보기 랜딩

정적 페이지. 서버 없음. 배포는 Vercel 프로젝트 `ingredient-lens`.

## 파일
- index.html: 랜딩. `window.SD_CONFIG = { ga4: "G-…", pixel: "…" }` 에 ID를 넣으면 계측이 켜진다. 비어 있으면 아무 스크립트도 싣지 않는다.
- privacy.html: 개인정보 처리방침. 주소는 /privacy
- data.json: 제품별 파생 지표. 전성분 원문은 넣지 않는다.

## data.json 갱신
- ingredients[]: key, label, category, n_products, common(전부에 든 성분), note
- products[]: id(화해), brand, name, chip(ingredients.key), total, pos(이름 성분 위치), boundary(1% 경계 위치 또는 null), families[{name,pos,top}], price_per_ml, registered
- 파일만 바꿔 다시 배포하면 칩·큰 숫자·점 띠·검색 목록이 모두 따라 바뀐다.

## 계측 이벤트 (GA4)
page_view(자동), chip_click{ingredient}, product_select{product,found,ingredient}, paste_run{n,found}, engaged_60s. 모든 이벤트에 frame(utm_content) 파라미터.
메타 픽셀: PageView, trackCustom ProductSelect.

## 광고 링크 UTM 예
?utm_source=meta&utm_medium=paid&utm_campaign=frame-test&utm_content=A
