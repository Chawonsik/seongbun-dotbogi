"""후보 성분마다 검색 결과 전체를 받아 data/raw/search/ 에 저장한다."""
from __future__ import annotations

import json
import math
from pathlib import Path

from crawler import schedule
from crawler.config import RAW_DIR
from crawler.hwahae_api import PAGE_SIZE, BlockedError, SearchClient

MAX_PAGES = 250


def _now() -> str:
    return schedule.now_iso()


def collect_term(client: SearchClient, term: str, out_jsonl: Path, max_pages: int = MAX_PAGES) -> dict:
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    started = _now()
    pages = 0
    total = None
    capped = False
    incomplete = False
    with open(out_jsonl, "a", encoding="utf-8") as f:
        page_num = 0
        while True:
            page = client.fetch_page(term, page_num)
            total = page.total_count
            f.write(json.dumps({"term": term, "page": page_num, "fetched_at": _now(), "response": page.raw}, ensure_ascii=False) + "\n")
            pages += 1
            page_num += 1
            needed = math.ceil(total / PAGE_SIZE) if total else 0
            if page_num >= needed:
                break
            if page.count == 0:
                # total_count 가 아직 더 남았다고 말하는데 빈 페이지가 온 상황: API 글리치일 수 있으니
                # 완료로 오인하지 않도록 incomplete 로 표시하고 멈춘다.
                incomplete = True
                break
            if page_num >= max_pages:
                capped = True
                break
    return {
        "term": term,
        "total_count": total or 0,
        "pages": pages,
        "max_pages": max_pages,
        "capped": capped,
        "incomplete": incomplete,
        "started_at": started,
        "finished_at": _now(),
    }


def collect_ingredient(client: SearchClient, ing: dict, raw_dir: Path = RAW_DIR, max_pages: int = MAX_PAGES, force: bool = False) -> dict:
    sdir = raw_dir / "search"
    jsonl = sdir / f"{ing['key']}.jsonl"
    meta_path = sdir / f"{ing['key']}.meta.json"
    if meta_path.exists() and not force:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        # 낮은 상한(스모크 실행)으로 잘린 결과는 더 큰 상한 요청 때 다시 받는다.
        if not (meta.get("capped") and meta.get("max_pages", 0) < max_pages):
            meta["skipped"] = True
            return meta
    if jsonl.exists():
        jsonl.unlink()
    started = _now()
    per_term = [collect_term(client, t, jsonl, max_pages=max_pages) for t in ing["search_terms"]]
    meta = {
        "key": ing["key"],
        "terms": list(ing["search_terms"]),
        "total_count": {m["term"]: m["total_count"] for m in per_term},
        "pages": {m["term"]: m["pages"] for m in per_term},
        "max_pages": max_pages,
        "capped": any(m["capped"] for m in per_term),
        "capped_terms": [m["term"] for m in per_term if m["capped"]],
        "incomplete": any(m["incomplete"] for m in per_term),
        "incomplete_terms": [m["term"] for m in per_term if m["incomplete"]],
        "started_at": started,
        "finished_at": _now(),
        "skipped": False,
    }
    sdir.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta


def read_products(key: str, raw_dir: Path = RAW_DIR) -> list[dict]:
    """jsonl 을 읽어 제품 목록으로. 검색어별 랭킹을 번갈아 합쳐(t1[0], t2[0], t1[1], ...) 순위를 매긴다.

    같은 id 는 먼저 나온 것만 남기고 _term, _page, _rank_index 를 붙인다.
    """
    jsonl = raw_dir / "search" / f"{key}.jsonl"
    if not jsonl.exists():
        return []
    per_term: dict[str, list[dict]] = {}
    seen_in_term: dict[str, set] = {}
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        term = rec["term"]
        seen = seen_in_term.setdefault(term, set())
        items = per_term.setdefault(term, [])
        for p in rec["response"].get("products", []):
            pid = p.get("id")
            if pid in seen:
                continue
            seen.add(pid)
            q = dict(p)
            q["_term"] = term
            q["_page"] = rec["page"]
            items.append(q)
    out: list[dict] = []
    seen_ids: set = set()
    lists = list(per_term.values())
    for i in range(max((len(x) for x in lists), default=0)):
        for items in lists:
            if i < len(items) and items[i].get("id") not in seen_ids:
                q = items[i]
                seen_ids.add(q.get("id"))
                q["_rank_index"] = len(out)
                out.append(q)
    return out


def run_search(raw_dir: Path, ingredients: list[dict], client: SearchClient, max_pages: int = MAX_PAGES, force: bool = False) -> list[dict]:
    metas = []
    print(f"[search] start {_now()}")
    for ing in ingredients:
        schedule.wait_if_refresh_window()
        try:
            meta = collect_ingredient(client, ing, raw_dir, max_pages=max_pages, force=force)
        except BlockedError as e:
            print(f"[search] BLOCKED at {ing['key']} {_now()}: {e}. 완료: {[m['key'] for m in metas]}")
            raise
        if meta.get("skipped"):
            status = "skip"
        elif meta["capped"]:
            status = "capped"
        elif meta.get("incomplete"):
            status = "incomplete"
        else:
            status = "ok"
        print(f"[search] {ing['key']:12s} {status:6s} total={meta['total_count']} pages={meta['pages']}")
        metas.append(meta)
    print(f"[search] end {_now()}")
    return metas
