"""유행 성분 선정용 판단 재료와 제안. 기준은 2026-09-29 에 숫자를 보기 전에 고정했다.

이름 단 제품 수(단종 제외) 상위 9개 + 히알루론산(비교 기준). 15개 미만은 제외. 증가율은 설명용.
"""
from __future__ import annotations

import csv
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from crawler import match
from crawler.search import read_products

FIELDS = ["key", "label", "total_count", "capped", "incomplete", "named_total", "recent_24m", "prior_24m", "growth",
          "top6_hit", "top6_rate", "proposed", "note"]
CAPPED_NOTE = "상한 250페이지에 잘림. 뒤쪽 제품이 빠져 named_total 과 증가율이 앞쪽(랭킹 상위)으로 치우침"
TOO_FEW_NOTE = "이름 단 제품 15개 미만이라 제외"
TOP_N = 9
MIN_NAMED = 15
ALWAYS = ("ha",)


def count_registrations(products: list[dict], ing: dict, today: date) -> dict:
    t_recent = datetime.combine(today - timedelta(days=730), datetime.min.time(), tzinfo=timezone.utc)
    t_prior = datetime.combine(today - timedelta(days=1460), datetime.min.time(), tzinfo=timezone.utc)
    named = recent = prior = top6 = 0
    for p in products:
        if p.get("obsolete") or not match.name_matches(p.get("productName", ""), ing["name_patterns"]):
            continue
        named += 1
        names = [x.get("name", "") for x in (p.get("product_ingredients") or [])]
        if match.find_position(names, ing["inci_patterns"]) is not None:
            top6 += 1
        ts = p.get("updateTime")
        if not ts:
            continue
        when = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        if when >= t_recent:
            recent += 1
        elif when >= t_prior:
            prior += 1
    return {"named_total": named, "recent_24m": recent, "prior_24m": prior, "growth": recent / max(prior, 5),
            "top6_hit": top6, "top6_rate": (top6 / named) if named else 0.0}


def propose_selection(rows: list[dict], top_n: int = TOP_N, min_named: int = MIN_NAMED, always: tuple = ALWAYS) -> set[str]:
    eligible = [r for r in rows if r["named_total"] >= min_named and r["key"] not in always]
    eligible.sort(key=lambda r: -r["named_total"])
    chosen = {r["key"] for r in eligible[:top_n]}
    chosen.update(k for k in always if any(r["key"] == k for r in rows))
    return chosen


def build_trend(raw_dir: Path, ingredients: list[dict], today: date | None = None) -> list[dict]:
    today = today or date.today()
    rows = []
    for ing in ingredients:
        meta_path = raw_dir / "search" / f"{ing['key']}.meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        tc = meta.get("total_count")
        total = sum(tc.values()) if isinstance(tc, dict) else 0
        c = count_registrations(read_products(ing["key"], raw_dir), ing, today)
        capped = bool(meta.get("capped"))
        rows.append({"key": ing["key"], "label": ing["label"], "total_count": total, "capped": capped,
                     "incomplete": bool(meta.get("incomplete")), "proposed": False, "note": CAPPED_NOTE if capped else "", **c})
    chosen = propose_selection(rows)
    for r in rows:
        r["proposed"] = r["key"] in chosen
        if not r["proposed"] and r["named_total"] < MIN_NAMED and r["key"] not in ALWAYS:
            r["note"] = (r["note"] + "; " if r["note"] else "") + TOO_FEW_NOTE
    rows.sort(key=lambda r: (not r["proposed"], -r["named_total"]))
    return rows


def write_trend_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in FIELDS})


def print_trend(rows: list[dict]) -> None:
    print(f"{'sel':3s} {'key':12s} {'label':10s} {'total':>6s} {'named':>6s} {'top6%':>6s} {'recent':>6s} {'prior':>6s} {'growth':>7s}")
    for r in rows:
        mark = "*" if r["capped"] else " "
        sel = "V" if r["proposed"] else " "
        print(f"{sel:3s} {r['key']:12s} {r['label'][:10]:10s} {r['total_count']:6d} {r['named_total']:6d} {r['top6_rate']*100:5.0f}% {r['recent_24m']:6d} {r['prior_24m']:6d} {mark}{r['growth']:6.2f}")
    print("V = 제안(이름 단 제품 수 상위 9 + 히알루론산, 15개 미만 제외). * = 250페이지 상한에 잘림(다른 성분과 직접 비교 금지)")
