from crawler import pick

ING = {"key": "PDRN", "name_patterns": ["pdrn", "피디알엔"]}


def _p(i, name, obsolete=False):
    return {"id": i, "productName": name, "brand": "브랜드 (B)", "brand_name": "브랜드", "obsolete": obsolete,
            "updateTime": 1700000000, "product_capacity": "30mL", "product_price": 20000, "_rank_index": i}


def test_select_filters_name_and_obsolete_and_keeps_rank_order():
    products = [_p(0, "PDRN 세럼"), _p(1, "레티놀 세럼"), _p(2, "피디알엔 크림", obsolete=True), _p(3, "PDRN 토너")]
    out = pick.select_candidates(products, ING, top_n=15)
    assert [c["id"] for c in out] == [0, 3]
    assert out[0]["name"] == "PDRN 세럼" and out[0]["rank_index"] == 0 and out[0]["brand"] == "브랜드"


def test_select_top_n_and_fewer_is_fine():
    products = [_p(i, f"PDRN {i}") for i in range(20)]
    assert len(pick.select_candidates(products, ING, top_n=15)) == 15
    assert len(pick.select_candidates(products[:4], ING, top_n=15)) == 4


def test_select_records_acid_in_name():
    ing = {"key": "acids", "name_patterns": ["아하", "바하", "aha", "bha"],
           "acid_group": {"아하": ["아하", "aha"], "바하": ["바하", "bha"]}}
    out = pick.select_candidates([_p(0, "AHA BHA 토너")], ing)
    assert out[0]["acid_in_name"] == ["아하", "바하"]
    assert pick.select_candidates([_p(0, "PDRN 세럼")], ING)[0]["acid_in_name"] == []
