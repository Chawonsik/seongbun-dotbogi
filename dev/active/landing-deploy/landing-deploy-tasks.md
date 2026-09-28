# landing-deploy tasks
- [x] PDRN 7개 레코드 복구 (트랜스크립트)
- [x] data.json 생성 (6개, 파생 지표만)
- [x] index.html 작성
- [x] privacy.html 작성
- [x] vercel.json, README
- [x] Vercel 배포 (ingredient-lens)
- [x] 브라우저 검증: 375px 첫 화면에 숫자 하나 + 검색창, 검색→카드 2초 내, 붙여넣기 뒷문 동작, 개인정보 링크
- [x] 사용자에게 주소·스크린샷 전달
- [ ] GA4·픽셀 ID 수신 후 SD_CONFIG 채워 재배포
- [x] 메모리 갱신(계정 구조, 주소), 노션 반영 여부 질문

## 배포 결과 (2026-09-23)
- 주소: https://seongbun-dotbogi.vercel.app (ingredient-lens.vercel.app, dotbogi.vercel.app은 타인 선점)
- 보조 주소: ingredient-lens-delta.vercel.app (자동), 프로젝트명 ingredient-lens
- 검증: HTTPS, data.json 200, /privacy 200, 콘솔 에러 0, 375px 첫 화면에 숫자+검색창

## 코드 리뷰 반영 (2026-09-23 저녁, 2차 배포)
- 계측: engaged_60s 가시성 누적 버그 수정, product_select found:0은 blur 시 1회로 제한, 픽셀 ProductSelect는 found=1만
- 문구: 규칙 칩을 관찰형으로("뒤쪽이면 함량 순서도 뒤쪽", "%가 붙은 숫자만 함량 표기"), 6개 일반화 문장 수정, "함량 수치는 추정하지 않음"으로 통일, 리뷰 함정에 "PDRN 밖의 사례" 표시
- 접근성: 선택 칩·버튼 대비(--on-accent), 점 히트 영역 24px+ 및 겹침 어긋내기, 칩 재생성 제거(포커스 유지), 콤보박스 aria 정리, 버튼 15px, textarea 16px
- 방어: DATA 미도착 시 검색 가드, 숫자 코어션, 괄호·"1,2,3-" 파서, 공백 입력 처리, nosniff·referrer 헤더
- 개인정보: Meta 제3자 제공 문구 정정, 국외이전 항목, 행태정보 절, 권익침해 구제, Vercel·Google Fonts 고지
- 남은 것: GA4 속성에서 데이터 보존 14개월로 설정(방침 문구와 맞추기)

## 계측 ID 심기 완료 (2026-09-23 저녁)
- GA4 측정 ID: G-6N4SF70RFR
- Meta 픽셀 ID: 418137582712970
- 재배포 후 실제 확인: gtag/fbq 스크립트 로드됨, dataLayer에 config(frame 파라미터 포함)와 product_select 이벤트 발화 확인. 픽셀 스크립트 로드 확인(PageView는 init 시 자동 발화)
- 남은 것: GA4 실시간 보고서에서 사람이 직접 방문해 이벤트가 잡히는지 최종 확인, 데이터 보관 14개월 설정
