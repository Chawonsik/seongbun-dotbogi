# 성분돋보기 랜딩

정적 페이지. 서버 없음. 배포는 Vercel 프로젝트 `ingredient-lens`(main 머지 시 자동 배포).

## 파일
- concept.html: 광고 도착 페이지(출시 전 콘셉트). 주소는 /concept. `window.SD_CONFIG` 에 Amplitude 키와 메타 픽셀 ID를 넣는다.
- privacy.html: 개인정보 처리방침. 주소는 /privacy
- img/: 콘셉트 사진(광고와 같은 사진), 로고

루트 주소(`/`)의 예전 성분 도구 페이지는 2026-09-30 삭제했다. 가상 제품이라 성분을 보여 줄 수 없어서 부록도 함께 뺐다.

## 계측
이벤트와 속성은 노션 "계측 설계 초안"을 따른다. `?debug=1` 로 열면 화면 아래에 보내는 이벤트가 보이고 `is_test` 가 붙는다.
디자인을 고칠 때도 `id` 와 `data-track` 표시는 유지한다.

## 광고 링크 UTM 예
?utm_source=facebook&utm_medium=cpc&utm_campaign=kr_2040_skincare&utm_content=r1_name
