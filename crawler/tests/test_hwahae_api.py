import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from crawler import hwahae_api

FIX = Path(__file__).parent / "fixtures" / "search_page.json"


def _resp(status=200, payload=None):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = payload if payload is not None else json.loads(FIX.read_text(encoding="utf-8"))
    r.text = json.dumps(r.json.return_value)
    return r


def test_build_url_uses_ranking_and_page_num():
    url = hwahae_api.build_url("PDRN", 3)
    assert url.startswith("https://gateway.hwahae.co.kr/v14/search/products/text?")
    assert "orderType=ranking" in url and "pageNum=3" in url and "query=PDRN" in url


def test_headers_have_three_anonymous_values():
    h = hwahae_api.HEADERS
    assert h["hwahae-user-id"] == "anonymous"
    assert h["hwahae-device-id"] == "anonymous"
    assert h["Authorization"] == "Bearer "
    assert "Mozilla" not in h["User-Agent"]
    assert "Origin" not in h and "Referer" not in h


def test_fetch_page_parses_pagination_and_products():
    session = MagicMock()
    session.get.return_value = _resp()
    client = hwahae_api.SearchClient(session=session, sleep_s=0)
    page = client.fetch_page("PDRN", 1)
    assert page.total_count == 45 and page.offset == 20 and page.count == 20
    assert page.products[0]["id"] == 2000002
    session.get.assert_called_once()
    assert session.get.call_args.kwargs["headers"] == hwahae_api.HEADERS


def test_fetch_page_retries_on_5xx_then_raises(monkeypatch):
    session = MagicMock()
    session.get.return_value = _resp(status=503, payload={"meta": {"code": 9}})
    monkeypatch.setattr(hwahae_api.time, "sleep", lambda s: None)
    client = hwahae_api.SearchClient(session=session, sleep_s=0, retries=2)
    with pytest.raises(hwahae_api.SearchError):
        client.fetch_page("PDRN", 0)
    assert session.get.call_count == 3


@pytest.mark.parametrize("status", [401, 403, 429])
def test_fetch_page_block_status_raises_blocked_without_retry(monkeypatch, status):
    session = MagicMock()
    session.get.return_value = _resp(status=status, payload={"meta": {"code": 2100}})
    monkeypatch.setattr(hwahae_api.time, "sleep", lambda s: None)
    client = hwahae_api.SearchClient(session=session, sleep_s=0, retries=2)
    with pytest.raises(hwahae_api.BlockedError):
        client.fetch_page("PDRN", 0)
    assert session.get.call_count == 1


def test_fetch_page_waf_challenge_202_raises_blocked(monkeypatch):
    session = MagicMock()
    r = _resp(status=202, payload={})
    r.headers = {"x-amzn-waf-action": "challenge"}
    session.get.return_value = r
    monkeypatch.setattr(hwahae_api.time, "sleep", lambda s: None)
    with pytest.raises(hwahae_api.BlockedError):
        hwahae_api.SearchClient(session=session, sleep_s=0).fetch_page("PDRN", 0)


def test_fetch_page_retries_on_connection_error_then_raises(monkeypatch):
    session = MagicMock()
    session.get.side_effect = hwahae_api.requests.ConnectionError("connection failed")
    monkeypatch.setattr(hwahae_api.time, "sleep", lambda s: None)
    client = hwahae_api.SearchClient(session=session, sleep_s=0, retries=2)
    with pytest.raises(hwahae_api.SearchError):
        client.fetch_page("PDRN", 0)
    assert session.get.call_count == 3


def test_fetch_page_retries_on_connection_error_then_succeeds(monkeypatch):
    session = MagicMock()
    session.get.side_effect = [
        hwahae_api.requests.ConnectionError("connection failed"),
        _resp(),
    ]
    monkeypatch.setattr(hwahae_api.time, "sleep", lambda s: None)
    client = hwahae_api.SearchClient(session=session, sleep_s=0, retries=2)
    page = client.fetch_page("PDRN", 1)
    assert page.total_count == 45
    assert session.get.call_count == 2
