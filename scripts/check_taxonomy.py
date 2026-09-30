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

# track('event') / trackOnce('event', { key: value, ... }), but not amplitude.track(name, ...)
TRACK_CALL = re.compile(r"(?<![\w.])track(?:Once)?\(\s*'([^']+)'\s*(?:,\s*\{([^}]*)\})?")
OBJECT_KEY = re.compile(r"(?:^|,)\s*([A-Za-z_]\w*)\s*:")
COMMON_LITERAL = re.compile(r"var\s+COMMON\s*=\s*\{([^}]*)\}", re.S)
COMMON_ASSIGN = re.compile(r"COMMON\.(\w+)\s*=(?!=)")
PIXEL_CALL = re.compile(r"fbq\(\s*'(?:track|trackCustom)'\s*,\s*'([^']+)'")


@dataclass
class Tracking:
    common: set = field(default_factory=set)
    events: dict = field(default_factory=dict)
    pixel: set = field(default_factory=set)


def load_taxonomy(csv_text):
    """Return (Tracking of active rows, list of sheet errors)."""
    reader = csv.reader(io.StringIO(csv_text))
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
    key = (r["Integration"], r["Event Name"], r["Event Property"])
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
    """Return the Tracking actually sent by a page's inline script."""
    code = Tracking()
    for event, body in TRACK_CALL.findall(source):
        code.events.setdefault(event, set()).update(OBJECT_KEY.findall(body or ""))
    for body in COMMON_LITERAL.findall(source):
        code.common.update(OBJECT_KEY.findall(body))
    code.common.update(COMMON_ASSIGN.findall(source))
    code.pixel.update(PIXEL_CALL.findall(source))
    return code


def merge(trackings):
    total = Tracking()
    for t in trackings:
        total.common |= t.common
        total.pixel |= t.pixel
        for event, props in t.events.items():
            total.events.setdefault(event, set()).update(props)
    return total


def compare(tax, code):
    """List every difference between the taxonomy and the code."""
    errors = _set_diff("common property", tax.common, code.common)
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
    tax, errors = load_taxonomy((root / TAXONOMY_PATH).read_text(encoding="utf-8"))
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
