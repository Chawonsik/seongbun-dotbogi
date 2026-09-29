"""제품 페이지에서 전성분을 읽는다. WAF 챌린지 때문에 Playwright(실제 브라우저)만 통과한다."""
from __future__ import annotations

import json
import time
from pathlib import Path

from crawler import schedule

PRODUCT_URL = "https://www.hwahae.co.kr/products/{id}"
RETRY_WAIT_S = 5.0
MAX_CONSECUTIVE_FAILS = 5


class ProductBlockedError(RuntimeError):
    """연속 실패가 많으면 차단으로 보고 멈춘다."""


def _now() -> str:
    return schedule.now_iso()


def extract_ingredients(page_props: dict) -> list[dict]:
    info = page_props.get("productIngredientInfoData") or {}
    items = info.get("ingredients") or []
    if not items:
        raise ValueError("productIngredientInfoData.ingredients 가 비어 있습니다")
    return [{"id": i.get("id"), "korean": i.get("korean"), "english": i.get("english"), "ewg": i.get("ewg"), "purposes": i.get("purposes") or []} for i in items]


def fetch_product(page, product_id: int) -> dict:
    page.goto(PRODUCT_URL.format(id=product_id), wait_until="domcontentloaded", timeout=45000)
    page.wait_for_selector("#__NEXT_DATA__", timeout=30000)
    raw = page.locator("#__NEXT_DATA__").text_content()
    data = json.loads(raw)
    props = data.get("props", {}).get("pageProps", {})
    return {"ingredients": extract_ingredients(props), "final_url": page.url}


def _open_browser(headless: bool):
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=headless)
    context = browser.new_context(locale="ko-KR", viewport={"width": 1280, "height": 900})
    page = context.new_page()
    return pw, browser, page


def run_products(raw_dir: Path, candidates_by_key: dict[str, list[dict]], sleep_s: float = 3.0, force: bool = False, headless: bool = True) -> dict:
    pdir = raw_dir / "products"
    pdir.mkdir(parents=True, exist_ok=True)
    errors = raw_dir / "errors.log"
    ok = fail = skip = 0
    consecutive = 0
    started = _now()
    print(f"[product] start {started}")
    pw, browser, page = _open_browser(headless)
    try:
        for key, cands in candidates_by_key.items():
            schedule.wait_if_refresh_window()
            for c in cands:
                out = pdir / f"{c['id']}.json"
                if out.exists() and not force:
                    skip += 1
                    continue
                last = None
                for attempt in range(3):
                    try:
                        got = fetch_product(page, c["id"])
                        rec = {"id": c["id"], "key": key, "candidate": c, "ingredients": got["ingredients"],
                               "final_url": got["final_url"], "collected_at": _now()}
                        out.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
                        ok += 1
                        last = None
                        break
                    except Exception as e:  # noqa: BLE001 - 수집은 한 건 실패로 멈추지 않는다
                        last = f"{type(e).__name__}: {e}"
                        time.sleep(RETRY_WAIT_S)
                if last:
                    fail += 1
                    consecutive += 1
                    with open(errors, "a", encoding="utf-8") as f:
                        f.write(f"{_now()}\t{key}\t{c['id']}\t{last}\n")
                    print(f"[product] FAIL {key} {c['id']} {last}")
                    if consecutive >= MAX_CONSECUTIVE_FAILS:
                        raise ProductBlockedError(f"연속 {consecutive}건 실패. 차단으로 보고 멈춥니다 ({_now()})")
                else:
                    consecutive = 0
                    print(f"[product] ok   {key} {c['id']} {c.get('name', '')[:30]}")
                time.sleep(sleep_s)
    finally:
        if browser is not None:
            browser.close()
        if pw is not None:
            pw.stop()
    finished = _now()
    print(f"[product] end {finished}")
    return {"ok": ok, "fail": fail, "skip": skip, "started_at": started, "finished_at": finished}
