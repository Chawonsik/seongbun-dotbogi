# 광고 소재

## 이름 규칙 (2026-10-02)

광고 관리자의 이름과 UTM을 같은 글자로 쓴다. 이름만 보고 누구에게 무엇을 시험하는지 알 수 있어야 한다(강사님 피드백). 다른 값이 생길 수 있는 것만 이름에 넣는다.

| 단계 | 규칙 | 1차 이름 | 들어가는 UTM |
|---|---|---|---|
| 캠페인 | 제품_목표_실험_차수_시작일 | `pdrncream_traffic_imgtest_r1_261002` | utm_campaign |
| 광고 세트 | 겨냥_연령_성별_고르는방법_값 | `ua_2040_female_interest_skincare` | utm_term |
| 광고 | img_그림_text_글_차수_버전 | 아래 표 | utm_content |

| | A | B |
|---|---|---|
| 1차 (그림만 다름) | `img_ingredient_text_common_r1_v1` | `img_texture_text_common_r1_v1` |
| 2차 (글만 다름) | `img_(고른 그림)_text_ingredient_r2_v1` | `img_(고른 그림)_text_review_r2_v1` |

광고 이름은 두 낱말씩 짝으로 읽는다. `img_ingredient` 는 "그림은 원료", `text_common` 은 "글은 A와 B가 같음".

낱말
- `ua`: 신규 유입. 우리를 처음 보는 사람에게 내보낸다. 리타겟팅을 하게 되면 `rt`
- `2040`: 20~40대(20~49세). `female`: 여성. `interest_skincare`: 관심사로 고르고 그 관심사는 스킨케어
- `img`, `text`: 그림과 글. 영상을 쓰게 되면 `img` 자리가 `vid`
- `ingredient`: 원료, 성분 이름. `texture`: 제형과 사용감. `review`: 리뷰 언어. `common`: A와 B가 같음
- `r1`, `r2`: 1차, 2차. `v1`: 버전. 소재를 고쳐 다시 올리면 `v2`
- `imgtest`, `texttest`: 그림을 시험, 글을 시험. 2차 캠페인 이름은 `pdrncream_traffic_texttest_r2_(시작일)`
- 시작일은 실제 게시일(YYMMDD). 게시가 미뤄지면 캠페인 이름과 두 링크의 utm_campaign을 같이 바꾼다
- 2차의 "(고른 그림)" 자리에는 1차에서 이긴 쪽에 따라 `ingredient` 또는 `texture` 가 들어간다

`/concept` 코드는 utm_content에서 차수와 소재 구분을 읽고 그림 값으로 첫 화면 사진을 고른다. 규칙에 맞지 않는 이름은 읽지 못하므로 이름을 바꾸려면 코드와 `docs/taxonomy/events.csv` 를 같은 PR에서 고친다. 게시한 뒤에는 바꾸지 않는다. 2026-10-01까지 쓰던 값(`kr_2040_skincare`, `r1_name`, `r1_review`)은 게시 전에 바꿨다.

이미지 파일: A `r1/r1_A_ingredient_1x1.png`, B `r1/r1_B_texture_1x1.png`

## 1차 (2026-10-01 확정)
- 규격 1:1 (1080x1080), 그림 안에 글자 없음
- 광고 글은 A, B 동일
  - 기본 문구: 새 크림을 준비하고 있어요. 판매 전 콘셉트를 가장 먼저 공개해요. 이런 크림이 나온다면 써 보고 싶은지, 관심 있어요 한 번으로 알려 주세요. (2026-10-01 3안 확정, 인스타그램에서 접히기 전에 "판매 전"이 보임)
  - 제목: 새 크림 콘셉트 미리 보기
  - 설명: 비움
  - 버튼: 더 알아보기

## 메타 광고 등록 순서 (1차)

광고 관리자 화면 순서대로 넣을 값이다. 캠페인 하나, 광고 세트 하나, 광고 두 개.

### 캠페인
| 항목 | 값 |
|---|---|
| 이름 | `pdrncream_traffic_imgtest_r1_261002` |
| 목표 | 트래픽 |
| A/B 테스트 기능 | 쓰지 않음 (A와 B를 같은 광고 세트에 넣는다) |
| 예산 | 하루 10,000원 |

### 광고 세트
| 항목 | 값 |
|---|---|
| 이름 | `ua_2040_female_interest_skincare` |
| 전환 위치 | 웹사이트 |
| 성과 목표 | 랜딩 페이지 조회 (워밍업과 같음) |
| 일정 | 7일, 종료 날짜 넣기 |
| 타겟 방식 | 원래 타겟 옵션. 어드밴티지+ 타겟은 연령과 성별이 추천값으로만 쓰여서 쓰지 않는다 |
| 위치 | 대한민국 |
| 연령 | 20~49세, 고정 |
| 성별 | 여성 |
| 관심사 | 스킨케어(화장품) |
| 다이내믹 크리에이티브 | 끔 |
| 노출 위치 | 자동(어드밴티지+ 노출 위치) |

연령 고정과 노출 위치 자동은 2026-10-02 강사님 답변이다.

### 광고 (두 개, 아래 표 말고는 모두 같게)
| 항목 | 광고 A | 광고 B |
|---|---|---|
| 광고 이름 | `img_ingredient_text_common_r1_v1` | `img_texture_text_common_r1_v1` |
| 이미지 | `r1/r1_A_ingredient_1x1.png` | `r1/r1_B_texture_1x1.png` |
| 웹사이트 URL | 아래 A 링크 | 아래 B 링크 |

- 형식: 단일 이미지
- 기본 문구, 제목, 설명, 버튼: 위 "1차" 절의 값. A와 B가 글자 하나까지 같아야 한다
- "여러 광고주의 광고" 체크를 푼다
- 어드밴티지+ 크리에이티브 개선 사항, 필수 개선 사항, 크리에이티브 설정(웹사이트 요약 등)을 모두 끈다
- URL 매개변수 칸은 비운다. 링크에 UTM이 이미 들어 있다
- 인스타그램 계정이 없으면 페이스북 페이지 이름으로 인스타그램에 나간다

```text
A: https://seongbun-dotbogi.vercel.app/concept?utm_source=facebook&utm_medium=cpc&utm_campaign=pdrncream_traffic_imgtest_r1_261002&utm_term=ua_2040_female_interest_skincare&utm_content=img_ingredient_text_common_r1_v1
B: https://seongbun-dotbogi.vercel.app/concept?utm_source=facebook&utm_medium=cpc&utm_campaign=pdrncream_traffic_imgtest_r1_261002&utm_term=ua_2040_female_interest_skincare&utm_content=img_texture_text_common_r1_v1
```

### 게시 직전
- 결과 예측 각자 적어 두기
- 두 링크에 `&debug=1` 을 붙여 열고 round(r1), variant(ingredient, texture), utm_term, 첫 화면 사진, 픽셀 PageView 확인
- 광고 관리자의 캠페인, 광고 세트, 광고 이름이 링크의 utm_campaign, utm_term, utm_content와 글자까지 같은지 확인
- 워밍업 캠페인을 복제해 만들었다면 예전 이미지, 문구, 링크가 남아 있지 않은지 확인

### 결과를 볼 때
- 판정에 쓰는 CTR은 광고 관리자의 "CTR(링크 클릭률)"이다. "CTR(전체)"는 좋아요와 프로필 누르기까지 세므로 쓰지 않는다
- 링크 클릭은 광고를 누른 수, 랜딩 페이지 조회는 페이지가 열려 픽셀이 작동한 수라서 랜딩 페이지 조회가 더 적다

## 2차 사전 준비 (2026-10-06, 그림과 시작일만 비어 있음)

1차가 끝나고 그림이 정해지면 `(그림)` 자리에 `ingredient` 또는 `texture`, `(시작일)` 자리에 실제 게시일(YYMMDD)을 넣는다.

| 항목 | 값 |
|---|---|
| 캠페인 | `pdrncream_traffic_texttest_r2_(시작일)`, 목표 트래픽, 하루 10,000원, A/B 테스트 기능 쓰지 않음 |
| 광고 세트 | `ua_2040_female_interest_skincare`, 1차와 같은 설정(위 "광고 세트" 표) |
| 광고 A | `img_(그림)_text_ingredient_r2_v1`, 그림 위 문구 "PDRN 연어크림" |
| 광고 B | `img_(그림)_text_review_r2_v1`, 그림 위 문구 "바르면 쫀쫀해지고 광이 나는 크림"(두 줄: 바르면 쫀쫀해지고 / 광이 나는 크림) |

- 지금 계획은 1차와 같은 구성(광고 세트 1개에 광고 2개). 1차에서 원료 쪽 노출이 멈춘 일이 있어 세트를 2개로 나눌지는 등록 전에 확정한다(`dev/active/ingredient-map/` 할 일). 영상은 하지 않는다(2026-10-06 결정)
- 그림 위 문구: 같은 글꼴, 같은 크기(72px, 굵게), 같은 위치(왼쪽 위 72, 72), 같은 색. A는 한 줄, B는 두 줄. 시안은 로컬 `r2-draft/`(스크립트 `make_overlay.py`). 시안 글꼴은 맥 기본 글꼴이라 게시 전에 공개 라이선스 글꼴로 바꾼다
- 기본 문구, 제목, 설명, 버튼은 1차와 같게 두는 안(A와 B가 다른 것은 그림 위 문구뿐). 게시 전에 확정
- 랜딩은 고칠 것이 없다. `/concept` 코드가 2차 이름을 이미 읽는다(round r2, variant ingredient 또는 review, 첫 화면 사진은 그림 값)

```text
A: https://seongbun-dotbogi.vercel.app/concept?utm_source=facebook&utm_medium=cpc&utm_campaign=pdrncream_traffic_texttest_r2_(시작일)&utm_term=ua_2040_female_interest_skincare&utm_content=img_(그림)_text_ingredient_r2_v1
B: https://seongbun-dotbogi.vercel.app/concept?utm_source=facebook&utm_medium=cpc&utm_campaign=pdrncream_traffic_texttest_r2_(시작일)&utm_term=ua_2040_female_interest_skincare&utm_content=img_(그림)_text_review_r2_v1
```

게시 전 순서
1. 1차 분석 결과로 그림을 정하고 분석에서 나온 피드백을 소재와 설정에 반영한다
2. 결과 예측을 각자 적는다
3. 두 링크에 `&debug=1`을 붙여 열고 round(r2), variant(ingredient, review), 첫 화면 사진, 픽셀 PageView를 확인한다
4. 광고 관리자의 이름 세 곳이 링크의 UTM과 글자까지 같은지, 그림과 문구가 이름과 맞는지 대조한다(1차 때 뒤바뀐 적이 있음)
5. 시작 시각은 "준비 중" 지연(보통 2시간, 길면 12시간)을 감안해 잡는다

## 폴더
- `r1/`: 1차 광고 이미지
- `r2-draft/`: 2차 시안 후보(예전 글자 들어간 이미지와 바탕 원본). 2차 방향이 정해질 때까지 저장소에 올리지 않고 로컬에만 둔다
