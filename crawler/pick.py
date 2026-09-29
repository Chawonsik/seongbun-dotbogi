"""검색 결과에서 상세 수집 대상을 고른다. 이름 패턴 일치, 단종 제외, 랭킹 순서 상위 N."""
from __future__ import annotations

from crawler import match


def _clean_brand(p: dict) -> str:
    return p.get("brand_name") or str(p.get("brand", "")).split(" (")[0]


def select_candidates(products: list[dict], ing: dict, top_n: int = 15) -> list[dict]:
    out = []
    for p in sorted(products, key=lambda x: x.get("_rank_index", 0)):
        if p.get("obsolete"):
            continue
        name = p.get("productName", "")
        if not match.name_matches(name, ing["name_patterns"]):
            continue
        out.append({
            "id": p["id"],
            "name": name,
            "brand": _clean_brand(p),
            "brand_name": p.get("brand_name"),
            "rank_index": p.get("_rank_index", 0),
            "update_time": p.get("updateTime"),
            "capacity": p.get("product_capacity"),
            "price": p.get("product_price"),
            "acid_in_name": match.acid_in_name(name, ing.get("acid_group", {})),
        })
        if len(out) >= top_n:
            break
    return out
