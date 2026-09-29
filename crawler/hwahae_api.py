"""화해 검색 API 클라이언트. 2026-09-28 실측 기준.

GET https://gateway.hwahae.co.kr/v14/search/products/text?orderType=ranking&pageNum={n}&query={term}
헤더 세 개가 모두 있어야 200. pageNum=n 은 offset=20n. 페이지당 20개.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from urllib.parse import urlencode

import requests

BASE = "https://gateway.hwahae.co.kr/v14/search/products/text"
HEADERS = {
    "hwahae-user-id": "anonymous",
    "hwahae-device-id": "anonymous",
    "Authorization": "Bearer ",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36",
    "Origin": "https://www.hwahae.co.kr",
    "Referer": "https://www.hwahae.co.kr/search",
}
PAGE_SIZE = 20
RETRY_WAIT_S = 10.0


class SearchError(RuntimeError):
    """재시도 후에도 실패."""


class BlockedError(SearchError):
    """차단 신호. 재시도하지 않고 전체 실행을 멈춰야 한다."""


@dataclass
class SearchPage:
    total_count: int
    offset: int
    count: int
    products: list[dict]
    raw: dict


def build_url(term: str, page_num: int) -> str:
    return BASE + "?" + urlencode({"orderType": "ranking", "pageNum": str(page_num), "query": term})


class SearchClient:
    def __init__(self, session: requests.Session | None = None, sleep_s: float = 3.0, retries: int = 2, timeout_s: float = 20.0):
        self.session = session or requests.Session()
        self.sleep_s = sleep_s
        self.retries = retries
        self.timeout_s = timeout_s

    def fetch_page(self, term: str, page_num: int) -> SearchPage:
        url = build_url(term, page_num)
        last_err = None
        for attempt in range(self.retries + 1):
            try:
                r = self.session.get(url, headers=HEADERS, timeout=self.timeout_s)
            except requests.RequestException as e:
                last_err = f"connection error: {e}"
                time.sleep(RETRY_WAIT_S)
                continue
            if r.status_code == 200:
                data = r.json()
                pag = data.get("meta", {}).get("pagination", {})
                if "total_count" not in pag:
                    raise SearchError(f"pagination 없음: {url} -> {r.text[:200]}")
                if self.sleep_s:
                    time.sleep(self.sleep_s)
                return SearchPage(
                    total_count=int(pag["total_count"]),
                    offset=int(pag.get("offset", page_num * PAGE_SIZE)),
                    count=int(pag.get("count", len(data.get("products", [])))),
                    products=list(data.get("products", [])),
                    raw=data,
                )
            if r.status_code in (401, 403, 429):
                raise BlockedError(f"차단 신호 HTTP {r.status_code}: 실행을 멈춥니다. {r.text[:200]}")
            if r.status_code == 202 and any(k.lower() == "x-amzn-waf-action" for k in (getattr(r, "headers", None) or {})):
                raise BlockedError("WAF 챌린지(202): 실행을 멈춥니다")
            last_err = f"HTTP {r.status_code}: {r.text[:200]}"
            time.sleep(RETRY_WAIT_S)
        raise SearchError(f"{url} 실패 ({self.retries + 1}회): {last_err}")
