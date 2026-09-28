# 성분돋보기

성분 이름 마케팅 실험 프로젝트의 코드 저장소입니다. 설계와 결정은 노션 결정 로그를 기준으로 합니다.

## 폴더
- `landing/`: 광고 도착 페이지. 운영 주소 https://seongbun-dotbogi.vercel.app (Vercel 프로젝트 ingredient-lens)
- `dev/active/`: 작업 계획과 진행 기록

## 운영 중인 랜딩에서 유지할 것
- 주소, 개인정보 처리방침 링크(`/privacy`)
- `landing/index.html` 의 `window.SD_CONFIG`: GA4 `G-6N4SF70RFR`, 메타 픽셀 `1547670487046797`
- 계측 수정 두 건: 60초 체류는 화면을 벗어난 시간을 빼고 계산, 제품 검색 "못 찾음" 이벤트는 입력창을 벗어날 때 한 번만 전송

## 원칙
- 화해 전성분 원문은 `data/raw/` 에만 두고 커밋하지 않습니다. 랜딩과 광고에는 파생값만 싣습니다.

## 브랜치 작업 방식
두 사람이 같은 파일을 동시에 고치다 충돌하지 않도록 main에 직접 커밋하지 않고 브랜치에서 작업한 뒤 PR로 합칩니다.

**원칙**
- main은 항상 합쳐도 되는 상태로 둡니다. main에 직접 커밋하거나 강제로 푸시하지 않습니다.
- 브랜치는 작업 하나당 하나이고 하루나 이틀 안에 합칠 크기로 만듭니다.
- 작업 전에 결정 로그에서 누가 어떤 폴더를 맡는지 확인하고 같은 파일을 동시에 고치지 않습니다.

**브랜치 이름**
`종류/짧은-설명` 형식으로 씁니다. 예: `feat/crawler-search`, `fix/landing-stay-60s`, `docs/readme`

| 종류 | 쓰는 경우 |
|---|---|
| feat | 새 기능 (크롤러 단계, 랜딩 화면, 광고 템플릿) |
| fix | 버그 수정 |
| data | 설정값이나 파생 데이터 갱신 (성분 목록, data.json) |
| docs | 문서 |
| chore | 설정과 정리 |

**순서**
1. 최신 main에서 브랜치를 만듭니다.
   ```
   git switch main
   git pull
   git switch -c feat/crawler-search
   ```
2. 작업하고 커밋합니다. 커밋 메시지는 영어로 `종류: 설명` 형식입니다. 예: `feat: collect search results via browser fetch capture`
3. 브랜치를 올립니다.
   ```
   git push -u origin feat/crawler-search
   ```
4. GitHub에서 PR을 만들고 무엇을 바꿨는지와 어떻게 확인했는지를 적습니다.
5. 다른 사람이 확인하고 승인하면 Squash and merge로 합치고 브랜치를 지웁니다.
6. 작업 중에 main이 바뀌었으면 합치기 전에 내 브랜치에 main을 받아 충돌을 먼저 풉니다.
   ```
   git pull origin main
   ```

**커밋하면 안 되는 것**
- `data/raw/` 의 화해 원본 데이터. `.gitignore` 에 들어 있습니다.
- 비밀번호, 토큰, API 키. GA4와 픽셀 ID는 공개 페이지에 들어가는 값이라 괜찮습니다.

**배포**
운영 랜딩의 Vercel 배포는 지금 git과 연결되어 있지 않습니다. main에 합쳐도 자동으로 배포되지 않으니 `landing/` 을 바꾼 PR이 합쳐지면 배포 담당이 따로 배포합니다. 배포 뒤에는 주소, 개인정보 처리방침 링크, 두 ID가 그대로인지 확인합니다.
