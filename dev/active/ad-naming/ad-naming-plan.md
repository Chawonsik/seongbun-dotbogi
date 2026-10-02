# 광고 이름과 UTM 규칙 변경: 계획

2026-10-02 강사님 검수에서 받은 피드백을 게시 전에 반영한다. 승인: 원식(2026-10-02), 지원 님과 공유됨.

## 왜
- 이름만 보고 누가 어떤 실험을 어떤 의도로 했는지 알 수 있어야 한다. 이름 짓기는 모든 변수를 고려한 실험 계획과 같다
- 캠페인 이름에 들어간 내용이 UTM에도 들어가야 한다
- 이름은 변수 종류와 값으로 짠다. 버전을 넣는다
- 예전 이름(`r1_name`, `r1_review`)은 1차가 그림 비교인데 2차의 문구 구분을 쓰고 있었다

## 무엇을
| 단계 | 이름 | UTM |
|---|---|---|
| 캠페인 | `pdrncream_traffic_imgtest_r1_261002` | utm_campaign |
| 광고 세트 | `ua_2040_female_interest_skincare` | utm_term (새로 추가) |
| 광고 A | `img_ingredient_text_common_r1_v1` | utm_content |
| 광고 B | `img_texture_text_common_r1_v1` | utm_content |

타겟은 한국 20~40대 여성(스킨케어 관심)으로 고정한다. 노출 위치는 자동, "여러 광고주의 광고"는 끔.

## 순서
1. 코드와 택소노미: `utm_term` 수집, utm_content에서 round와 variant 읽기, 그림 값으로 첫 화면 사진 고르기, 사진 파일 이름 변경
2. 문서: 택소노미 README, 계측 설계 사본, `ads/README.md`, `landing/README.md`, dev docs
3. 머지 뒤 운영 주소에서 새 링크 계측 점검
4. Amplitude 추적 계획(utm_term 속성, variant와 landing_page 값 목록)과 노션(결정 로그, 계측 설계, 진행 현황) 반영
5. 광고 관리자 초안 수정(원식)과 대조
6. 게시
