from crawler import run


def test_parse_args_defaults():
    a = run.parse_args(["search"])
    assert a.step == "search" and a.top_n == 30 and a.max_pages == 250 and a.force is False and a.only is None and a.file is None


def test_parse_args_ingest_file_and_flags():
    a = run.parse_args(["ingest", "sd-collect-1.json", "--only", "PDRN", "--force", "--top-n", "3"])
    assert a.step == "ingest" and a.file == "sd-collect-1.json" and a.only == "PDRN" and a.force and a.top_n == 3


def test_filter_only():
    ings = [{"key": "PDRN"}, {"key": "cica"}]
    assert [i["key"] for i in run.filter_only(ings, "cica")] == ["cica"]
    assert [i["key"] for i in run.filter_only(ings, None)] == ["PDRN", "cica"]


def test_links_only_forces_selected():
    ings = [{"key": "PDRN", "selected": False}]
    out = run.force_selected(ings)
    assert out[0]["selected"] is True and ings[0]["selected"] is False   # 원본은 그대로


def test_verify_products_reads_given_baseline(tmp_path):
    import json
    base = tmp_path / "baseline-data.json"
    base.write_text(json.dumps({"products": [{"id": 1, "brand": "b", "name": "n", "pos": 2}, {"id": 2}]}, ensure_ascii=False), encoding="utf-8")
    assert run._verify_products(base) == [{"id": 1, "brand": "b", "name": "n"}, {"id": 2, "brand": "", "name": ""}]
    assert run._verify_products(tmp_path / "missing.json") == []


def test_parse_args_publish_flag():
    assert run.parse_args(["derive"]).publish is False
    assert run.parse_args(["derive", "--publish"]).publish is True


def test_baseline_path_prefers_derived_copy(tmp_path, monkeypatch):
    monkeypatch.setattr(run.config, "DERIVED_DIR", tmp_path)
    monkeypatch.setattr(run.config, "LANDING_DIR", tmp_path / "landing")
    assert run.baseline_path() == tmp_path / "landing" / "data.json"
    (tmp_path / "baseline-data.json").write_text("{}", encoding="utf-8")
    assert run.baseline_path() == tmp_path / "baseline-data.json"


def test_is_under(tmp_path):
    assert run._is_under(tmp_path / "exports" / "a.json", tmp_path)
    assert not run._is_under(tmp_path.parent / "a.json", tmp_path)
