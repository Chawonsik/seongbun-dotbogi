"""Build the public report page and its charts from docs/report/data.json.

Usage: python3 scripts/make_report.py

Writes landing/report.html (charts inlined) and docs/report/img/*.svg (the same
charts as standalone files for the README). Numbers live only in data.json, so
refreshing the report means editing that file and running this script again.
"""
from __future__ import annotations

import datetime
import json
import math
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
BAR_LABEL = 12

Series = tuple[str, str, list[float], list[str]]

# Standalone SVG files cannot read the page's CSS variables, so they carry their
# own colors and background. GitHub's theme can differ from the OS theme, so they
# use the light palette on every theme instead of a media query.
STANDALONE_STYLE = """<style>
.vz text{font-family:"Noto Sans KR","Apple SD Gothic Neo",sans-serif}
.vz-t{fill:#3B2A25}.vz-s{fill:#7D6761}.vz-g{stroke:#E6D2C6}
.vz-a{fill:#2a78d6}.vz-b{fill:#eb6834}.vz-la{stroke:#2a78d6}.vz-lb{stroke:#eb6834}.vz-ring{stroke:#FFF8F3}
.vz-off{fill:#F3EAE3}
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


def two_proportion_z(clicks_a: int, shown_a: int, clicks_b: int, shown_b: int) -> tuple[float, float]:
    """Two-sided two-proportion z-test with a pooled rate. Returns (z, p); (0, 1) when it cannot be computed."""
    if not shown_a or not shown_b:
        return 0.0, 1.0
    pooled = (clicks_a + clicks_b) / (shown_a + shown_b)
    se = math.sqrt(pooled * (1 - pooled) * (1 / shown_a + 1 / shown_b))
    if not se:
        return 0.0, 1.0
    z = (clicks_a / shown_a - clicks_b / shown_b) / se
    return z, math.erfc(abs(z) / math.sqrt(2))


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
        group = []
        for j, (name, cls, values, labels) in enumerate(series):
            x = left + j * (bar_w + gap)
            bar_h = values[i] / peak * (base - top)
            if bar_h > 0:
                parts.append(_bar_up(x, base, bar_w, bar_h, cls, f"{category} {name}: {labels[i]}"))
            group.append((x, base - bar_h, labels[i]))
        if label_all or i == len(categories) - 1:
            for x, y, label in _place_bar_labels(group, bar_w):
                parts.append(_text(x, y, label, size=BAR_LABEL))
        parts.append(_text(PAD + band * (i + 0.5), base + 19, category, "vz-s"))
    return _svg(height, title, _describe(categories, series), "".join(parts))


def _place_bar_labels(group: list[tuple[float, float, str]], bar_w: float) -> list[tuple[float, float, str]]:
    """Label positions for one group of bars. group: (bar left, bar top, label).

    A label wider than its bar spills over the neighbouring bar, so it sits
    above every bar it spans. Two labels that end up on one line are split,
    and the label of the taller bar goes on top.
    """
    placed = []
    for x, _, label in group:
        center, half = x + bar_w / 2, len(label) * BAR_LABEL * 0.3
        spanned = [t for bx, t, _ in group if center - half < bx + bar_w and center + half > bx]
        placed.append([center, min(spanned) - 6, label])
    for (_, top_a, _), (_, top_b, _), a, b in zip(group, group[1:], placed, placed[1:]):
        if abs(a[1] - b[1]) < BAR_LABEL + 1:
            upper, lower = (a, b) if top_a < top_b else (b, a)
            upper[1] = lower[1] - (BAR_LABEL + 1)
    return [(x, y, label) for x, y, label in placed]


def off_days(days: list[str], year: int, holidays: dict[str, str]) -> set[int]:
    """Indices of days that are a weekend or a listed holiday. days are "M/D" strings."""
    off = set()
    for i, day in enumerate(days):
        month, date = (int(part) for part in day.split("/"))
        if day in holidays or datetime.date(year, month, date).weekday() >= 5:
            off.add(i)
    return off


def day_labels(days: list[str], year: int) -> tuple[list[str], list[str]]:
    """Axis labels for "M/D" days: the full date where the month first appears, the day alone after
    that, plus a row of weekday letters."""
    names = "월화수목금토일"
    labels, weekdays, last_month = [], [], None
    for day in days:
        month, date = (int(part) for part in day.split("/"))
        labels.append(day if month != last_month else str(date))
        weekdays.append(names[datetime.date(year, month, date).weekday()])
        last_month = month
    return labels, weekdays


def nice_ticks(peak: float) -> list[float]:
    """Tick values from 0 to just above the peak, in 1, 2, 2.5 or 5 steps, about four of them."""
    if peak <= 0:
        return [0.0, 1.0]
    raw = peak / 3
    magnitude = 10 ** math.floor(math.log10(raw))
    step = min((m * magnitude for m in (1, 2, 2.5, 5, 10)), key=lambda c: abs(c - raw))
    count = math.ceil(peak / step - 1e-9)
    return [step * i for i in range(count + 1)]


def line_chart(
    categories: list[str],
    series: list[Series],
    title: str,
    callouts: dict[tuple[int, int], tuple],
    height: float = 250,
    gutter: float = 0,
    tick_format=None,
    off: set[int] = frozenset(),
    x_labels: list[str] | None = None,
    x_sub: list[str] | None = None,
) -> str:
    """Lines over time. callouts maps (series index, point index) to (label, dy) or (label, dy, dx).

    dy is the label offset from the point: negative sits above it, positive below.
    dx > 0 puts the label to the right of the point, starting there; gutter keeps room for it.
    tick_format turns a y value into its axis label; off marks the x positions shaded as rest days.
    x_labels replaces the category text on the axis and x_sub adds a second row under it.
    """
    tick_format = tick_format or (lambda v: num(int(v)))
    x_labels = x_labels or categories
    top, base, left, right = 30.0, height - (44 if x_sub else 30), PAD + 44, W - PAD - 8 - gutter
    peak = max(max(values) for _, _, values, _ in series) or 1
    ticks = nice_ticks(peak)
    scale_top = ticks[-1]
    step = (right - left) / (len(categories) - 1)

    def point(i: int, value: float) -> tuple[float, float]:
        return left + step * i, base - value / scale_top * (base - top)

    parts = []
    for i in sorted(off):
        x0 = max(left + step * i - step / 2, left - 10)
        x1 = min(left + step * i + step / 2, right + 10)
        parts.append(f'<rect class="vz-off" x="{x0:.1f}" y="{top - 8:.1f}" width="{x1 - x0:.1f}" height="{base - top + 8:.1f}"/>')
    for value in ticks:
        y = point(0, value)[1]
        parts.append(f'<line class="vz-g" x1="{left - 6}" x2="{W - PAD}" y1="{y:.1f}" y2="{y:.1f}"/>')
        parts.append(_text(left - 10, y + 4, tick_format(value), "vz-s", anchor="end", size=11))
    parts += [_text(left + step * i, base + 19, c, "vz-s") for i, c in enumerate(x_labels)]
    if x_sub:
        parts += [_text(left + step * i, base + 33, c, "vz-s", size=11) for i, c in enumerate(x_sub)]
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
                label, dy, *rest = callouts[(s, i)]
                dx = rest[0] if rest else 0
                parts.append(_text(x + dx, y + dy, label, anchor="start" if dx > 0 else "middle", size=12))
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
            # near an even split a whole-number label would read 50% and 50%
            label_pct = pct(value, total, 1) if abs(value / total - 0.5) < 0.05 else share(value, total)
            parts.append(_bar_right(x, y + 26, width, bar_h, cls, f"{label} {name}: {label_pct}"))
            edge, anchor = (PAD, "start") if k == 0 else (W - PAD, "end")
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
    year = int(data["queried_at"][:4])
    holidays = data.get("calendar", {}).get("holidays", {})
    peak_day = max(range(len(r1["days"])), key=lambda i: tex["daily_impressions"][i])
    first_zero = next(i for i, v in enumerate(ing["daily_impressions"]) if v == 0)
    ing_peak = max(range(len(r1["days"])), key=lambda i: ing["daily_impressions"][i])
    for key, total in (("a", a), ("b", b)):
        summed = [sum(d[key][0] for d in r2["daily"]), sum(d[key][1] for d in r2["daily"])]
        if summed != [total["clicks"], total["impressions"]]:
            raise ValueError(f"round2.daily {key} sums to {summed}, but the totals say {[total['clicks'], total['impressions']]}")
    days, last = r2["daily"], len(r2["daily"]) - 1
    r1_labels, r1_weekdays = day_labels(r1["days"], year)
    r2_labels, r2_weekdays = day_labels([d["day"] for d in days], year)
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
            off=off_days(r1["days"], year, holidays),
            x_labels=r1_labels,
            x_sub=r1_weekdays,
            height=264,
        ),
        "impression-share": share_bars(
            [
                ("1차: 광고 세트 하나에 광고 둘", [(ing["name"], "vz-a", ing["impressions"]), (tex["name"], "vz-b", tex["impressions"])]),
                ("2차: 광고 세트 둘에 예산 고정", [(a["name"], "vz-a", a["impressions"]), (b["name"], "vz-b", b["impressions"])]),
            ],
            "광고별 노출 비중. 1차와 2차",
        ),
        "r2-ctr": line_chart(
            [d["day"] for d in days],
            [
                (a["name"], "vz-a", [rate(*d["a"]) for d in days], [pct(*d["a"]) for d in days]),
                (b["name"], "vz-b", [rate(*d["b"]) for d in days], [pct(*d["b"]) for d in days]),
            ],
            "2차 광고의 일자별 링크 클릭률",
            # only the latest day is labeled, to the right of the point so no line crosses it;
            # the higher one is nudged up and the lower one down so the two never touch
            {
                (0, last): (pct(*days[-1]["a"]), -2 if rate(*days[-1]["a"]) >= rate(*days[-1]["b"]) else 12, 9),
                (1, last): (pct(*days[-1]["b"]), -2 if rate(*days[-1]["b"]) > rate(*days[-1]["a"]) else 12, 9),
            },
            gutter=36,
            tick_format=lambda v: f"{v:g}%",
            off=off_days([d["day"] for d in days], year, holidays),
            x_labels=r2_labels,
            x_sub=r2_weekdays,
            height=264,
        ),
        "landing-steps": step_bars(
            [(s["label"], s["devices"]) for s in landing["sections"]["steps"]],
            "랜딩에 도착한 기기가 어디까지 갔는지",
        ),
    }


def standalone(svg: str) -> str:
    head, rest = svg.split(">", 1)
    return f"{head}>{STANDALONE_STYLE}{rest}"


def diff_interval(clicks_a: int, shown_a: int, clicks_b: int, shown_b: int) -> tuple[float, float]:
    """95% interval of rate A minus rate B in percentage points, unpooled. (0, 0) when it cannot be computed."""
    if not shown_a or not shown_b:
        return 0.0, 0.0
    pa, pb = clicks_a / shown_a, clicks_b / shown_b
    se = math.sqrt(pa * (1 - pa) / shown_a + pb * (1 - pb) / shown_b)
    return (pa - pb - 1.96 * se) * 100, (pa - pb + 1.96 * se) * 100


def render(data: dict) -> str:
    r1, r2, landing = data["round1"], data["round2"], data["landing"]
    ing, tex, a, b = r1["ingredient"], r1["texture"], r2["a"], r2["b"]
    r1_total = ing["impressions"] + tex["impressions"]
    r2_total = a["impressions"] + b["impressions"]
    steps = landing["sections"]["steps"]
    values = {f"chart_{name.replace('-', '_')}": svg for name, svg in charts(data).items()}
    same = r1["same_days"]
    z, p = two_proportion_z(a["clicks"], a["impressions"], b["clicks"], b["impressions"])
    ci_low, ci_high = diff_interval(a["clicks"], a["impressions"], b["clicks"], b["impressions"])
    r2_clicks = a["clicks"] + b["clicks"]
    l2 = landing["round2"]
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
        # the gap is taken from the rounded rates so it matches the two numbers printed beside it
        r2_gap=f"{abs(round(rate(a['clicks'], a['impressions']), 2) - round(rate(b['clicks'], b['impressions']), 2)):.2f}%p",
        r2_test=f"z = {z:.2f}, p = {p:.2f}" if p >= 0.01 else f"z = {z:.2f}, p < 0.01",
        r2_ci=f"{ci_low:.2f}%p ~ {ci_high:.2f}%p".replace("-", "\u2212"),
        r2_imp_total=num(r2_total),
        r1_imp_total=num(r1_total),
        r1_period=r1["period"],
        holiday_note="음영은 주말과 공휴일" + (f"({', '.join(f'{d} {n}' for d, n in data['calendar']['holidays'].items())})" if data.get("calendar", {}).get("holidays") else ""),
        r2_period=r2["period"],
        r2_clk_total=num(r2_clicks),
        r2_arrived=num(l2["arrived"]),
        r2_left=num(l2["arrived"] - l2["interest"]),
        l1_arrived_n=num(landing["round1"]["arrived"]),
        l1_interest_n=num(landing["round1"]["interest"]),
        cost_round=num(round((a["spend"] + b["spend"]) / l2["interest"], -2)) if l2["interest"] else "-",
        cpc_low=num(min(a["spend"] / a["clicks"], b["spend"] / b["clicks"])),
        cpc_high=num(max(a["spend"] / a["clicks"], b["spend"] / b["clicks"])),
        r2_interested=num(l2["interest"]),
        r2_click_rate=pct(r2_clicks, r2_total, 1),
        r2_arrive_rate=pct(l2["arrived"], r2_clicks, 1),
        r2_verdict="5% 기준에서 통계적으로 유의하다" if p < 0.05 else "5% 기준에서 통계적으로 유의하지 않다",
        r2_verdict_short="유의함" if p < 0.05 else "유의하지 않음",
        copy_a=a["copy"],
        copy_b=b["copy"],
        l1_interest=f"{landing['round1']['interest']} / {num(landing['round1']['arrived'])}",
        l2_interest=f"{landing['round2']['interest']} / {num(landing['round2']['arrived'])}",
        l1_cost=num((ing["spend"] + tex["spend"]) / landing["round1"]["interest"]) if landing["round1"]["interest"] else "-",
        l2_cost=num((a["spend"] + b["spend"]) / landing["round2"]["interest"]) if landing["round2"]["interest"] else "-",
        l1_rate=pct(landing["round1"]["interest"], landing["round1"]["arrived"], 1),
        l2_rate=pct(landing["round2"]["interest"], landing["round2"]["arrived"], 1),
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
