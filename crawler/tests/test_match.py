from crawler import match

CFG = [
    {"key": "PDRN", "label": "PDRN", "inci_patterns": ["디엔에이", "폴리데옥시리보뉴클레오타이드"]},
    {"key": "niacinamide", "label": "나이아신아마이드", "inci_patterns": ["나이아신아마이드"]},
    {"key": "cica", "label": "시카 계열", "inci_patterns": ["병풀", "마데카소사이드"]},
]
MARKERS = ["페녹시에탄올", "카보머", "향료"]
INCI = ["정제수", "글리세린", "나이아신아마이드", "소듐디엔에이", "병풀추출물", "카보머", "향료", "마데카소사이드"]


def test_name_matches_ignores_case_and_spaces():
    assert match.name_matches("아누아 PDRN 히알루론산 세럼", ["pdrn"])
    assert match.name_matches("피디 알엔 앰플", ["피디알엔"])
    assert not match.name_matches("레티놀 세럼", ["pdrn", "피디알엔"])


def test_find_position_is_one_based_first_hit():
    assert match.find_position(INCI, ["디엔에이"]) == 4
    assert match.find_position(INCI, ["병풀", "마데카소사이드"]) == 5
    assert match.find_position(INCI, ["엑소좀"]) is None


def test_find_boundary_first_marker():
    assert match.find_boundary(INCI, MARKERS) == 6
    assert match.find_boundary(["정제수", "글리세린"], MARKERS) is None


def test_find_families_marks_top_before_boundary():
    fams = match.find_families(INCI, CFG, boundary=6)
    assert fams == [
        {"name": "PDRN", "pos": 4, "top": True},
        {"name": "나이아신아마이드", "pos": 3, "top": True},
        {"name": "시카 계열", "pos": 5, "top": True},
    ]
    fams2 = match.find_families(["정제수", "카보머", "소듐디엔에이"], CFG, boundary=2)
    assert fams2 == [{"name": "PDRN", "pos": 3, "top": False}]


def test_find_families_without_boundary_is_top():
    fams = match.find_families(["소듐디엔에이"], CFG, boundary=None)
    assert fams == [{"name": "PDRN", "pos": 1, "top": True}]


def test_acid_in_name():
    group = {"아하": ["아하", "aha"], "바하": ["바하", "bha"], "파하": ["파하", "pha"]}
    assert match.acid_in_name("AHA BHA PHA 30일 세럼", group) == ["아하", "바하", "파하"]
    assert match.acid_in_name("바하 토너", group) == ["바하"]
    assert match.acid_in_name("수분 크림", group) == []


def test_relative_position():
    assert match.relative_position(1, 10) == 0.0
    assert match.relative_position(10, 10) == 1.0
    assert match.relative_position(5, 1) == 0.0  # total 1 이면 0 나누기 방지


def test_first_name_keeps_comma_inside_ingredient_name():
    # 화해 korean 필드는 "이름, 별칭" 을 쉼표+공백으로 잇는다. "1,2-헥산다이올" 의 쉼표는 이름 안이라 잘리면 안 된다
    assert match.first_name("1,2-헥산다이올") == "1,2-헥산다이올"
    assert match.first_name("1,2-헥산다이올, 헥산다이올") == "1,2-헥산다이올"
    assert match.first_name("정제수, 증류수, 물") == "정제수"
    assert match.first_name(None) == ""


def test_latin_patterns_use_word_boundary():
    assert match.name_matches("AHA BHA PHA 30일 세럼", ["pha"])
    assert not match.name_matches("알파 Alpha Arbutin 세럼", ["pha"])   # alpha 안의 pha
    assert not match.name_matches("LHA 토너", ["bha"])                 # lha 와 bha 는 다른 글자
    assert match.name_matches("리쥬란 힐러 pdrn", ["pdrn"])


def test_acid_group_overlap_is_fine_inside_one_bundle():
    # 라하(카프릴로일살리실릭애씨드)는 바하(살리실릭애씨드) 글자를 포함한다. 한 묶음이라 처음 나오는 산이 이름 성분이면 된다
    acids = ["글라이콜릭애씨드", "살리실릭애씨드", "카프릴로일살리실릭애씨드"]
    assert match.find_position(["정제수", "카프릴로일살리실릭애씨드", "살리실릭애씨드"], acids) == 2
    assert match.find_position(["정제수", "살리실릭애씨드", "카프릴로일살리실릭애씨드"], acids) == 2


def test_exosome_pattern_does_not_catch_cell_culture():
    # "세포배양액" 은 엑소좀이 아닌 배양액 제품까지 잡아서 패턴에서 뺐다
    from crawler import config
    exo = [i for i in config.load_ingredients() if i["key"] == "exosome"][0]
    assert match.find_position(["정제수", "인체줄기세포배양액", "엑소좀"], exo["inci_patterns"]) == 3
    assert match.find_position(["정제수", "인체줄기세포배양액"], exo["inci_patterns"]) is None
    assert "세포배양액" not in exo["inci_patterns"]
