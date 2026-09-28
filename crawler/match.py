"""이름 필터, 이름 성분 위치, 1% 경계, 계열 매칭. 모두 순수 함수."""
from __future__ import annotations

import re

from crawler.config import normalize

_LATIN = re.compile(r"^[a-z0-9 .\-]+$")


def _spaced(s: str) -> str:
    """소문자로 바꾸고 연속 공백을 하나로. 라틴 패턴의 단어 경계 판정용(공백을 남긴다)."""
    return " ".join(str(s).lower().split())


def _hit(stripped: str, spaced: str, pattern: str) -> bool:
    p_stripped = normalize(pattern)
    if not p_stripped:
        return False
    p_spaced = _spaced(pattern)
    if _LATIN.match(p_spaced):
        # 라틴 패턴은 앞뒤에 다른 라틴 글자가 없어야 한다. "pha" 가 "alpha" 에 걸리지 않게.
        # 공백을 지운 문자열에서는 "aha bha" 가 "ahabha" 가 되어 경계가 사라지므로 공백을 남긴 문자열에서 본다
        return re.search(r"(?<![a-z])" + re.escape(p_spaced) + r"(?![a-z])", spaced) is not None
    return p_stripped in stripped


def _contains_any(text: str, patterns: list[str]) -> bool:
    stripped = normalize(text)
    spaced = _spaced(text)
    return any(_hit(stripped, spaced, p) for p in patterns)


def first_name(korean: str | None) -> str:
    """화해 korean 필드 "이름, 별칭, 별칭" 에서 첫 이름. 구분자는 쉼표+공백. "1,2-헥산다이올" 처럼 이름 안의 쉼표는 보존."""
    if not korean:
        return ""
    return str(korean).split(", ")[0].strip()


def name_matches(product_name: str, patterns: list[str]) -> bool:
    return _contains_any(product_name, patterns)


def find_position(ingredients: list[str], patterns: list[str]) -> int | None:
    """패턴 중 하나를 포함하는 첫 성분의 1부터 시작하는 순번. 없으면 None."""
    for i, name in enumerate(ingredients, start=1):
        if _contains_any(name, patterns):
            return i
    return None


def find_boundary(ingredients: list[str], markers: list[str]) -> int | None:
    """1% 이하로 흔히 쓰이는 성분이 처음 나오는 순번. 없으면 None."""
    return find_position(ingredients, markers)


def find_families(ingredients: list[str], all_ingredients_cfg: list[dict], boundary: int | None) -> list[dict]:
    """설정의 모든 후보 성분 계열이 전성분 어디에 있는지. top 은 경계보다 앞이면 True."""
    out = []
    for cfg in all_ingredients_cfg:
        pos = find_position(ingredients, cfg["inci_patterns"])
        if pos is None:
            continue
        top = True if boundary is None else pos < boundary
        out.append({"name": cfg["label"], "pos": pos, "top": top})
    return out


def acid_in_name(product_name: str, acid_group: dict[str, list[str]]) -> list[str]:
    """제품명에 적힌 각질 산 종류(아하, 바하, 파하, 라하)를 설정 순서대로."""
    return [acid for acid, pats in acid_group.items() if _contains_any(product_name, pats)]


def relative_position(pos: int, total: int) -> float:
    """(pos - 1) / (total - 1). 기존 랜딩의 pct() 와 같다. total 이 1 이하이면 0."""
    if total <= 1:
        return 0.0
    return (pos - 1) / (total - 1)
