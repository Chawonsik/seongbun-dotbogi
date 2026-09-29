# 북마클릿으로 전성분 모으기

1. `python crawler/run.py links ...` 로 만든 `data/derived/collect-links.html` 을 브라우저로 연다
2. 위쪽 "성분 수집", "수집 내보내기", "수집 비우기" 세 링크를 북마크바로 끌어다 놓는다(한 번만)
3. 제품 링크를 새 탭으로 열고, 페이지가 뜨면 북마크바의 "성분 수집"을 누른다. 오른쪽 위에 "저장 n개"가 뜨면 된다. 페이지는 자동으로 넘어가지 않으니 탭을 닫고 다음 링크로
4. 다 모았으면 www.hwahae.co.kr 의 아무 페이지(같은 사이트여야 모아 둔 것이 보입니다)에서 "수집 내보내기"를 누른다. `sd-collect-날짜.json` 이 내려받힌다
5. 내려받은 파일을 `data/raw/exports/` 로 옮긴 뒤 `python crawler/run.py ingest data/raw/exports/sd-collect-날짜.json` 으로 들여오고 `python crawler/run.py derive` 를 돌린다
6. 수집이 끝나고 파일을 확인했으면 `수집 비우기`로 화해 쪽 브라우저 저장분을 지운다

모아 둔 것은 화해 사이트의 브라우저 저장소(localStorage)에 남으므로 탭을 닫아도 유지된다. 다른 브라우저나 시크릿 창에서는 따로 모인다.

"성분 수집"은 페이지에 실린 데이터의 제품 번호가 주소의 번호와 다르면(예전 페이지가 남은 경우) 저장하지 않고 "새 탭에서 다시 열어 주세요"라고 알린다. 그때는 링크를 새 탭으로 다시 연다.

내려받은 `sd-collect-*.json` 에는 제품별 전성분 원문이 그대로 들어 있다. 절대 커밋하지 말고 팀 밖으로 공유하지 않는다(`.gitignore` 가 `sd-collect-*.json` 과 `data/raw/exports/` 를 막아 두었다).
