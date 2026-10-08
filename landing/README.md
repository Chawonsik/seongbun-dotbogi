# 성분돋보기 랜딩

정적 페이지. 서버 없음. 배포는 Vercel 프로젝트 `ingredient-lens`(main 머지 시 자동 배포).

주소 연결은 `vercel.json`의 rewrites가 한다(`/concept`, `/privacy`, `/notes/:slug` → 같은 이름의 .html). cleanUrls는 2026-10-05에 껐다. 켜 두면 검색 엔진 소유 확인 파일(`google….html`, `naver….html`)이 .html 없는 주소로 넘어가 확인이 실패할 수 있어서다. 새 페이지를 만들면 rewrites에 주소를 더한다.

## 파일
- concept.html: 광고 도착 페이지(출시 전 콘셉트). 주소는 /concept. `window.SD_CONFIG` 에 Amplitude 키와 메타 픽셀 ID를 넣는다. 화면 구성은 아래 "콘셉트 페이지 구성"
- privacy.html: 개인정보 처리방침. 주소는 /privacy
- notes/: 검색용 글. `notes/pdrn-cream-reviews.html` 주소는 /notes/pdrn-cream-reviews. 검색 허용(콘셉트와 처리방침은 noindex). 계측은 note_view, note_link_click이고 메타 픽셀은 싣지 않는다. 콘셉트 링크 값은 `utm_source=notes&utm_medium=owned&utm_campaign=organic&utm_content=n01`
- robots.txt, sitemap.xml: 검색 엔진용. sitemap에는 검색에 나올 글 주소만 넣는다
- google2e9047ca9cc0e9f7.html, naver8ad44ea19e0d116fef037d4373ef854e.html: 구글 서치 콘솔, 네이버 서치어드바이저 소유 확인 파일. 지우면 소유 확인이 풀린다
- favicon.ico: 로고로 만든 아이콘. img/og-pdrn-cream-reviews.png는 글 링크를 공유할 때 보이는 그림(1200x630)
- img/: 첫 화면 사진과 로고. 광고로 들어오면 광고 이름(utm_content)의 그림 값과 같은 사진(`img_ingredient_...` → `r1-ingredient.webp`, `img_texture_...` → `r1-texture-wide.webp`), 그 밖(UTM 없음, SNS)은 `concept-hero.webp`. 규칙은 concept.html 머리의 `HERO` 표
  - `r1-texture-wide.webp`(2496x960): 사용감 사진 `r1-texture.webp`를 양옆으로 늘린 판. 가운데 960px은 원본 그대로이고 늘린 부분은 사진이 아니다(배경은 가장자리 색을 이어 붙였고 스패출러 손잡이는 같은 기울기로 이어 그림). 사진을 자르지 않고 화면 폭에 맞추려고 만들었다(2026-10-08)
  - `note-form.webp`, `note-feel.webp`, `note-jar.webp`, `note-use.webp`(160x160): 제품 설명 네 줄 옆의 작은 사진. Canva 이미지 생성으로 만든 그림이다(2026-10-08). 용기와 쓰는 때는 사용감 사진을 참고 이미지로 넣어 통 색을 맞췄다

루트 주소(`/`)의 예전 성분 도구 페이지는 2026-09-30 삭제했다. 가상 제품이라 성분을 보여 줄 수 없어서 부록도 함께 뺐다.

## 콘셉트 페이지 구성 (2차, 2026-10-08)
- 첫 화면: 사진, 제목, 한 줄 소개, "이럴 때 바르는 크림이에요"와 세 줄. 제목과 한 줄 소개는 2차 광고 이름의 글 값에 따라 `ingredient`(A), `review`(B)로 나뉘고 그 밖은 공통 문구. 문구는 concept.html 머리의 `COPY` 표
- 버튼 줄: "더 보고 싶어요"(interest_click)와 "관심 없어요"(no_interest_click). 화면 아래에 붙어 따라오고 하나를 누르면 사라진다
- 누른 뒤: 한 줄 소개와 세 줄이 접히고 그 자리에 고마움 표시가 나온다. "더 보고 싶어요"는 제품 설명(예상 가격, 제형, 바르는 느낌, 용기, 쓰는 때)을 열고, 두 버튼 모두 설문을 연다. 설문은 버튼을 누른 직후에만 뜬다(20초 타이머는 뺐다)
- A와 B에 똑같이 들어가야 하는 부분(세 줄, 버튼, 제품 설명, 설문)은 한쪽만 고치지 않는다. 문구 비교가 깨진다

## 계측
이벤트와 속성의 기준은 `docs/taxonomy/events.csv` 이다. 광고 이름과 UTM 규칙은 `ads/README.md`. `?debug=1` 로 열면 화면 아래에 보내는 이벤트가 보이고 `is_test` 가 붙는다.
디자인을 고칠 때도 `id`, `data-track`, `data-section` 표시는 유지한다. `data-section`(cta, info, footer)이 붙은 요소가 화면에 절반 이상 들어오면 section_view를 보낸다. 2차 랜딩에서 cta는 늘 보이는 버튼 줄이라 방문 수와 같고 info는 "더 보고 싶어요"를 누른 뒤에만 열리는 제품 설명이다.

## 광고 링크 UTM 예
1차: ?utm_source=facebook&utm_medium=cpc&utm_campaign=pdrncream_traffic_imgtest_r1_261002&utm_term=ua_2040_female_interest_skincare&utm_content=img_ingredient_text_common_r1_v1

2차: ?utm_source=facebook&utm_medium=cpc&utm_campaign=pdrncream_traffic_texttest_r2_261009&utm_term=ua_2040_female_interest_skincare&utm_content=img_texture_text_ingredient_r2_v1
