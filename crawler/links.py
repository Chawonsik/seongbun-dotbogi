"""사람이 열 제품 링크 페이지와 북마클릿 설치 칸을 만든다. 자동으로 페이지를 열지 않는다."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from crawler import pick
from crawler.search import read_products

PRODUCT_URL = "https://www.hwahae.co.kr/products/{id}"


def bookmarklet_href(js_source: str) -> str:
    return "javascript:" + re.sub(r"\s+", " ", js_source.strip())


def build_candidates(raw_dir: Path, ingredients: list[dict], top_n: int) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for ing in ingredients:
        if not ing.get("selected"):
            continue
        products = read_products(ing["key"], raw_dir)
        if not products:
            print(f"[links] {ing['key']}: 검색 결과가 없습니다. 먼저 search 를 실행하세요")
            continue
        out[ing["key"]] = pick.select_candidates(products, ing, top_n=top_n)
    return out


def _item(pid: int, brand: str, name: str, extra: str = "") -> str:
    url = PRODUCT_URL.format(id=pid)
    return (f'<li><a href="{url}" target="_blank" rel="noopener">{html.escape(str(brand))} {html.escape(str(name))}</a>'
            f'{(" <small>" + html.escape(extra) + "</small>") if extra else ""}</li>')


def render_html(candidates: dict[str, list[dict]], verify: list[dict], collect_js: str, export_js: str, clear_js: str, labels: dict[str, str] | None = None) -> str:
    labels = labels or {}
    parts = ['<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>성분 수집 링크</title>',
             '<style>body{font:15px/1.5 sans-serif;max-width:860px;margin:24px auto;padding:0 16px;color:#222}'
             '.bm a{display:inline-block;padding:8px 14px;margin:4px 8px 4px 0;border:2px solid #444;border-radius:8px;text-decoration:none;color:#222;font-weight:700}'
             'h2{margin-top:32px;border-bottom:1px solid #ddd;padding-bottom:4px}li{margin:4px 0}small{color:#777}</style></head><body>',
             '<h1>성분 수집 링크</h1>',
             '<p>1. 아래 세 버튼을 <b>북마크바로 끌어다</b> 놓는다. 2. 제품 링크를 새 탭으로 열고 북마크바의 <b>성분 수집</b>을 누른다. '
             '3. 다 모으면 www.hwahae.co.kr 의 아무 페이지에서 <b>수집 내보내기</b>를 누른다. '
             '4. 파일을 확인했으면 <b>수집 비우기</b>로 브라우저 저장분을 지운다. 페이지는 자동으로 넘어가지 않는다.</p>',
             f'<p class="bm"><a href="{html.escape(bookmarklet_href(collect_js), quote=True)}">성분 수집</a>'
             f'<a href="{html.escape(bookmarklet_href(export_js), quote=True)}">수집 내보내기</a>'
             f'<a href="{html.escape(bookmarklet_href(clear_js), quote=True)}">수집 비우기</a></p>']
    total = 0
    for key, items in candidates.items():
        parts.append(f'<h2>{html.escape(labels.get(key, key))} <small>{len(items)}개</small></h2><ol>')
        for c in items:
            parts.append(_item(c["id"], c.get("brand", ""), c.get("name", ""), f"랭킹 {c.get('rank_index', 0) + 1}"))
        parts.append("</ol>")
        total += len(items)
    if verify:
        parts.append(f'<h2>검증: 지금 랜딩의 제품 <small>{len(verify)}개</small></h2><ol>')
        for v in verify:
            parts.append(_item(v["id"], v.get("brand", ""), v.get("name", "")))
        parts.append("</ol>")
    parts.append(f'<p><small>총 {total + len(verify)}개 링크</small></p></body></html>')
    return "\n".join(parts)


def write_links(raw_dir: Path, derived_dir: Path, ingredients: list[dict], top_n: int, verify_products: list[dict],
                collect_js: str, export_js: str, clear_js: str) -> tuple[Path, Path]:
    derived_dir.mkdir(parents=True, exist_ok=True)
    cands = build_candidates(raw_dir, ingredients, top_n)
    cand_ids = {c["id"] for items in cands.values() for c in items}
    kept = [v for v in verify_products if v["id"] not in cand_ids]
    if len(kept) != len(verify_products):
        print(f"[links] 검증 제품 {len(verify_products) - len(kept)}개는 이미 후보에 있어 뺐습니다")
    verify_products = kept
    cpath = derived_dir / "candidates.json"
    cpath.write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
    labels = {i["key"]: i.get("label", i["key"]) for i in ingredients}
    hpath = derived_dir / "collect-links.html"
    hpath.write_text(render_html(cands, verify_products, collect_js, export_js, clear_js, labels), encoding="utf-8")
    print(f"[links] {sum(len(v) for v in cands.values())} candidates in {len(cands)} ingredients, {len(verify_products)} verify -> {hpath}")
    return cpath, hpath
