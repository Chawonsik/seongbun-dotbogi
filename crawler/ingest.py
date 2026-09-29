"""북마클릿이 내보낸 JSON 을 raw 제품 파일로 들여온다."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from crawler.search import read_products

NO_INGREDIENTS = "전성분 없음"
NO_PRODUCT_ID = "제품 번호를 맞추지 못함"
ID_MISMATCH = "번호 불일치"


def load_export(path: Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    records = data.get("records", data)
    if isinstance(records, dict):
        return list(records.values())
    return list(records)


def resolve_product_id(rec: dict, goods_to_product: dict[int, int]) -> int | None:
    pid = rec.get("product_id")
    if pid:
        return int(pid)
    gid = rec.get("goods_id")
    if gid and int(gid) in goods_to_product:
        return goods_to_product[int(gid)]
    return None


def _goods_map(raw_dir: Path, ingredients: list[dict]) -> dict[int, int]:
    out: dict[int, int] = {}
    for ing in ingredients:
        for p in read_products(ing["key"], raw_dir):
            for g in p.get("goods") or []:
                if g.get("id"):
                    out[int(g["id"])] = int(p["id"])
    return out


def _brand_name_from_title(title: str) -> tuple[str, str]:
    return "", str(title or "").strip()


def ingest_export(path: Path, raw_dir: Path, derived_dir: Path, ingredients: list[dict]) -> dict:
    cands_path = derived_dir / "candidates.json"
    cands = json.loads(cands_path.read_text(encoding="utf-8")) if cands_path.exists() else {}
    by_id: dict[int, list[tuple[str, dict]]] = {}
    for key, items in cands.items():
        for c in items:
            by_id.setdefault(int(c["id"]), []).append((key, c))
    goods_map = _goods_map(raw_dir, ingredients)
    pdir = raw_dir / "products"
    pdir.mkdir(parents=True, exist_ok=True)
    saved = 0
    skipped: list[dict] = []
    for rec in load_export(path):
        pid = resolve_product_id(rec, goods_map)
        if not rec.get("ingredients"):
            skipped.append({"product_id": pid or rec.get("product_id"), "goods_id": rec.get("goods_id"), "url": rec.get("url"), "reason": NO_INGREDIENTS})
            continue
        if pid is None:
            skipped.append({"product_id": None, "goods_id": rec.get("goods_id"), "url": rec.get("url"), "reason": NO_PRODUCT_ID})
            continue
        gid = rec.get("goods_id")
        mapped = goods_map.get(int(gid)) if gid and rec.get("product_id") else None
        if mapped is not None and mapped != pid:
            skipped.append({"product_id": pid, "goods_id": gid, "url": rec.get("url"), "reason": ID_MISMATCH})
            continue
        targets = by_id.get(pid)
        if not targets:
            brand, name = _brand_name_from_title(rec.get("title", ""))
            targets = [("verify", {"id": pid, "name": name, "brand": brand})]
        for key, cand in targets:
            out = {"id": pid, "key": key, "candidate": cand, "ingredients": rec["ingredients"],
                   "final_url": rec.get("url"), "collected_at": rec.get("collected_at")}
            (pdir / f"{key}__{pid}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
            saved += 1
    derived_dir.mkdir(parents=True, exist_ok=True)
    with open(derived_dir / "ingest-skipped.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["product_id", "goods_id", "url", "reason"])
        w.writeheader()
        w.writerows(skipped)
    print(f"[ingest] saved={saved} skipped={len(skipped)}")
    return {"saved": saved, "skipped": len(skipped)}
