from crawler import config


def test_load_ingredients_has_18_with_required_keys():
    items = config.load_ingredients()
    assert len(items) == 18
    for it in items:
        for k in ("key", "label", "search_terms", "name_patterns", "inci_patterns", "selected"):
            assert k in it, (it.get("key"), k)
        assert it["search_terms"] and it["name_patterns"] and it["inci_patterns"]


def test_keys_are_unique():
    keys = [it["key"] for it in config.load_ingredients()]
    assert len(keys) == len(set(keys))


def test_load_markers_contains_phenoxyethanol():
    assert "페녹시에탄올" in config.load_markers()


def test_normalize_lowercases_and_strips_spaces():
    assert config.normalize(" PDRN 히알루론산  캡슐 ") == "pdrn히알루론산캡슐"
