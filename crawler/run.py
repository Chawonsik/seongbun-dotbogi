"""크롤러 진입점. search -> trend -> (selected 표시) -> links -> 사람이 수집 -> ingest -> derive."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawler import config, derive, ingest, links, schedule, search, trend  # noqa: E402
from crawler.hwahae_api import BlockedError, SearchClient  # noqa: E402

TOOLS = config.ROOT / "tools" / "bookmarklet"


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="화해 유행 성분 수집 (검색은 자동, 전성분은 사람이 북마클릿으로)")
    ap.add_argument("step", choices=["search", "trend", "links", "ingest", "derive"])
    ap.add_argument("file", nargs="?", default=None, help="ingest: 북마클릿이 내보낸 JSON")
    ap.add_argument("--top-n", type=int, default=30, help="links: 성분당 링크 수")
    ap.add_argument("--max-pages", type=int, default=search.MAX_PAGES)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", default=None, help="성분 key 하나만")
    ap.add_argument("--publish", action="store_true", help="derive: 결과를 landing/data.json 에도 쓴다(배포용)")
    return ap.parse_args(argv)


def filter_only(ingredients: list[dict], only: str | None) -> list[dict]:
    return [i for i in ingredients if only is None or i["key"] == only]


def force_selected(ingredients: list[dict]) -> list[dict]:
    return [{**i, "selected": True} for i in ingredients]


def baseline_path() -> Path:
    """검증 기준선. 파일럿 시작 전 landing/data.json 을 고정해 둔 사본을 쓴다."""
    p = config.DERIVED_DIR / "baseline-data.json"
    if p.exists():
        return p
    print(f"경고: {p} 가 없어 landing/data.json 을 기준선으로 씁니다. derive --publish 뒤에는 기준선이 바뀝니다")
    return config.LANDING_DIR / "data.json"


def load_baseline(path: Path | None = None) -> dict:
    p = path or baseline_path()
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _verify_products(path: Path | None = None) -> list[dict]:
    old = load_baseline(path)
    return [{"id": x["id"], "brand": x.get("brand", ""), "name": x.get("name", "")} for x in old.get("products", [])]


def _is_under(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def main(argv=None) -> int:
    a = parse_args(argv)
    all_ings = config.load_ingredients()
    ings = filter_only(all_ings, a.only)
    if not ings:
        print(f"key 를 찾지 못했습니다: {a.only}")
        return 2
    if a.step == "search":
        schedule.wait_if_refresh_window()
        try:
            search.run_search(config.RAW_DIR, ings, SearchClient(), max_pages=a.max_pages, force=a.force)
        except BlockedError as e:
            print(f"[search] 차단으로 멈춤: {e}")
            return 3
    elif a.step == "trend":
        rows = trend.build_trend(config.RAW_DIR, ings, date.today())
        trend.write_trend_csv(rows, config.DERIVED_DIR / "trend.csv")
        trend.print_trend(rows)
    elif a.step == "links":
        target = force_selected(ings) if a.only else ings
        if not any(i.get("selected") for i in target):
            print("selected: true 인 성분이 없습니다. trend 를 보고 config/ingredients.json 에 표시하거나 --only KEY 로 지정하세요")
            return 2
        collect_js = (TOOLS / "collect.js").read_text(encoding="utf-8")
        export_js = (TOOLS / "export.js").read_text(encoding="utf-8")
        clear_js = (TOOLS / "clear.js").read_text(encoding="utf-8")
        links.write_links(config.RAW_DIR, config.DERIVED_DIR, target, a.top_n, _verify_products(), collect_js, export_js, clear_js)
    elif a.step == "ingest":
        if not a.file:
            print("ingest 에는 내보낸 JSON 파일 경로가 필요합니다")
            return 2
        if not Path(a.file).exists():
            print(f"파일을 찾을 수 없습니다: {a.file}")
            return 2
        if not _is_under(Path(a.file), config.RAW_DIR):
            print("주의: 전성분 원문이 든 파일입니다. data/raw/exports/ 로 옮겨 두세요")
        ingest.ingest_export(Path(a.file), config.RAW_DIR, config.DERIVED_DIR, all_ings)
    elif a.step == "derive":
        version = f"{date.today().isoformat()}-pilot"
        markers = config.load_markers()
        top6 = derive.load_top6_rates(config.DERIVED_DIR / "trend.csv")
        data, unmatched = derive.build_data(config.RAW_DIR, all_ings, markers, version, top6)
        raws = derive.load_raw(config.RAW_DIR)
        family_rows = derive.family_match_table([r for r in raws if r["key"] != derive.VERIFY_KEY], all_ings)
        old = load_baseline()
        pdrn = next((i["inci_patterns"] for i in all_ings if i["key"] == "PDRN"), ["디엔에이"])
        verify_rows = derive.verify_table(raws, old, markers, pdrn)
        if not data["ingredients"]:
            print("selected: true 인 성분이 없어 data.json 은 만들지 않습니다. verify 와 family 표만 씁니다")
            derive.write_outputs(data, unmatched, family_rows, verify_rows, config.LANDING_DIR, config.DERIVED_DIR, write_landing=False)
            return 0
        derive.write_outputs(data, unmatched, family_rows, verify_rows, config.LANDING_DIR, config.DERIVED_DIR, write_landing=a.publish)
        if not a.publish:
            print("landing/data.json 은 건드리지 않았습니다. 배포용으로 쓰려면 --publish")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
