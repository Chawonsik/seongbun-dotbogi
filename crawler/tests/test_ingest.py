import json
from pathlib import Path

from crawler import ingest

FIX = Path(__file__).parent / "fixtures" / "sd-collect-sample.json"


def test_load_export_returns_records():
    recs = ingest.load_export(FIX)
    assert len(recs) == 3 and recs[0]["product_id"] == 2113285


def test_resolve_product_id_prefers_product_id_then_goods_map():
    assert ingest.resolve_product_id({"product_id": 5, "goods_id": 9}, {9: 7}) == 5
    assert ingest.resolve_product_id({"product_id": None, "goods_id": 9}, {9: 7}) == 7
    assert ingest.resolve_product_id({"product_id": None, "goods_id": 1}, {9: 7}) is None


def test_ingest_export_saves_by_key_and_skips_bad(tmp_path):
    derived = tmp_path / "derived"
    derived.mkdir()
    cands = {"PDRN": [{"id": 2113285, "name": "PDRN 세럼", "brand": "아누아", "rank_index": 0, "update_time": 1, "capacity": "30mL", "price": 1, "acid_in_name": []},
                      {"id": 2000002, "name": "테스트 PDRN 토너", "brand": "테스트브랜드", "rank_index": 1, "update_time": 1, "capacity": "170mL", "price": 1, "acid_in_name": []}],
             "retinoid": [{"id": 2000002, "name": "테스트 PDRN 토너", "brand": "테스트브랜드", "rank_index": 3, "update_time": 1, "capacity": "170mL", "price": 1, "acid_in_name": []}]}
    (derived / "candidates.json").write_text(json.dumps(cands, ensure_ascii=False), encoding="utf-8")
    sdir = tmp_path / "search"
    sdir.mkdir()
    (sdir / "PDRN.jsonl").write_text(json.dumps({"term": "t", "page": 0, "fetched_at": "x", "response": {"products": [
        {"id": 2000002, "productName": "테스트 PDRN 토너", "goods": [{"id": 70406}]}]}}, ensure_ascii=False) + "\n", encoding="utf-8")
    (sdir / "PDRN.meta.json").write_text("{}", encoding="utf-8")
    result = ingest.ingest_export(FIX, tmp_path, derived, ingredients=[{"key": "PDRN"}, {"key": "retinoid"}])
    assert result == {"saved": 3, "skipped": 1}
    saved = sorted(p.name for p in (tmp_path / "products").glob("*.json"))
    assert saved == ["PDRN__2000002.json", "PDRN__2113285.json", "retinoid__2000002.json"]
    rec = json.loads((tmp_path / "products" / "PDRN__2113285.json").read_text(encoding="utf-8"))
    assert rec["key"] == "PDRN" and rec["candidate"]["name"] == "PDRN 세럼" and rec["ingredients"][1]["id"] == 2
    assert rec["final_url"].startswith("https://www.hwahae.co.kr/goods/69360") and rec["collected_at"] == "2026-09-29T15:20:11+09:00"
    skipped = (derived / "ingest-skipped.csv").read_text(encoding="utf-8")
    assert "999" in skipped and "전성분 없음" in skipped


def test_ingest_export_unknown_product_goes_to_verify(tmp_path):
    derived = tmp_path / "derived"
    derived.mkdir()
    (derived / "candidates.json").write_text("{}", encoding="utf-8")
    export = tmp_path / "e.json"
    export.write_text(json.dumps({"records": {"5": {"product_id": 5, "goods_id": None, "url": "u", "title": "브랜드X 제품X", "collected_at": "2026-09-29T00:00:00+09:00",
                                                     "ingredients": [{"id": 1, "korean": "정제수", "english": "", "ewg": "1", "purposes": []}]}}}, ensure_ascii=False), encoding="utf-8")
    result = ingest.ingest_export(export, tmp_path, derived, ingredients=[])
    assert result == {"saved": 1, "skipped": 0}
    rec = json.loads((tmp_path / "products" / "verify__5.json").read_text(encoding="utf-8"))
    assert rec["key"] == "verify" and rec["candidate"] == {"id": 5, "name": "브랜드X 제품X", "brand": ""}


def test_ingest_export_skips_when_product_id_and_goods_id_disagree(tmp_path):
    derived = tmp_path / "derived"
    derived.mkdir()
    (derived / "candidates.json").write_text("{}", encoding="utf-8")
    sdir = tmp_path / "search"
    sdir.mkdir()
    (sdir / "PDRN.jsonl").write_text(json.dumps({"term": "t", "page": 0, "fetched_at": "x", "response": {"products": [
        {"id": 7, "productName": "PDRN 7", "goods": [{"id": 9}]}]}}) + chr(10), encoding="utf-8")
    export = tmp_path / "e.json"
    export.write_text(json.dumps({"records": {"5": {"product_id": 5, "goods_id": 9, "url": "u", "title": "t", "collected_at": "2026-09-29T00:00:00+09:00",
                                                     "ingredients": [{"id": 1, "korean": "정제수", "english": "", "ewg": "1", "purposes": []}]}}}, ensure_ascii=False), encoding="utf-8")
    result = ingest.ingest_export(export, tmp_path, derived, ingredients=[{"key": "PDRN"}])
    assert result == {"saved": 0, "skipped": 1}
    assert ingest.ID_MISMATCH == "번호 불일치"
    assert "번호 불일치" in (derived / "ingest-skipped.csv").read_text(encoding="utf-8")
    assert not list((tmp_path / "products").glob("*.json"))
