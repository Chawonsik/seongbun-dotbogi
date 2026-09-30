"""Check that landing page tracking code matches docs/taxonomy/events.csv.

Usage: python3 scripts/check_taxonomy.py
Exits 1 and lists every mismatch when code and taxonomy disagree.
"""

import csv
import io
import pathlib
import re
import sys
from dataclasses import dataclass, field

TAXONOMY_PATH = pathlib.Path("docs/taxonomy/events.csv")
PAGES_GLOB = "landing/*.html"

HEADER = [
    "Trigger", "Event Category", "Integration", "Event Name", "Event Description",
    "Event Property", "Property Description", "Required", "Array", "Data Type",
    "Value Example", "Analysis", "Status", "Since", "Note",
]
STATUSES = {"proposed", "active", "deprecated", "rejected"}
SDK = "SDK"
PIXEL = "Meta Pixel"
COMMON_EVENT = "*"
SNAKE_CASE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")

# Supported call shape: track('event') or trackOnce('event', { key: value, ... }) with a flat object
# literal. Nested braces or shorthand keys make the check fail loudly instead of passing silently.
# amplitude.track(name, ...) inside the SDK wrapper is not a call site and is skipped.
TRACK_CALL = re.compile(r'''(?<![\w.])track(?:Once)?\(\s*(['"])([^'"]+)\1\s*(?:,\s*\{([^}]*)\})?''')
ANY_TRACK_CALL = re.compile(r"(?<![\w.])track(?:Once)?\(\s*([^\s)])")
WRAPPER_DEF = re.compile(r"function\s+track(?:Once)?\s*\([^)]*\)\s*\{")
OBJECT_KEY = re.compile(r'''(?:^|,)\s*['"]?([A-Za-z_]\w*)['"]?\s*:''')
COMMON_LITERAL = re.compile(r"var\s+COMMON\s*=\s*\{([^}]*)\}", re.S)
COMMON_ASSIGN = re.compile(r"COMMON\.(\w+)\s*=(?!=)")
PIXEL_CALL = re.compile(r'''fbq\(\s*['"](?:track|trackCustom)['"]\s*,\s*['"]([^'"]+)['"]''')
SCRIPT_BODY = re.compile(r"<script\b[^>]*>(.*?)</script>", re.S | re.I)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)


@dataclass
class Tracking:
    common: set = field(default_factory=set)
    events: dict = field(default_factory=dict)
    pixel: set = field(default_factory=set)
    errors: list = field(default_factory=list)


def load_taxonomy(csv_text):
    """Return (Tracking of active rows, list of sheet errors)."""
    reader = csv.reader(io.StringIO(csv_text.lstrip("\ufeff")))
    header = next(reader, [])
    if header != HEADER:
        return Tracking(), [f"events.csv header must be: {','.join(HEADER)}"]

    tax, errors, seen = Tracking(), [], set()
    for line_no, cells in enumerate(reader, start=2):
        if not any(cells):
            continue
        if len(cells) != len(HEADER):
            errors.append(f"events.csv line {line_no}: expected {len(HEADER)} columns, got {len(cells)}")
            continue
        r = dict(zip(HEADER, cells))
        errors.extend(_row_errors(r, line_no, seen))
        if r["Status"] == "active":
            _add_active(tax, r)
    return tax, errors


def _row_errors(r, line_no, seen):
    errors = []
    where = f"events.csv line {line_no} ({r['Event Name']} {r['Event Property']})".rstrip()
    if r["Status"] not in STATUSES:
        errors.append(f"{where}: status must be one of {sorted(STATUSES)}")
    if r["Integration"] == SDK:
        for name in (r["Event Name"], r["Event Property"]):
            if name and name != COMMON_EVENT and not SNAKE_CASE.match(name):
                errors.append(f"{where}: '{name}' is not snake_case")
    if r["Status"] in {"active", "proposed"} and not r["Analysis"].strip():
        errors.append(f"{where}: Analysis is empty. Say what decision this data supports")
    key = (r["Integration"], r["Event Name"], r["Event Property"], r["Status"])
    if key in seen:
        errors.append(f"{where}: duplicate event and property")
    seen.add(key)
    return errors


def _add_active(tax, r):
    event, prop = r["Event Name"], r["Event Property"]
    if r["Integration"] == PIXEL:
        tax.pixel.add(event)
    elif r["Integration"] != SDK:
        return
    elif event == COMMON_EVENT:
        tax.common.add(prop)
    else:
        props = tax.events.setdefault(event, set())
        if prop:
            props.add(prop)


def extract_code(source):
    """Return the Tracking actually sent by a page's inline scripts."""
    js = "\n".join(_strip_js_comments(b) for b in SCRIPT_BODY.findall(HTML_COMMENT.sub("", source)))
    js = _drop_wrapper_definitions(js)
    code = Tracking()
    for _, event, body in TRACK_CALL.findall(js):
        code.events.setdefault(event, set()).update(OBJECT_KEY.findall(body or ""))
    for m in ANY_TRACK_CALL.finditer(js):
        if m.group(1) not in "'\"":
            code.errors.append(f"track call without a literal event name: {js[m.start():m.start() + 40]!r}")
    for body in COMMON_LITERAL.findall(js):
        code.common.update(OBJECT_KEY.findall(body))
    code.common.update(COMMON_ASSIGN.findall(js))
    code.pixel.update(PIXEL_CALL.findall(js))
    return code


def _strip_js_comments(js):
    """Remove // and /* */ comments, leaving string contents (like URLs) alone."""
    out, i, quote = [], 0, None
    while i < len(js):
        c = js[i]
        if quote:
            out.append(c)
            if c == "\\" and i + 1 < len(js):
                out.append(js[i + 1])
                i += 1
            elif c == quote:
                quote = None
        elif c in "'\"`":
            quote = c
            out.append(c)
        elif js.startswith("//", i):
            i = js.find("\n", i)
            if i == -1:
                break
            continue
        elif js.startswith("/*", i):
            end = js.find("*/", i + 2)
            i = len(js) if end == -1 else end + 2
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out)


def _drop_wrapper_definitions(js):
    """Remove the bodies of function track/trackOnce, which forward a variable name."""
    while (m := WRAPPER_DEF.search(js)):
        depth, i = 1, m.end()
        while i < len(js) and depth:
            depth += {"{": 1, "}": -1}.get(js[i], 0)
            i += 1
        js = js[:m.start()] + js[i:]
    return js


def merge(trackings):
    total = Tracking()
    for t in trackings:
        total.common |= t.common
        total.pixel |= t.pixel
        total.errors += t.errors
        for event, props in t.events.items():
            total.events.setdefault(event, set()).update(props)
    return total


def compare(tax, code):
    """List every difference between the taxonomy and the code."""
    errors = list(code.errors)
    errors += _set_diff("common property", tax.common, code.common)
    errors += _set_diff("Meta Pixel event", tax.pixel, code.pixel)
    errors += _set_diff("event", set(tax.events), set(code.events))
    for event in sorted(set(tax.events) & set(code.events)):
        errors += _set_diff(f"property on {event}", tax.events[event], code.events[event])
    return errors


def _set_diff(label, documented, sent):
    return (
        [f"{label} '{n}' is sent by the code but not in events.csv as active" for n in sorted(sent - documented)]
        + [f"{label} '{n}' is active in events.csv but not sent by the code" for n in sorted(documented - sent)]
    )


def check_repo(root):
    root = pathlib.Path(root)
    tax, errors = load_taxonomy((root / TAXONOMY_PATH).read_text(encoding="utf-8-sig"))
    pages = sorted(root.glob(PAGES_GLOB))
    code = merge(extract_code(p.read_text(encoding="utf-8")) for p in pages)
    return errors + compare(tax, code)


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    errors = check_repo(root)
    if errors:
        print("Tracking code and docs/taxonomy/events.csv disagree:")
        for e in errors:
            print(f"  - {e}")
        print("Fix the code or update events.csv in the same PR (see docs/taxonomy/README.md section 6).")
        return 1
    print("Taxonomy check passed: tracking code matches docs/taxonomy/events.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
