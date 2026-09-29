import json

from crawler import search
from crawler.hwahae_api import SearchPage


class FakeClient:
    """총 45개짜리 검색 결과를 페이지 3장으로 흉내낸다."""
    def __init__(self, total=45, fail_on=None):
        self.total = total
        self.calls = []

    def fetch_page(self, term, page_num):
        self.calls.append((term, page_num))
        start = page_num * 20
        ids = list(range(start, min(start + 20, self.total)))
        products = [{"id": 1000 + i, "productName": f"{term} 제품 {i}", "obsolete": False, "updateTime": 1700000000 + i} for i in ids]
        return SearchPage(total_count=self.total, offset=start, count=len(products), products=products,
                          raw={"meta": {"pagination": {"total_count": self.total, "offset": start, "count": len(products)}}, "products": products})


def test_collect_term_fetches_until_total(tmp_path):
    client = FakeClient(total=45)
    out = tmp_path / "x.jsonl"
    meta = search.collect_term(client, "PDRN", out)
    assert [c[1] for c in client.calls] == [0, 1, 2]
    assert meta["total_count"] == 45 and meta["pages"] == 3 and meta["capped"] is False
    assert meta["started_at"] <= meta["finished_at"] and meta["started_at"].endswith("+09:00")
    lines = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 3 and lines[0]["term"] == "PDRN" and lines[2]["page"] == 2


def test_collect_term_respects_cap(tmp_path):
    client = FakeClient(total=1000)
    meta = search.collect_term(client, "PDRN", tmp_path / "x.jsonl", max_pages=2)
    assert meta["pages"] == 2 and meta["capped"] is True


class EmptyPageGlitchClient(FakeClient):
    """total=45 라고 말하지만 page_num==1 에서 빈 products 를 준다 (API 글리치 흉내)."""
    def fetch_page(self, term, page_num):
        if page_num == 1:
            self.calls.append((term, page_num))
            return SearchPage(total_count=self.total, offset=page_num * 20, count=0, products=[],
                              raw={"meta": {"pagination": {"total_count": self.total, "offset": page_num * 20, "count": 0}}, "products": []})
        return super().fetch_page(term, page_num)


def test_collect_term_marks_incomplete_on_early_empty_page(tmp_path):
    client = EmptyPageGlitchClient(total=45)
    meta = search.collect_term(client, "PDRN", tmp_path / "x.jsonl")
    assert meta["pages"] == 2
    assert meta["incomplete"] is True
    assert meta["capped"] is False


def test_collect_ingredient_merges_terms_and_is_idempotent(tmp_path):
    ing = {"key": "cica", "search_terms": ["시카", "센텔라"]}
    client = FakeClient(total=25)
    meta = search.collect_ingredient(client, ing, tmp_path)
    assert (tmp_path / "search" / "cica.jsonl").exists()
    assert meta["terms"] == ["시카", "센텔라"] and meta["total_count"] == {"시카": 25, "센텔라": 25}
    assert meta["capped"] is False and meta["capped_terms"] == [] and "started_at" in meta and "finished_at" in meta
    assert meta["incomplete"] is False and meta["incomplete_terms"] == []
    n_calls = len(client.calls)
    meta2 = search.collect_ingredient(client, ing, tmp_path)
    assert len(client.calls) == n_calls and meta2["skipped"] is True


def test_read_products_dedups_and_annotates(tmp_path):
    ing = {"key": "cica", "search_terms": ["시카", "센텔라"]}
    search.collect_ingredient(FakeClient(total=25), ing, tmp_path)
    products = search.read_products("cica", tmp_path)
    assert len(products) == 25  # 두 검색어가 같은 id 를 주므로 중복 제거
    assert products[0]["_rank_index"] == 0 and products[0]["_term"] == "시카" and products[0]["_page"] == 0
    assert products[24]["_rank_index"] == 24


def test_run_search_stops_on_blocked(tmp_path, monkeypatch):
    import pytest
    from crawler.hwahae_api import BlockedError

    class Blocking(FakeClient):
        def fetch_page(self, term, page_num):
            if term == "센텔라":
                raise BlockedError("401")
            return super().fetch_page(term, page_num)

    monkeypatch.setattr(search.schedule, "wait_if_refresh_window", lambda log=print: None)
    ings = [{"key": "PDRN", "search_terms": ["PDRN"]}, {"key": "cica", "search_terms": ["센텔라"]}, {"key": "ha", "search_terms": ["히알루론산"]}]
    with pytest.raises(BlockedError):
        search.run_search(tmp_path, ings, Blocking(total=5))
    assert (tmp_path / "search" / "PDRN.meta.json").exists()
    assert not (tmp_path / "search" / "ha.meta.json").exists()


def test_collect_term_meta_records_max_pages(tmp_path):
    meta = search.collect_term(FakeClient(total=45), "PDRN", tmp_path / "x.jsonl", max_pages=7)
    assert meta["max_pages"] == 7
    assert search.collect_ingredient(FakeClient(total=25), {"key": "k", "search_terms": ["a"]}, tmp_path, max_pages=9)["max_pages"] == 9


def _write_meta(tmp_path, key, **meta):
    sdir = tmp_path / "search"
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / f"{key}.meta.json").write_text(json.dumps({"key": key, **meta}), encoding="utf-8")


def test_capped_smoke_meta_does_not_block_larger_run(tmp_path):
    ing = {"key": "PDRN", "search_terms": ["PDRN"]}
    _write_meta(tmp_path, "PDRN", capped=True, max_pages=2, total_count={"PDRN": 1000}, pages={"PDRN": 2})
    client = FakeClient(total=45)
    meta = search.collect_ingredient(client, ing, tmp_path, max_pages=250)
    assert client.calls and meta["skipped"] is False and meta["capped"] is False and meta["max_pages"] == 250


def test_uncapped_meta_still_skips(tmp_path):
    ing = {"key": "PDRN", "search_terms": ["PDRN"]}
    _write_meta(tmp_path, "PDRN", capped=False, max_pages=2, total_count={"PDRN": 30}, pages={"PDRN": 2})
    client = FakeClient(total=45)
    assert search.collect_ingredient(client, ing, tmp_path, max_pages=250)["skipped"] is True and not client.calls


def _write_terms(tmp_path, key, per_term):
    sdir = tmp_path / "search"
    sdir.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps({"term": t, "page": 0, "fetched_at": "x", "response": {"products": [{"id": i} for i in ids]}}) for t, ids in per_term.items()]
    (sdir / f"{key}.jsonl").write_text(chr(10).join(lines) + chr(10), encoding="utf-8")


def test_read_products_interleaves_terms_round_robin(tmp_path):
    _write_terms(tmp_path, "k", {"A": [1, 2, 3, 4], "B": [10, 2, 11]})
    got = search.read_products("k", tmp_path)
    assert [p["id"] for p in got] == [1, 10, 2, 3, 11, 4]      # B 의 2 는 A 에서 이미 나와 건너뜀
    assert [p["_rank_index"] for p in got] == [0, 1, 2, 3, 4, 5]
    assert [p["_term"] for p in got] == ["A", "B", "A", "A", "B", "A"]


def test_read_products_term_a_four_term_b_two(tmp_path):
    _write_terms(tmp_path, "k", {"A": [1, 2, 3, 4], "B": [10, 11]})
    got = search.read_products("k", tmp_path)
    assert [p["id"] for p in got] == [1, 10, 2, 11, 3, 4] and got[3]["_rank_index"] == 3 and got[3]["_page"] == 0
