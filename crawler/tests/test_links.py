import json

from crawler import links


def _write_search(tmp_path, key, products):
    sdir = tmp_path / "search"
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / f"{key}.meta.json").write_text(json.dumps({"total_count": {"t": len(products)}, "capped": False}), encoding="utf-8")
    (sdir / f"{key}.jsonl").write_text(json.dumps({"term": "t", "page": 0, "fetched_at": "x", "response": {"products": products}}, ensure_ascii=False) + "\n", encoding="utf-8")


def _p(i, name):
    return {"id": i, "productName": name, "brand": "브랜드 (B)", "brand_name": "브랜드", "obsolete": False, "updateTime": 1700000000,
            "product_capacity": "30mL", "product_price": 10000, "goods": [{"id": 70000 + i}]}


def test_bookmarklet_href_collapses_whitespace():
    href = links.bookmarklet_href("(function () {\n  var a = 1;\n  alert(a);\n})();")
    assert href.startswith("javascript:(function () { var a = 1; alert(a); })();")
    assert "\n" not in href


def test_build_candidates_uses_selected_only(tmp_path):
    _write_search(tmp_path, "PDRN", [_p(i, f"PDRN {i}") for i in range(5)])
    _write_search(tmp_path, "ha", [_p(i, f"히알루론 {i}") for i in range(5)])
    ings = [{"key": "PDRN", "label": "PDRN", "name_patterns": ["pdrn"], "selected": True},
            {"key": "ha", "label": "히알루론산", "name_patterns": ["히알루론"], "selected": False}]
    c = links.build_candidates(tmp_path, ings, top_n=3)
    assert list(c.keys()) == ["PDRN"] and len(c["PDRN"]) == 3 and c["PDRN"][0]["id"] == 0


def test_render_html_has_bookmarklets_links_and_verify_group():
    cands = {"PDRN": [{"id": 1, "name": "PDRN 세럼", "brand": "브랜드", "rank_index": 0}]}
    verify = [{"id": 2140532, "brand": "비플레인", "name": "시카 PDRN 스킨 부스터 세럼"}]
    html = links.render_html(cands, verify, "(function(){alert(1)})();", "(function(){alert(2)})();", labels={"PDRN": "PDRN"})
    assert 'href="javascript:(function(){alert(1)})();"' in html and 'href="javascript:(function(){alert(2)})();"' in html
    assert 'href="https://www.hwahae.co.kr/products/1"' in html and 'target="_blank"' in html
    assert "검증" in html and "products/2140532" in html and "비플레인" in html
    assert "PDRN 세럼" in html and "1개" in html


def test_write_links_writes_two_files(tmp_path):
    _write_search(tmp_path, "PDRN", [_p(i, f"PDRN {i}") for i in range(3)])
    ings = [{"key": "PDRN", "label": "PDRN", "name_patterns": ["pdrn"], "selected": True}]
    cpath, hpath = links.write_links(tmp_path, tmp_path / "derived", ings, 2, [], "(function(){})();", "(function(){})();")
    assert json.loads(cpath.read_text(encoding="utf-8"))["PDRN"][1]["id"] == 1
    assert hpath.name == "collect-links.html" and "products/0" in hpath.read_text(encoding="utf-8")
