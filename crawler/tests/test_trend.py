import csv
import json
from datetime import date, datetime, timezone

from crawler import trend

ING = {"key": "PDRN", "label": "PDRN", "name_patterns": ["pdrn"], "inci_patterns": ["디엔에이"]}
TODAY = date(2026, 9, 29)


def _ts(y, m, d):
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp())


def _p(i, name, ts, obsolete=False, top6=None):
    return {"id": i, "productName": name, "updateTime": ts, "obsolete": obsolete,
            "product_ingredients": [{"name": n, "is_matched": False} for n in (top6 or ["정제수", "글리세린"])]}


def test_count_registrations_windows_growth_and_top6():
    products = [
        _p(1, "PDRN a", _ts(2026, 1, 1), top6=["정제수", "소듐디엔에이"]),   # recent, top6 hit
        _p(2, "PDRN b", _ts(2025, 6, 1)),                                  # recent
        _p(3, "PDRN c", _ts(2023, 6, 1), top6=["정제수", "하이드롤라이즈드디엔에이"]),  # prior, hit
        _p(4, "PDRN d", _ts(2021, 1, 1)),                                  # older than 48m
        _p(5, "레티놀 e", _ts(2026, 1, 1)),                                 # name mismatch
        _p(6, "PDRN f", _ts(2026, 2, 1), obsolete=True, top6=["소듐디엔에이"]),  # obsolete: excluded everywhere
    ]
    c = trend.count_registrations(products, ING, TODAY)
    assert c == {"named_total": 4, "recent_24m": 2, "prior_24m": 1, "growth": 2 / 5, "top6_hit": 2, "top6_rate": 0.5}


def test_count_registrations_empty():
    assert trend.count_registrations([], ING, TODAY)["top6_rate"] == 0.0


def test_propose_selection_rule():
    rows = [{"key": k, "named_total": n} for k, n in
            (("a", 500), ("b", 400), ("c", 300), ("d", 200), ("e", 100), ("f", 90), ("g", 80), ("h", 70), ("i", 60), ("j", 50), ("k", 40), ("small", 14), ("ha", 9000))]
    got = trend.propose_selection(rows, top_n=9, min_named=15, always=("ha",))
    assert got == {"a", "b", "c", "d", "e", "f", "g", "h", "i", "ha"}   # ha 는 always 로 들어가고 9개 안에 안 셈
    assert "small" not in got and "j" not in got


def test_propose_selection_ha_not_double_counted():
    rows = [{"key": "ha", "named_total": 9000}] + [{"key": f"x{i}", "named_total": 100 - i} for i in range(9)]
    got = trend.propose_selection(rows)
    assert len(got) == 10 and "ha" in got and "x8" in got


def _write_search(tmp_path, key, products, capped=False, incomplete=False):
    sdir = tmp_path / "search"
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / f"{key}.meta.json").write_text(json.dumps({"total_count": {"t": len(products)}, "capped": capped, "incomplete": incomplete}), encoding="utf-8")
    (sdir / f"{key}.jsonl").write_text(json.dumps({"term": "t", "page": 0, "fetched_at": "x", "response": {"products": products}}, ensure_ascii=False) + "\n", encoding="utf-8")


def test_build_trend_orders_proposed_first_and_marks_capped(tmp_path):
    _write_search(tmp_path, "ha", [_p(i, "히알루론 x", _ts(2026, 1, 1)) for i in range(20)], capped=True)
    _write_search(tmp_path, "PDRN", [_p(i, "PDRN x", _ts(2026, 1, 1)) for i in range(30)])
    _write_search(tmp_path, "small", [_p(i, "small x", _ts(2026, 1, 1)) for i in range(5)])
    ings = [{"key": "ha", "label": "히알루론산", "name_patterns": ["히알루론"], "inci_patterns": ["하이알루로"]},
            {"key": "PDRN", "label": "PDRN", "name_patterns": ["pdrn"], "inci_patterns": ["디엔에이"]},
            {"key": "small", "label": "작음", "name_patterns": ["small"], "inci_patterns": ["x"]}]
    rows = trend.build_trend(tmp_path, ings, TODAY)
    assert [r["key"] for r in rows] == ["PDRN", "ha", "small"]        # 제안된 것 먼저(named_total 순), ha 는 always
    assert rows[0]["proposed"] is True and rows[1]["proposed"] is True and rows[2]["proposed"] is False
    assert rows[1]["capped"] is True and rows[1]["note"] == trend.CAPPED_NOTE
    assert rows[2]["note"] == trend.TOO_FEW_NOTE


def test_write_trend_csv(tmp_path):
    rows = [{"key": "PDRN", "label": "PDRN", "total_count": 1813, "capped": False, "incomplete": False,
             "named_total": 900, "recent_24m": 600, "prior_24m": 200, "growth": 3.0, "top6_hit": 90, "top6_rate": 0.1,
             "proposed": True, "note": ""}]
    path = tmp_path / "trend.csv"
    trend.write_trend_csv(rows, path)
    with open(path, encoding="utf-8", newline="") as f:
        got = list(csv.DictReader(f))
    assert got[0]["key"] == "PDRN" and got[0]["top6_rate"] == "0.1" and got[0]["proposed"] == "True"
