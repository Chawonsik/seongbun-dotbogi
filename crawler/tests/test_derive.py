import json

from crawler import derive

CFG = [
    {"key": "PDRN", "label": "PDRN", "category": "", "inci_patterns": ["디엔에이"], "selected": True, "name_patterns": ["pdrn"], "search_terms": ["PDRN"]},
    {"key": "cica", "label": "시카 계열", "category": "", "inci_patterns": ["병풀"], "selected": False, "name_patterns": ["시카"], "search_terms": ["시카"]},
]
MARKERS = ["카보머", "향료"]


def _rec(pid, ings, price=30000, cap="30mL", key="PDRN"):
    items = [(i if isinstance(i, tuple) else (sum(map(ord, i)), i)) for i in ings]
    return {"id": pid, "key": key, "candidate": {"id": pid, "name": f"제품{pid}", "brand": "브랜드", "price": price, "capacity": cap,
                                                 "update_time": 1700000000, "acid_in_name": []},
            "ingredients": [{"id": n, "korean": k, "english": "", "ewg": "1", "purposes": []} for n, k in items],
            "final_url": "u", "collected_at": "2026-09-29T15:20:11+09:00"}


def test_price_per_ml():
    assert derive.price_per_ml(30000, "30mL") == 1000
    assert derive.price_per_ml(25000, "170ml / 5.7 fl.oz.") == 147
    assert derive.price_per_ml(10000, "1매") is None
    assert derive.price_per_ml(None, "30mL") is None


def test_derive_product_positions_and_bands():
    rec = _rec(1, ["정제수", "글리세린", "소듐디엔에이", "병풀추출물", "카보머", "향료"])
    p = derive.derive_product(rec, CFG[0], CFG, MARKERS)
    assert p["id"] == 1 and p["chip"] == "PDRN" and p["pos"] == 3 and p["total"] == 6 and p["boundary"] == 5
    assert p["rel"] == round(2 / 5, 4) and p["price_per_ml"] == 1000 and p["registered"] == "2023-11-14"
    assert p["collected_at"] == "2026-09-29"
    assert {"name": "시카 계열", "pos": 4, "top": True} in p["families"]
    assert "ingredients" not in p and "review_count" not in p


def test_derive_product_returns_none_when_unmatched():
    assert derive.derive_product(_rec(2, ["정제수", "글리세린"]), CFG[0], CFG, MARKERS) is None


def test_common_ingredients_by_hwahae_id_not_name():
    recs = [_rec(1, [(5321, "정제수, 물"), (2, "1,2-헥산다이올"), (9, "소듐디엔에이")]),
            _rec(2, [(2, "1"), (5321, "정제수, 물"), (77, "향료")]),
            _rec(3, [(5321, "정제수"), (2, "1,2-헥산다이올"), (78, "글리세린")]),
            _rec(4, [(2, "1,2-헥산다이올"), (5321, "정제수, 물"), (79, "카보머")]),
            _rec(5, [(5321, "정제수, 물"), (2, "1,2-헥산다이올"), (80, "병풀추출물")])]
    assert derive.common_ingredients(recs) == ["1,2-헥산다이올", "정제수"]
    diff = [_rec(i, [(i, "글리세린")]) for i in range(1, 6)]
    assert derive.common_ingredients(diff) == []


def test_common_ingredients_hidden_when_too_few_products():
    recs = [_rec(i, [(5321, "정제수"), (2, "1,2-헥산다이올")]) for i in range(1, 5)]
    assert derive.common_ingredients(recs[:1]) == []
    assert derive.common_ingredients(recs) == []


def test_family_match_table_lists_hit_ingredient_and_id():
    cfg = [{"key": "PDRN", "label": "PDRN", "inci_patterns": ["디엔에이"]},
           {"key": "cica", "label": "시카 계열", "inci_patterns": ["병풀", "마데카소사이드"]}]
    raws = [_rec(1, [(10, "정제수"), (20, "소듐디엔에이"), (30, "병풀추출물")]),
            _rec(2, [(10, "정제수"), (31, "마데카소사이드"), (30, "병풀추출물")]),
            _rec(3, [(10, "정제수"), (21, "하이드롤라이즈드디엔에이")])]
    rows = derive.family_match_table(raws, cfg)
    assert rows == [
        {"family": "PDRN", "ingredient_id": 20, "ingredient": "소듐디엔에이", "products": 1},
        {"family": "PDRN", "ingredient_id": 21, "ingredient": "하이드롤라이즈드디엔에이", "products": 1},
        {"family": "시카 계열", "ingredient_id": 30, "ingredient": "병풀추출물", "products": 1},
        {"family": "시카 계열", "ingredient_id": 31, "ingredient": "마데카소사이드", "products": 1},
    ]


def test_build_data_only_selected_skips_verify_and_records_unmatched(tmp_path):
    pdir = tmp_path / "products"
    pdir.mkdir(parents=True)
    for rec in [_rec(1, ["정제수", "소듐디엔에이", "카보머"]), _rec(2, ["정제수", "글리세린"]),
                _rec(3, ["정제수", "병풀추출물"], key="cica"), _rec(4, ["정제수", "소듐디엔에이"], key="verify")]:
        (pdir / f"{rec['key']}__{rec['id']}.json").write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    data, unmatched = derive.build_data(tmp_path, CFG, MARKERS, version="2026-09-29-pilot", top6_rates={"PDRN": 0.42})
    assert [i["key"] for i in data["ingredients"]] == ["PDRN"]
    assert [p["id"] for p in data["products"]] == [1]
    ing = data["ingredients"][0]
    assert ing["n_products"] == 1 and ing["median_rel"] == 0.5 and ing["back_half"] == 1 and ing["low_zone"] == 0 and ing["top6_rate"] == 0.42 and ing["common"] == []
    assert unmatched == [{"key": "PDRN", "id": 2, "name": "제품2", "brand": "브랜드"}]
    assert data["family_dict"][0]["name"] == "PDRN" and "카보머" in data["one_percent_markers"]


def test_verify_table_compares_with_old_landing():
    old = {"products": [{"id": 4, "brand": "b", "name": "n", "pos": 2, "total": 2, "boundary": None}]}
    raws = [_rec(4, ["정제수", "소듐디엔에이"], key="verify"), _rec(5, ["정제수"], key="verify")]
    rows = derive.verify_table(raws, old, MARKERS, pdrn_patterns=["디엔에이"])
    assert rows[0] == {"id": 4, "name": "n", "old_pos": 2, "new_pos": 2, "old_total": 2, "new_total": 2, "old_boundary": None, "new_boundary": None, "same": True}
    assert rows[1]["id"] == 5 and rows[1]["old_pos"] is None and rows[1]["new_pos"] is None and rows[1]["same"] is False


def test_write_outputs_writes_four_files(tmp_path):
    data = {"version": "v", "source": "s", "family_dict": [], "one_percent_markers": [], "ingredients": [], "products": []}
    fam = [{"family": "PDRN", "ingredient_id": 20, "ingredient": "소듐디엔에이", "products": 3}]
    ver = [{"id": 4, "name": "n", "old_pos": 2, "new_pos": 2, "old_total": 2, "new_total": 2, "old_boundary": None, "new_boundary": None, "same": True}]
    top6 = [{"id": 4, "key": "PDRN", "name": "n", "search_top6": "a | b", "page_top6": "a | b", "same_order": True, "same_set": True}]
    derive.write_outputs(data, [], fam, ver, top6, tmp_path / "landing", tmp_path / "derived", write_landing=True)
    assert (tmp_path / "landing" / "data.json").exists() and (tmp_path / "derived" / "data.json").exists()
    for name in ("unmatched.csv", "family_matches.csv", "verify.csv", "top6-check.csv"):
        assert (tmp_path / "derived" / name).exists()
    assert "소듐디엔에이" in (tmp_path / "derived" / "family_matches.csv").read_text(encoding="utf-8")


def test_write_outputs_can_skip_landing(tmp_path):
    data = {"version": "v", "source": "s", "family_dict": [], "one_percent_markers": [], "ingredients": [], "products": []}
    derive.write_outputs(data, [], [], [], [], tmp_path / "landing", tmp_path / "derived", write_landing=False)
    assert not (tmp_path / "landing" / "data.json").exists()
    assert json.loads((tmp_path / "derived" / "data.json").read_text(encoding="utf-8"))["version"] == "v"
    for name in ("unmatched.csv", "family_matches.csv", "verify.csv", "top6-check.csv"):
        assert (tmp_path / "derived" / name).exists()


def test_write_outputs_does_not_touch_landing_by_default(tmp_path):
    landing = tmp_path / "landing"
    landing.mkdir()
    (landing / "data.json").write_text("LIVE", encoding="utf-8")
    data = {"version": "v", "source": "s", "family_dict": [], "one_percent_markers": [], "ingredients": [], "products": []}
    derive.write_outputs(data, [], [], [], [], landing, tmp_path / "derived")
    assert (landing / "data.json").read_text(encoding="utf-8") == "LIVE"


def test_top6_check_table_order_set_and_exclusion():
    names = ["정제수", "글리세린", "부틸렌글라이콜", "소듐디엔에이", "나이아신아마이드", "판테놀", "향료"]
    same = _rec(1, names)
    swapped = _rec(2, names, key="verify")
    absent = _rec(3, names)
    search = {1: names[:6], 2: [names[1], names[0]] + names[2:6], 99: ["x"]}
    rows = derive.top6_check_table([same, swapped, absent], search)
    assert [r["id"] for r in rows] == [1, 2]                                # 검색 목록에 없는 3 은 제외, verify 는 포함
    assert rows[0] == {"id": 1, "key": "PDRN", "name": "제품1", "search_top6": " | ".join(names[:6]), "page_top6": " | ".join(names[:6]),
                       "same_order": True, "same_set": True}
    assert rows[1]["key"] == "verify" and rows[1]["same_order"] is False and rows[1]["same_set"] is True
    assert rows[1]["page_top6"] == " | ".join(names[:6])


def test_top6_check_table_uses_first_name_of_page_and_flags_different_set():
    rec = _rec(1, ["정제수", "글리세린"])
    rec["ingredients"][0]["korean"] = "정제수, 물"
    rows = derive.top6_check_table([rec], {1: ["정제수", "다른성분"]})
    assert rows[0]["page_top6"] == "정제수 | 글리세린" and rows[0]["same_order"] is False and rows[0]["same_set"] is False
