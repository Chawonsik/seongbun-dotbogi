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
