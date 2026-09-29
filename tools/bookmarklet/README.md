# 북마클릿으로 전성분 모으기

1. `python crawler/run.py links ...` 로 만든 `data/derived/collect-links.html` 을 브라우저로 연다
2. 위쪽 "성분 수집", "수집 내보내기" 두 링크를 북마크바로 끌어다 놓는다(한 번만)
3. 제품 링크를 새 탭으로 열고, 페이지가 뜨면 북마크바의 "성분 수집"을 누른다. 오른쪽 위에 "저장 n개"가 뜨면 된다. 페이지는 자동으로 넘어가지 않으니 탭을 닫고 다음 링크로
4. 다 모았으면 아무 화해 페이지에서 "수집 내보내기"를 누른다. `sd-collect-날짜.json` 이 내려받힌다
5. `python crawler/run.py ingest 내려받은파일.json` 으로 들여온 뒤 `python crawler/run.py derive`

모아 둔 것은 화해 사이트의 브라우저 저장소(localStorage)에 남으므로 탭을 닫아도 유지된다. 다른 브라우저나 시크릿 창에서는 따로 모인다.
