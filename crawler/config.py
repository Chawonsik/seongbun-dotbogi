"""설정 파일 로드와 문자열 정규화."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
RAW_DIR = ROOT / "data" / "raw"
DERIVED_DIR = ROOT / "data" / "derived"
LANDING_DIR = ROOT / "landing"


def normalize(s: str) -> str:
    """소문자로 바꾸고 공백을 모두 없앤다. 패턴 비교 전에 양쪽에 적용한다."""
    return "".join(str(s).lower().split())


def load_ingredients(path: Path | None = None) -> list[dict]:
    p = path or CONFIG_DIR / "ingredients.json"
    with open(p, encoding="utf-8") as f:
        items = json.load(f)
    if not isinstance(items, list) or not items:
        raise ValueError(f"ingredients.json 이 비어 있거나 목록이 아닙니다: {p}")
    return items


def load_markers(path: Path | None = None) -> list[str]:
    p = path or CONFIG_DIR / "one-percent-markers.json"
    with open(p, encoding="utf-8") as f:
        markers = json.load(f)
    if not isinstance(markers, list) or not markers:
        raise ValueError(f"one-percent-markers.json 이 비어 있습니다: {p}")
    return markers
