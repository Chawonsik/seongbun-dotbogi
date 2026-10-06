# 성분돋보기 랜딩

정적 페이지. 서버 없음. 배포는 Vercel 프로젝트 `ingredient-lens`(main 머지 시 자동 배포).

주소 연결은 `vercel.json`의 rewrites가 한다(`/concept`, `/privacy`, `/notes/:slug` → 같은 이름의 .html). cleanUrls는 2026-10-05에 껐다. 켜 두면 검색 엔진 소유 확인 파일(`google….html`, `naver….html`)이 .html 없는 주소로 넘어가 확인이 실패할 수 있어서다. 새 페이지를 만들면 rewrites에 주소를 더한다.

## 파일
- concept.html: 광고 도착 페이지(출시 전 콘셉트). 주소는 /concept. `window.SD_CONFIG` 에 Amplitude 키와 메타 픽셀 ID를 넣는다.
- privacy.html: 개인정보 처리방침. 주소는 /privacy
- notes/: 검색용 글. `notes/pdrn-cream-reviews.html` 주소는 /notes/pdrn-cream-reviews. 검색 허용(콘셉트와 처리방침은 noindex). 계측은 note_view, note_link_click이고 메타 픽셀은 싣지 않는다. 콘셉트 링크 값은 `utm_source=notes&utm_medium=owned&utm_campaign=organic&utm_content=n01`
- robots.txt, sitemap.xml: 검색 엔진용. sitemap에는 검색에 나올 글 주소만 넣는다
- google2e9047ca9cc0e9f7.html, naver8ad44ea19e0d116fef037d4373ef854e.html: 구글 서치 콘솔, 네이버 서치어드바이저 소유 확인 파일. 지우면 소유 확인이 풀린다
- favicon.ico: 로고로 만든 아이콘. img/og-pdrn-cream-reviews.png는 글 링크를 공유할 때 보이는 그림(1200x630)
- img/: 첫 화면 사진과 로고. 광고로 들어오면 광고 이름(utm_content)의 그림 값과 같은 사진(`img_ingredient_...` → `r1-ingredient.webp`, `img_texture_...` → `r1-texture.webp`), 그 밖(UTM 없음, SNS)은 `concept-hero.webp`. 규칙은 concept.html 머리의 `HERO` 표

루트 주소(`/`)의 예전 성분 도구 페이지는 2026-09-30 삭제했다. 가상 제품이라 성분을 보여 줄 수 없어서 부록도 함께 뺐다.

## 계측
이벤트와 속성의 기준은 `docs/taxonomy/events.csv` 이다. 광고 이름과 UTM 규칙은 `ads/README.md`. `?debug=1` 로 열면 화면 아래에 보내는 이벤트가 보이고 `is_test` 가 붙는다.
디자인을 고칠 때도 `id`, `data-track`, `data-section` 표시는 유지한다. `data-section`(cta, info, footer)이 붙은 요소가 화면에 절반 이상 들어오면 section_view를 보낸다.

## 광고 링크 UTM 예
?utm_source=facebook&utm_medium=cpc&utm_campaign=pdrncream_traffic_imgtest_r1_261002&utm_term=ua_2040_female_interest_skincare&utm_content=img_ingredient_text_common_r1_v1
