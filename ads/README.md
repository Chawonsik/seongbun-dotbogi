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

## 2차 등록 값 (2026-10-08 확정, 게시는 2026-10-09 17:00 뒤)

그림은 사용감 그림(`texture`)이다(2026-10-07). 캠페인 이름의 시작일은 실제 게시일이라 10/9에 게시하면 `261009`. 게시가 자정을 넘기면 캠페인 이름과 두 링크의 utm_campaign을 함께 바꾼다.

### 캠페인
| 항목 | 값 |
|---|---|
| 이름 | `pdrncream_traffic_texttest_r2_261009` |
| 목표 | 트래픽 |
| A/B 테스트 기능 | 쓰지 않음 |
| 예산 | 캠페인에 걸지 않는다(어드밴티지 캠페인 예산 끔). 1차 캠페인을 복제하면 이 설정이 따라오니 새로 만든다 |

### 광고 세트 (2개, 세트마다 광고 1개)
| 항목 | 값 |
|---|---|
| 이름 | 두 세트 모두 `ua_2040_female_interest_skincare`(1차와 같음. utm_term도 같고 광고는 utm_content로 구분) |
| 하루 예산 | 세트마다 5,000원(합계 하루 10,000원, 7일 70,000원) |
| 일정 | 예약하지 않고 게시한 때부터 7일. 두 세트에 같은 종료 시각을 넣는다 |
| 나머지 | 1차와 같음(위 "광고 세트" 표): 웹사이트, 랜딩 페이지 조회, 대한민국, 20~49세 고정, 여성, 스킨케어(화장품), 다이내믹 크리에이티브 끔, 노출 위치 자동 |

### 광고
| 항목 | 광고 A | 광고 B |
|---|---|---|
| 광고 이름 | `img_texture_text_ingredient_r2_v1` | `img_texture_text_review_r2_v1` |
| 이미지 | `r2/r2_A_text_ingredient_1x1.png` | `r2/r2_B_text_review_1x1.png` |
| 라벨 문구 | PDRN 연어크림 | 바르면 쫀쫀해지고 / 광이 나는 크림 (두 줄) |
| 웹사이트 URL | 아래 A 링크 | 아래 B 링크 |

- 기본 문구, 제목, 설명, 버튼은 1차와 글자까지 같게 둔다(2026-10-08). A와 B가 다른 것은 이미지 안 문구뿐이다
- 인스타그램 계정은 연결하지 않는다(2026-10-08). 1차처럼 페이스북 페이지 이름으로 나간다
- "여러 광고주의 광고", 어드밴티지+ 크리에이티브 개선 사항, 필수 개선 사항, 크리에이티브 설정은 1차처럼 모두 끈다. URL 매개변수 칸은 비운다
- 그림 아래 아이보리 라벨에 문구를 넣는다: 나눔명조(SIL 오픈 폰트 라이선스), 64px, 자간 넓게, 가운데 정렬. 비교하는 낱말(A의 PDRN, B의 쫀쫀과 광)만 굵게 하고 로즈 색(#965C54)으로 구분한다. 사진은 조금 줄여 위에 두고 A와 B가 문구 말고는 모두 같다. A는 한 줄, B는 두 줄. `r2/make_overlay.py`로 만든다
- 영상은 하지 않는다(2026-10-06). 강사님 검수는 받지 않고 게시한다(2026-10-08)

```text
A: https://seongbun-dotbogi.vercel.app/concept?utm_source=facebook&utm_medium=cpc&utm_campaign=pdrncream_traffic_texttest_r2_261009&utm_term=ua_2040_female_interest_skincare&utm_content=img_texture_text_ingredient_r2_v1
B: https://seongbun-dotbogi.vercel.app/concept?utm_source=facebook&utm_medium=cpc&utm_campaign=pdrncream_traffic_texttest_r2_261009&utm_term=ua_2040_female_interest_skincare&utm_content=img_texture_text_review_r2_v1
```

### 2차를 이렇게 바꾼 이유
- 1차는 세트 1개에 광고 2개였고 예산이 캠페인에 걸려 원료 쪽 노출이 10/5부터 멈췄다. 그래서 세트를 2개로 나누고 세트마다 같은 예산을 고정한다(2026-10-06). 예산이 캠페인에 걸려 있으면 세트를 나눠도 메타가 한쪽으로 몰아준다
- 2차는 1차 캠페인에 넣지 않고 새 캠페인으로 만든다(1차 캠페인 이름이 이미지 테스트 1차를 뜻하므로)
- 랜딩은 소재별 랜딩으로 고친다. 첫 화면의 말을 누른 광고의 문구와 맞추고 `landing_page` 값은 `ingredient` 또는 `review`. 1차가 끝나는 10/9 17:00 뒤에 운영에 반영한다

### 게시 순서 (10/9)
1. 17:00 뒤 1차 캠페인이 끝났는지 확인하고 랜딩 수정을 운영에 반영한다
2. 위 두 링크에 `&debug=1`을 붙여 열고 round(r2), variant(ingredient, review), landing_page, 첫 화면 제목과 버튼, 픽셀 PageView를 확인한다
3. 결과 예측을 각자 적는다(노션 "2차 결과 예측")
4. 캠페인, 광고 세트 2개, 광고 2개를 만든다. 캠페인 예산이 꺼져 있고 금액이 세트에 들어갔는지 확인한다
5. 광고 관리자의 이름 세 곳이 링크의 UTM과 글자까지 같은지, 그림과 문구가 이름과 맞는지 대조한다(1차 때 뒤바뀐 적이 있음)
6. 게시하고 게시 시각, 심사 통과 시각, 세트별 첫 노출 시각을 노션에 적는다. "준비 중"이 보통 2시간, 길면 12시간 이어질 수 있다

## 폴더
- `r1/`: 1차 광고 이미지
- `r2/`: 2차 광고 이미지와 문구를 얹는 스크립트
- `r2-draft/`: 2차 시안 후보(예전 글자 들어간 이미지와 바탕 원본). 2차 방향이 정해질 때까지 저장소에 올리지 않고 로컬에만 둔다
