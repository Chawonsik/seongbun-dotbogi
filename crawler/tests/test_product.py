import json
from pathlib import Path

import pytest

from crawler import product

FIX = json.loads((Path(__file__).parent / "fixtures" / "next_data_product.json").read_text(encoding="utf-8"))


def test_extract_ingredients_keeps_order_and_fields():
    ings = product.extract_ingredients(FIX)
    assert [i["korean"] for i in ings] == ["정제수, 증류수, 물", "글리세린", "소듐디엔에이"]
    assert [i["id"] for i in ings] == [5321, 1, 2]
    assert ings[0]["ewg"] == "1" and ings[0]["purposes"][0]["group_name"] == "피부 보습"


def test_extract_ingredients_raises_when_missing():
    with pytest.raises(ValueError):
        product.extract_ingredients({"goodsProductsData": None})
    with pytest.raises(ValueError):
        product.extract_ingredients({"productIngredientInfoData": {"ingredients": []}})


def test_run_products_skips_existing_and_writes_new(tmp_path, monkeypatch):
    pdir = tmp_path / "products"
    pdir.mkdir(parents=True)
    (pdir / "1.json").write_text("{}", encoding="utf-8")
    calls = []

    def fake_fetch(page, pid):
        calls.append(pid)
        return {"ingredients": product.extract_ingredients(FIX), "final_url": f"u/{pid}"}

    monkeypatch.setattr(product, "fetch_product", fake_fetch)
    monkeypatch.setattr(product, "_open_browser", lambda headless: (None, None, object()))
    monkeypatch.setattr(product.time, "sleep", lambda s: None)
    cands = {"PDRN": [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]}
    monkeypatch.setattr(product.schedule, "wait_if_refresh_window", lambda log=print: None)
    result = product.run_products(tmp_path, cands, sleep_s=0)
    assert calls == [2] and {k: result[k] for k in ("ok", "fail", "skip")} == {"ok": 1, "fail": 0, "skip": 1}
    assert result["started_at"] <= result["finished_at"]
    saved = json.loads((pdir / "2.json").read_text(encoding="utf-8"))
    assert saved["id"] == 2 and saved["key"] == "PDRN" and saved["ingredients"][2]["korean"] == "소듐디엔에이"
