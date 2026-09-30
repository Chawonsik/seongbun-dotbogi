# 크롤러

검색은 화해 검색 API(사이트가 비로그인 상태에서 쓰는 익명 헤더)로 자동 수집한다. 전성분은 사람이 브라우저에서 제품 페이지를 열고 북마클릿으로 모은다. 자동 조작 브라우저와 봇 감지 우회는 쓰지 않는다. 원문은 `data/raw/`(git 제외)에만 둔다.

## 준비
pip install --user -r crawler/requirements.txt

## 순서
python crawler/run.py search                 # 후보 18개 검색 전체 (약 2시간, 1회, 04:50~05:20 KST 는 자동 대기)
python crawler/run.py trend                  # data/derived/trend.csv + 제안 표. 기준: 이름 단 제품 수 상위 9 + 히알루론산, 15개 미만 제외
python crawler/run.py links --only PDRN --top-n 3    # 북마클릿 점검용 3개 (data/derived/collect-links.html). selected 는 아직 표시하지 않는다
#   사람이 열고 북마클릿으로 모아 내보낸 뒤 (tools/bookmarklet/README.md), 받은 파일은 data/raw/exports/ 로 옮긴다
python crawler/run.py ingest data/raw/exports/sd-collect-YYYYMMDD-HHMM.json
python crawler/run.py derive                 # selected 가 아직 없으므로 CSV(verify, family_matches, top6-check 등)와 data/derived/data.json 만 쓴다
#   점검이 통과하면 config/ingredients.json 의 selected 를 표시한 뒤
python crawler/run.py links --top-n 30       # 확정 성분 x 30개 링크 페이지 (둘이 나눠 수집)
#   collect -> data/raw/exports/ 로 옮기기
python crawler/run.py ingest data/raw/exports/sd-collect-YYYYMMDD-HHMM.json
python crawler/run.py derive                 # data/derived/data.json 과 CSV. landing/data.json 은 건드리지 않는다
#   결과를 검토한 뒤, 팀이 배포하기로 했을 때만
python crawler/run.py derive --publish       # landing/data.json 에도 쓴다

검증 기준선은 `data/derived/baseline-data.json`(파일럿 시작 전 `landing/data.json` 의 사본)이다. `links` 의 검증 묶음과 `derive` 의 verify.csv 가 이 파일과 비교한다. 없으면 `landing/data.json` 으로 대신하고 경고를 찍는다.

## 내보낸 파일 주의
북마클릿이 내려받은 `sd-collect-*.json` 에는 제품별 전성분 원문이 그대로 들어 있다. 반드시 `data/raw/exports/`(git 제외)에 두고, 커밋하거나 팀 밖으로 공유하지 않는다. 저장소 다른 곳에 둔 채 `ingest` 하면 경고가 뜬다.

`derive` 가 쓰는 `data/derived/top6-check.csv` 도 제품별 성분표 앞 6개를 그대로 담으므로 git 에서 제외한다. 점검 결과는 숫자로만 남긴다.

- 2026-09-29 점검 (PDRN 3개 + 검증 5개 = 8개): 검색 응답의 앞 6개 성분 순서가 실제 성분표와 8/8 일치, verify 기준선과 5/5 일치

## 옵션
--only PDRN  한 성분만 (links 에서는 selected 여부와 무관하게 지정) / --top-n 30 성분당 링크 수 / --force 검색 다시 받기 / --max-pages N 검색 성분당 페이지 상한(기본 250)

## 규칙
요청 간격 3초. 검색 상한 250페이지(잘린 성분은 meta 의 capped 와 trend 표의 * 로 표시). 낮은 상한으로 잘린 meta(스모크 실행)는 더 큰 상한으로 다시 돌리면 다시 받는다. meta 없이 중단된 성분은 trend 표에 ! 로 나오고 제안에서 빠진다. 검색어가 여러 개면 검색어별 랭킹을 번갈아 합쳐 후보 순위를 정한다. 단종(obsolete) 제외.
401, 403, 429, WAF 202 가 오면 즉시 멈춘다. 검색 jsonl 과 전성분 원문은 data/raw/ 아래(git 제외).
전성분 원문, 리뷰 수, 평점은 공개 파일에 넣지 않는다.
