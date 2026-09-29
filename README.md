# 성분돋보기

성분 이름 마케팅 실험 프로젝트의 코드 저장소입니다. 설계와 결정은 노션 결정 로그를 기준으로 합니다.

## 폴더
- `landing/`: 광고 도착 페이지. 운영 주소 https://seongbun-dotbogi.vercel.app (Vercel 프로젝트 ingredient-lens)
- `dev/active/`: 작업 계획과 진행 기록
- `crawler/`, `config/`: 화해 검색 수집 스크립트와 후보 성분 설정. 사용법은 `crawler/README.md`
- `tools/bookmarklet/`: 전성분을 사람이 모으는 북마클릿. 설명은 그 폴더의 README
- `data/raw/`: 수집 원문(git 제외). `data/derived/`: 선정 표, 링크 페이지, 미매칭과 검증 목록

## 운영 중인 랜딩에서 유지할 것
- 주소, 개인정보 처리방침 링크(`/privacy`)
- `landing/index.html` 의 `window.SD_CONFIG`: GA4 `G-6N4SF70RFR`, 메타 픽셀 `1547670487046797`
- 계측 수정 두 건: 60초 체류는 화면을 벗어난 시간을 빼고 계산, 제품 검색 "못 찾음" 이벤트는 입력창을 벗어날 때 한 번만 전송

## 원칙
- 화해 전성분 원문은 `data/raw/` 에만 두고 커밋하지 않습니다. 랜딩과 광고에는 파생값만 싣습니다.
