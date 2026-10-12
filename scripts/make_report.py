"""Build the public report page and its charts from docs/report/data.json.

Usage: python3 scripts/make_report.py

Writes landing/report.html (charts inlined) and docs/report/img/*.svg (the same
charts as standalone files for the README). Numbers live only in data.json, so
refreshing the report means editing that file and running this script again.
"""
from __future__ import annotations

import json
import pathlib
import string
from html import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "docs" / "report" / "data.json"
TEMPLATE_PATH = ROOT / "scripts" / "report_template.html"
PAGE_PATH = ROOT / "landing" / "report.html"
IMG_DIR = ROOT / "docs" / "report" / "img"

W = 360  # chart width in viewBox units; close to a phone's width so labels are not shrunk there
PAD = 12
FONT = 13

Series = tuple[str, str, list[float], list[str]]

# Standalone SVG files cannot read the page's CSS variables, so they carry their
# own colors and background. GitHub's theme can differ from the OS theme, so they
# use the light palette on every theme instead of a media query.
STANDALONE_STYLE = """<style>
.vz text{font-family:"Noto Sans KR","Apple SD Gothic Neo",sans-serif}
.vz-t{fill:#3B2A25}.vz-s{fill:#7D6761}.vz-g{stroke:#E6D2C6}
.vz-a{fill:#2a78d6}.vz-b{fill:#eb6834}.vz-la{stroke:#2a78d6}.vz-lb{stroke:#eb6834}.vz-ring{stroke:#FFF8F3}
</style><rect width="100%" height="100%" rx="10" fill="#FFF8F3"/>"""


def pct(numerator: float, denominator: float, digits: int = 2) -> str:
    if not denominator:
        return "-"
    return f"{numerator / denominator * 100:.{digits}f}%"


def share(numerator: float, denominator: float) -> str:
    """Percent for a share of a whole: whole numbers, one decimal under 1%."""
    if not denominator:
        return "-"
    value = numerator / denominator * 100
    return f"{value:.1f}%" if 0 < value < 1 else f"{value:.0f}%"


def num(value: float) -> str:
    return f"{value:,.0f}"


def rate(numerator: float, denominator: float) -> float:
    return numerator / denominator * 100 if denominator else 0.0


def _svg(height: float, title: str, desc: str, body: str) -> str:
    """desc spells out the values, since role="img" hides the marks from screen readers."""
    return (
        f'<svg class="vz" viewBox="0 0 {W} {height:.0f}" role="img" xmlns="http://www.w3.org/2000/svg">'
        f"<title>{escape(title)}</title><desc>{escape(desc)}</desc>{body}</svg>"
    )


def _describe(categories: list[str], series: list[Series]) -> str:
    return " ".join(
        f"{name}: " + ", ".join(f"{c} {label}" for c, label in zip(categories, labels)) + "."
        for name, _, _, labels in series
    )


def _text(x: float, y: float, label: str, cls: str = "vz-t", anchor: str = "middle", size: int = FONT) -> str:
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}">{escape(label)}</text>'


def _bar_up(x: float, base: float, width: float, height: float, cls: str, tip: str) -> str:
    """A bar anchored to the baseline with only its top end rounded."""
    r = min(4.0, height, width / 2)
    top = base - height
    d = (
        f"M{x:.1f},{base:.1f} V{top + r:.1f} Q{x:.1f},{top:.1f} {x + r:.1f},{top:.1f} "
        f"H{x + width - r:.1f} Q{x + width:.1f},{top:.1f} {x + width:.1f},{top + r:.1f} V{base:.1f} Z"
    )
    return f'<path class="{cls}" data-h="{height:.2f}" d="{d}"><title>{escape(tip)}</title></path>'


def _bar_right(x: float, y: float, width: float, height: float, cls: str, tip: str) -> str:
    return (
        f'<rect class="{cls}" data-w="{width:.2f}" x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" '
        f'height="{height:.1f}" rx="4"><title>{escape(tip)}</title></rect>'
    )


def grouped_bars(categories: list[str], series: list[Series], title: str, height: float = 250) -> str:
    """Vertical bars, one group per category. series: (name, css class, values, labels).

    With more than four groups only the last group is labeled, because every
    label would not fit; the rest stay readable through hover titles and <desc>.
    """
    top, base = 38.0, height - 30
    peak = max(max(values) for _, _, values, _ in series) or 1
    band = (W - 2 * PAD) / len(categories)
    gap = 4.0
    bar_w = min(38.0, (band - 10) / len(series) - gap)
    group_w = len(series) * bar_w + (len(series) - 1) * gap
    label_all = len(categories) <= 4
    parts = [f'<line class="vz-g" x1="{PAD}" x2="{W - PAD}" y1="{base}" y2="{base}"/>']
    for i, category in enumerate(categories):
        left = PAD + band * i + (band - group_w) / 2
        previous_y = None
        for j, (name, cls, values, labels) in enumerate(series):
            x = left + j * (bar_w + gap)
            bar_h = values[i] / peak * (base - top)
            if bar_h > 0:
                parts.append(_bar_up(x, base, bar_w, bar_h, cls, f"{category} {name}: {labels[i]}"))
            if label_all or i == len(categories) - 1:
                y = base - bar_h - 6
                # bars of nearly equal height would put their labels side by side and touching
                if previous_y is not None and abs(y - previous_y) < 13:
                    y = previous_y - 13
                parts.append(_text(x + bar_w / 2, y, labels[i], size=12))
                previous_y = y
        parts.append(_text(PAD + band * (i + 0.5), base + 19, category, "vz-s"))
    return _svg(height, title, _describe(categories, series), "".join(parts))


def line_chart(
    categories: list[str],
    series: list[Series],
    title: str,
    callouts: dict[tuple[int, int], tuple[str, int]],
    height: float = 250,
) -> str:
    """Lines over time. callouts maps (series index, point index) to (label, dy).

    dy is the label offset from the point: negative sits above it, positive below.
    """
    top, base, left, right = 30.0, height - 30, PAD + 8, W - PAD - 8
    peak = max(max(values) for _, _, values, _ in series) or 1
    step = (right - left) / (len(categories) - 1)

    def point(i: int, value: float) -> tuple[float, float]:
        return left + step * i, base - value / peak * (base - top)

    parts = [f'<line class="vz-g" x1="{PAD}" x2="{W - PAD}" y1="{base}" y2="{base}"/>']
    parts += [_text(left + step * i, base + 19, c, "vz-s") for i, c in enumerate(categories)]
    for s, (name, cls, values, labels) in enumerate(series):
        line_cls = "vz-la" if cls == "vz-a" else "vz-lb"
        path = " ".join(f"{'M' if i == 0 else 'L'}{point(i, v)[0]:.1f},{point(i, v)[1]:.1f}" for i, v in enumerate(values))
        parts.append(f'<path class="{line_cls}" d="{path}" fill="none" stroke-width="2" stroke-linejoin="round"/>')
        for i, value in enumerate(values):
            x, y = point(i, value)
            parts.append(
                f'<circle class="{cls} vz-ring" cx="{x:.1f}" cy="{y:.1f}" r="4.5" stroke-width="2">'
                f"<title>{escape(f'{categories[i]} {name}: {labels[i]}')}</title></circle>"
            )
            if (s, i) in callouts:
                label, dy = callouts[(s, i)]
                parts.append(_text(x, y + dy, label, size=12))
    return _svg(height, title, _describe(categories, series), "".join(parts))


def share_bars(rows: list[tuple[str, list[tuple[str, str, float]]]], title: str) -> str:
    """One 100% bar per row. rows: (row label, [(part name, css class, value)])."""
    row_h, bar_h, gap = 78.0, 22.0, 2.0
    inner = W - 2 * PAD
    parts, described = [], []
    for r, (label, segments) in enumerate(rows):
        y = r * row_h
        total = sum(value for _, _, value in segments) or 1
        parts.append(_text(PAD, y + 16, label, anchor="start"))
        x = float(PAD)
        usable = inner - gap * (len(segments) - 1)
        for k, (name, cls, value) in enumerate(segments):
            width = value / total * usable
            tip = f"{label} {name}: {share(value, total)}"
            parts.append(_bar_right(x, y + 26, width, bar_h, cls, tip))
            edge, anchor = (PAD, "start") if k == 0 else (W - PAD, "end")
            # near an even split a whole-number label would read 50% and 50%
            label_pct = pct(value, total, 1) if abs(value / total - 0.5) < 0.05 else share(value, total)
            parts.append(_text(edge, y + 26 + bar_h + 17, f"{name} {label_pct}", "vz-s", anchor, 12))
            described.append(f"{label} {name} {label_pct}.")
            x += width + gap
    return _svg(len(rows) * row_h - 6, title, " ".join(described), "".join(parts))


def step_bars(steps: list[tuple[str, float]], title: str, cls: str = "vz-b") -> str:
    """Horizontal bars for steps of one flow. The first step is the 100% base."""
    row_h, bar_h = 50.0, 14.0
    inner = W - 2 * PAD
    base = steps[0][1] or 1
    parts = []
    for r, (label, value) in enumerate(steps):
        y = r * row_h
        parts.append(_text(PAD, y + 15, label, anchor="start"))
        parts.append(_text(W - PAD, y + 15, f"{num(value)}대 · {share(value, base)}", "vz-s", "end", 12))
        if value > 0:
            parts.append(_bar_right(PAD, y + 23, value / base * inner, bar_h, cls, f"{label}: {num(value)}대"))
        else:
            parts.append(f'<line class="vz-g" x1="{PAD}" x2="{PAD}" y1="{y + 23}" y2="{y + 23 + bar_h}" stroke-width="2"/>')
    desc = " ".join(f"{label} {num(value)}대 {share(value, base)}." for label, value in steps)
    return _svg(len(steps) * row_h - 8, title, desc, "".join(parts))


def charts(data: dict) -> dict[str, str]:
    r1, r2, landing = data["round1"], data["round2"], data["landing"]
    ing, tex, a, b = r1["ingredient"], r1["texture"], r2["a"], r2["b"]
    peak_day = max(range(len(r1["days"])), key=lambda i: tex["daily_impressions"][i])
    first_zero = next(i for i, v in enumerate(ing["daily_impressions"]) if v == 0)
    ing_peak = max(range(len(r1["days"])), key=lambda i: ing["daily_impressions"][i])
    for key, total in (("a", a), ("b", b)):
        summed = [sum(d[key][0] for d in r2["daily"]), sum(d[key][1] for d in r2["daily"])]
        if summed != [total["clicks"], total["impressions"]]:
            raise ValueError(f"round2.daily {key} sums to {summed}, but the totals say {[total['clicks'], total['impressions']]}")
    daily = r2["daily"] + [{"day": "누적", "a": [a["clicks"], a["impressions"]], "b": [b["clicks"], b["impressions"]]}]
    return {
        "r1-daily-impressions": line_chart(
            r1["days"],
            [
                (ing["name"], "vz-a", ing["daily_impressions"], [num(v) for v in ing["daily_impressions"]]),
                (tex["name"], "vz-b", tex["daily_impressions"], [num(v) for v in tex["daily_impressions"]]),
            ],
            "1차 광고의 일자별 노출 수",
            {
                # the smaller series peaks under the other line, so its label goes below the point
                (0, ing_peak): (num(ing["daily_impressions"][ing_peak]), 20),
                (0, first_zero): ("0", -11),
                (1, peak_day): (num(tex["daily_impressions"][peak_day]), -11),
            },
        ),
        "impression-share": share_bars(
            [
                ("1차: 광고 세트 하나에 광고 둘", [(ing["name"], "vz-a", ing["impressions"]), (tex["name"], "vz-b", tex["impressions"])]),
                ("2차: 광고 세트 둘에 예산 고정", [(a["name"], "vz-a", a["impressions"]), (b["name"], "vz-b", b["impressions"])]),
            ],
            "광고별 노출 비중. 1차와 2차",
        ),
        "r2-ctr": grouped_bars(
            [d["day"] for d in daily],
            [
                (a["name"], "vz-a", [rate(*d["a"]) for d in daily], [pct(*d["a"]) for d in daily]),
                (b["name"], "vz-b", [rate(*d["b"]) for d in daily], [pct(*d["b"]) for d in daily]),
            ],
            "2차 광고의 일자별 링크 클릭률과 누적 링크 클릭률",
        ),
        "landing-steps": step_bars(
            [(s["label"], s["devices"]) for s in landing["sections"]["steps"]],
            "랜딩에 도착한 기기가 어디까지 갔는지",
        ),
    }


def standalone(svg: str) -> str:
    head, rest = svg.split(">", 1)
    return f"{head}>{STANDALONE_STYLE}{rest}"


def render(data: dict) -> str:
    r1, r2, landing = data["round1"], data["round2"], data["landing"]
    ing, tex, a, b = r1["ingredient"], r1["texture"], r2["a"], r2["b"]
    r1_total = ing["impressions"] + tex["impressions"]
    r2_total = a["impressions"] + b["impressions"]
    steps = landing["sections"]["steps"]
    values = {f"chart_{name.replace('-', '_')}": svg for name, svg in charts(data).items()}
    same = r1["same_days"]
    text = dict(
        queried_at=data["queried_at"],
        result_title=data["headline"]["result_title"],
        result_body=data["headline"]["result_body"],
        solution_title=data["headline"]["solution_title"],
        solution_body=data["headline"]["solution_body"],
        pdrn_products=num(data["background"]["hwahae_pdrn_products"]),
        r1_share_ing=share(ing["impressions"], r1_total),
        r1_share_tex=share(tex["impressions"], r1_total),
        r1_ctr_ing=pct(ing["clicks"], ing["impressions"]),
        r1_ctr_tex=pct(tex["clicks"], tex["impressions"]),
        r1_imp_ing=num(ing["impressions"]),
        r1_imp_tex=num(tex["impressions"]),
        r1_same_ing=pct(*same["ingredient"]),
        r1_same_tex=pct(*same["texture"]),
        r2_ctr_a=pct(a["clicks"], a["impressions"]),
        r2_ctr_b=pct(b["clicks"], b["impressions"]),
        r2_frac_a=f"{a['clicks']}/{num(a['impressions'])}",
        r2_frac_b=f"{b['clicks']}/{num(b['impressions'])}",
        r2_share_a=pct(a["impressions"], r2_total, 1),
        r2_share_b=pct(b["impressions"], r2_total, 1),
        copy_a=a["copy"],
        copy_b=b["copy"],
        l1_interest=f"{landing['round1']['interest']} / {num(landing['round1']['arrived'])}",
        l2_interest=f"{landing['round2']['interest']} / {num(landing['round2']['arrived'])}",
        seen_share=share(steps[1]["devices"], steps[0]["devices"]),
        info_share=share(steps[2]["devices"], steps[0]["devices"]),
        section_base=num(steps[0]["devices"]),
        section_period=landing["sections"]["period"],
    )
    # the charts are already-escaped SVG; everything else is plain text from data.json
    values.update({key: escape(value) for key, value in text.items()})
    return string.Template(TEMPLATE_PATH.read_text(encoding="utf-8")).substitute(values)


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    PAGE_PATH.write_text(render(data), encoding="utf-8")
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    for name, svg in charts(data).items():
        (IMG_DIR / f"{name}.svg").write_text(standalone(svg), encoding="utf-8")


if __name__ == "__main__":
    main()
