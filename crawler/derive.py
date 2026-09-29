"""raw 제품 파일에서 랜딩용 파생값만 뽑아 landing/data.json 을 만든다. 전성분 원문은 싣지 않는다."""
from __future__ import annotations

import csv
import json
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

from crawler import match

SOURCE_NOTE = "화해(hwahae.co.kr) 등록 전성분 표기 순서 기준 파생 지표. 원문 미수록. 함량 수치는 추정하지 않음. 1% 경계는 추정."
VERIFY_KEY = "verify"
# 매칭 제품이 이보다 적으면 공통 성분이 한 제품의 전성분과 거의 같아지므로 공개하지 않는다.
MIN_COMMON_PRODUCTS = 5


def price_per_ml(price, capacity: str | None) -> int | None:
    if not price or not capacity:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*(ml|mL|ML|g|G)\b", str(capacity))
    if not m:
        return None
    vol = float(m.group(1))
    if vol <= 0:
        return None
    return int(round(float(price) / vol))


def _first_name(korean: str | None) -> str:
    return match.first_name(korean)


def _to_date(ts) -> str | None:
    if not ts:
        return None
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).date().isoformat()


def _names(rec: dict) -> list[str]:
    return [_first_name(i.get("korean")) for i in rec["ingredients"]]


def derive_product(rec: dict, ing: dict, all_cfg: list[dict], markers: list[str]) -> dict | None:
    names = _names(rec)
    pos = match.find_position(names, ing["inci_patterns"])
    if pos is None:
        return None
    total = len(names)
    boundary = match.find_boundary(names, markers)
    c = rec["candidate"]
    return {
        "id": rec["id"],
        "brand": c.get("brand"),
        "name": c.get("name"),
        "chip": ing["key"],
        "total": total,
        "pos": pos,
        "boundary": boundary,
        "rel": round(match.relative_position(pos, total), 4),
        "families": match.find_families(names, all_cfg, boundary),
        "price_per_ml": price_per_ml(c.get("price"), c.get("capacity")),
        "registered": _to_date(c.get("update_time")),
        "acid_in_name": c.get("acid_in_name") or [],
        "collected_at": str(rec.get("collected_at") or "")[:10],
    }


def common_ingredients(product_recs: list[dict]) -> list[str]:
    """전부에 든 성분. 화해 성분 번호(id)로 교집합을 구하고, 표시 이름은 가장 긴 korean 첫 이름."""
    if len(product_recs) < MIN_COMMON_PRODUCTS:
        return []
    id_sets = []
    names: dict = {}
    for r in product_recs:
        ids = set()
        for i in r["ingredients"]:
            iid = i.get("id")
            if iid is None:
                continue
            ids.add(iid)
            nm = _first_name(i.get("korean"))
            if len(nm) > len(names.get(iid, "")):
                names[iid] = nm
        id_sets.append(ids)
    common = set.intersection(*id_sets)
    return sorted(names[i] for i in common if i in names)


def family_match_table(raws: list[dict], ingredients: list[dict]) -> list[dict]:
    """계열(후보 성분)마다 실제로 걸린 성분의 번호와 이름, 걸린 제품 수. 계열을 번호로 고정할 때 본다."""
    counts: dict[tuple, dict] = {}
    for cfg in ingredients:
        for r in raws:
            names = _names(r)
            pos = match.find_position(names, cfg["inci_patterns"])
            if pos is None:
                continue
            hit = r["ingredients"][pos - 1]
            k = (cfg["label"], hit.get("id"))
            if k not in counts:
                counts[k] = {"family": cfg["label"], "ingredient_id": hit.get("id"), "ingredient": names[pos - 1], "products": 0}
            counts[k]["products"] += 1
    return sorted(counts.values(), key=lambda x: (x["family"], -x["products"], str(x["ingredient_id"])))


def load_raw(raw_dir: Path) -> list[dict]:
    pdir = raw_dir / "products"
    out = []
    for f in sorted(pdir.glob("*.json")) if pdir.exists() else []:
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"[derive] skip (bad json) {f.name}")
            continue
        if "ingredients" not in rec or "candidate" not in rec or "key" not in rec:
            print(f"[derive] skip (missing keys) {f.name}")
            continue
        out.append(rec)
    return out


def load_top6_rates(trend_csv: Path) -> dict[str, float]:
    if not trend_csv.exists():
        return {}
    with open(trend_csv, encoding="utf-8", newline="") as f:
        return {r["key"]: float(r["top6_rate"] or 0) for r in csv.DictReader(f)}


def build_data(raw_dir: Path, ingredients: list[dict], markers: list[str], version: str, top6_rates: dict[str, float] | None = None) -> tuple[dict, list[dict]]:
    raws = [r for r in load_raw(raw_dir) if r["key"] != VERIFY_KEY]
    top6_rates = top6_rates or {}
    selected = [i for i in ingredients if i.get("selected")]
    out_ings, out_products, unmatched = [], [], []
    for ing in selected:
        recs = [r for r in raws if r["key"] == ing["key"]]
        derived, matched_recs = [], []
        for r in recs:
            p = derive_product(r, ing, ingredients, markers)
            if p is None:
                unmatched.append({"key": ing["key"], "id": r["id"], "name": r["candidate"].get("name"), "brand": r["candidate"].get("brand")})
                continue
            derived.append(p)
            matched_recs.append(r)
        derived.sort(key=lambda p: p["rel"])
        rels = [p["rel"] for p in derived]
        out_ings.append({
            "key": ing["key"], "label": ing["label"], "category": ing.get("category", ""),
            "n_products": len(derived), "common": common_ingredients(matched_recs),
            "note": f"{version} 실측. 검색 랭킹 상위 {len(recs)}개 중 이름 성분이 보인 {len(derived)}개.",
            "median_rel": round(statistics.median(rels), 4) if rels else None,
            "back_half": sum(1 for p in derived if p["pos"] / p["total"] > 0.5),
            "low_zone": sum(1 for p in derived if p["boundary"] and p["pos"] >= p["boundary"]),
            "top6_rate": top6_rates.get(ing["key"]),
        })
        out_products.extend(derived)
    data = {
        "version": version,
        "source": SOURCE_NOTE,
        "family_dict": [{"name": i["label"], "keys": list(i["inci_patterns"])} for i in ingredients],
        "one_percent_markers": list(markers),
        "ingredients": out_ings,
        "products": out_products,
    }
    return data, unmatched


def verify_table(raws: list[dict], old_data: dict, markers: list[str], pdrn_patterns: list[str]) -> list[dict]:
    """key == verify 레코드를 지금 랜딩 data.json 의 값과 비교한다."""
    old = {int(p["id"]): p for p in old_data.get("products", [])}
    rows = []
    for r in raws:
        if r["key"] != VERIFY_KEY:
            continue
        names = _names(r)
        new_pos = match.find_position(names, pdrn_patterns)
        new_total = len(names)
        new_boundary = match.find_boundary(names, markers)
        o = old.get(int(r["id"]), {})
        row = {"id": r["id"], "name": o.get("name") or r["candidate"].get("name"),
               "old_pos": o.get("pos"), "new_pos": new_pos, "old_total": o.get("total"), "new_total": new_total,
               "old_boundary": o.get("boundary"), "new_boundary": new_boundary}
        row["same"] = bool(o) and o.get("pos") == new_pos and o.get("total") == new_total and o.get("boundary") == new_boundary
        rows.append(row)
    return rows


def write_outputs(data: dict, unmatched: list[dict], family_rows: list[dict], verify_rows: list[dict], landing_dir: Path, derived_dir: Path, write_landing: bool = True) -> None:
    derived_dir.mkdir(parents=True, exist_ok=True)
    if write_landing:
        landing_dir.mkdir(parents=True, exist_ok=True)
        (landing_dir / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    def _csv(name: str, fields: list[str], rows: list[dict]) -> None:
        with open(derived_dir / name, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    _csv("unmatched.csv", ["key", "id", "name", "brand"], unmatched)
    _csv("family_matches.csv", ["family", "ingredient_id", "ingredient", "products"], family_rows)
    _csv("verify.csv", ["id", "name", "old_pos", "new_pos", "old_total", "new_total", "old_boundary", "new_boundary", "same"], verify_rows)
    print(f"[derive] ingredients={len(data['ingredients'])} products={len(data['products'])} unmatched={len(unmatched)} family_rows={len(family_rows)} verify={len(verify_rows)}")
