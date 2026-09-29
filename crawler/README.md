# 크롤러

검색은 화해 검색 API(사이트가 비로그인 상태에서 쓰는 익명 헤더)로 자동 수집한다. 전성분은 사람이 브라우저에서 제품 페이지를 열고 북마클릿으로 모은다. 자동 조작 브라우저와 봇 감지 우회는 쓰지 않는다. 원문은 `data/raw/`(git 제외)에만 둔다.

## 준비
pip install --user -r crawler/requirements.txt

## 순서
python crawler/run.py search                 # 후보 18개 검색 전체 (약 2시간, 1회, 04:50~05:20 KST 는 자동 대기)
python crawler/run.py trend                  # data/derived/trend.csv + 제안 표. 기준: 이름 단 제품 수 상위 9 + 히알루론산, 15개 미만 제외
#   config/ingredients.json 의 selected 를 표시한 뒤
python crawler/run.py links --only PDRN --top-n 3    # 북마클릿 점검용 3개 (data/derived/collect-links.html)
#   사람이 열고 북마클릿으로 모아 내보낸 뒤 (tools/bookmarklet/README.md)
python crawler/run.py ingest sd-collect-YYYYMMDD-HHMM.json
python crawler/run.py derive                 # selected 가 있으면 landing/data.json 과 unmatched.csv, family_matches.csv, verify.csv. selected 가 없으면 verify.csv 와 family_matches.csv 만 쓰고 landing/data.json 은 건드리지 않는다
python crawler/run.py links --top-n 30       # 확정 성분 x 30개 링크 페이지 (둘이 나눠 수집)

## 옵션
--only PDRN  한 성분만 (links 에서는 selected 여부와 무관하게 지정) / --top-n 30 성분당 링크 수 / --force 검색 다시 받기 / --max-pages N 검색 성분당 페이지 상한(기본 250)

## 규칙
요청 간격 3초. 검색 상한 250페이지(잘린 성분은 meta 의 capped 와 trend 표의 * 로 표시). 단종(obsolete) 제외.
401, 403, 429, WAF 202 가 오면 즉시 멈춘다. 검색 jsonl 과 전성분 원문은 data/raw/ 아래(git 제외).
전성분 원문, 리뷰 수, 평점은 공개 파일에 넣지 않는다.
