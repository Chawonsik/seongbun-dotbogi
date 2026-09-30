import pathlib
import unittest

import check_taxonomy as ct

HEADER = (
    "Trigger,Event Category,Integration,Event Name,Event Description,Event Property,"
    "Property Description,Required,Array,Data Type,Value Example,Analysis,Status,Since,Note\n"
)


def row(trigger, integration, event, prop="", status="active", analysis="why"):
    return f"{trigger},cat,{integration},{event},desc,{prop},pdesc,TRUE,FALSE,String,x,{analysis},{status},2026-09-30,\n"


CSV_OK = HEADER + "".join([
    row("-", "SDK", "*", "utm_source"),
    row("-", "SDK", "*", "round"),
    row("-", "SDK", "*", "is_test"),
    row("view", "SDK", "landing_view"),
    row("click", "SDK", "survey_answer", "q"),
    row("click", "SDK", "survey_answer", "answer"),
    row("auto", "Amplitude autocapture", "session_start"),
    row("view", "Meta Pixel", "PageView"),
    row("click", "Meta Pixel", "InterestClick", status="rejected"),
    row("click", "SDK", "future_click", status="proposed"),
])

HTML_OK = """
<button data-track="interest_click">x</button>
<script>
  var COMMON = {
    utm_source: clean(qs.get('utm_source'))
  };
  if (DEBUG) COMMON.is_test = true;
  COMMON.round = m ? m[1] : '(none)';
  function send(name, props) { window.amplitude.track(name, props); }
  function track(name, extra) { send(name, Object.assign({}, COMMON, extra || {})); }
  window.fbq('init', CFG.pixel); window.fbq('track', 'PageView');
  trackOnce('landing_view');
  track('survey_answer', { q: q.id, answer: o[0] });
</script>
"""


class LoadTaxonomyTest(unittest.TestCase):
    def test_splits_active_rows_by_integration(self):
        tax, errors = ct.load_taxonomy(CSV_OK)
        self.assertEqual(errors, [])
        self.assertEqual(tax.common, {"utm_source", "round", "is_test"})
        self.assertEqual(tax.events, {"landing_view": set(), "survey_answer": {"q", "answer"}})
        self.assertEqual(tax.pixel, {"PageView"})

    def test_ignores_proposed_rejected_and_autocapture(self):
        tax, _ = ct.load_taxonomy(CSV_OK)
        self.assertNotIn("future_click", tax.events)
        self.assertNotIn("InterestClick", tax.pixel)
        self.assertNotIn("session_start", tax.events)

    def test_rejects_unknown_status(self):
        _, errors = ct.load_taxonomy(HEADER + row("view", "SDK", "a_view", status="live"))
        self.assertTrue(any("status" in e for e in errors))

    def test_rejects_non_snake_case_sdk_event(self):
        _, errors = ct.load_taxonomy(HEADER + row("view", "SDK", "LandingView"))
        self.assertTrue(any("snake_case" in e for e in errors))

    def test_requires_analysis_for_active_rows(self):
        _, errors = ct.load_taxonomy(HEADER + row("view", "SDK", "a_view", analysis=""))
        self.assertTrue(any("Analysis" in e for e in errors))

    def test_rejects_duplicate_event_property(self):
        dup = HEADER + row("click", "SDK", "a_click", "q") + row("click", "SDK", "a_click", "q")
        _, errors = ct.load_taxonomy(dup)
        self.assertTrue(any("duplicate" in e for e in errors))

    def test_allows_readding_a_deprecated_row(self):
        csv_text = HEADER + row("click", "SDK", "a_click", "q", status="deprecated") + row("click", "SDK", "a_click", "q")
        _, errors = ct.load_taxonomy(csv_text)
        self.assertEqual(errors, [])

    def test_accepts_byte_order_mark(self):
        _, errors = ct.load_taxonomy("﻿" + HEADER + row("view", "SDK", "a_view"))
        self.assertEqual(errors, [])

    def test_rejects_wrong_header(self):
        _, errors = ct.load_taxonomy("a,b,c\n1,2,3\n")
        self.assertTrue(any("header" in e for e in errors))


class ExtractCodeTest(unittest.TestCase):
    def test_extracts_events_props_common_and_pixel(self):
        code = ct.extract_code(HTML_OK)
        self.assertEqual(code.common, {"utm_source", "round", "is_test"})
        self.assertEqual(code.events, {"landing_view": set(), "survey_answer": {"q", "answer"}})
        self.assertEqual(code.pixel, {"PageView"})

    def test_ignores_sdk_internal_track_and_data_attributes(self):
        code = ct.extract_code(HTML_OK)
        self.assertNotIn("interest_click", code.events)
        self.assertNotIn("name", code.events)

    def test_merges_props_across_calls(self):
        code = ct.extract_code("<script>track('a_view', { x: 1 }); track('a_view', { y: 2 });</script>")
        self.assertEqual(code.events, {"a_view": {"x", "y"}})

    def test_ignores_commented_out_code(self):
        src = """<script>
          // track('old_view', { a: 1 });
          /* trackOnce('older_view'); COMMON.foo = 1; */
          var url = 'https://example.com/x'; track('a_view');
        </script>
        <!-- <script>track('html_comment_view')</script> -->"""
        code = ct.extract_code(src)
        self.assertEqual(set(code.events), {"a_view"})
        self.assertEqual(code.common, set())

    def test_ignores_text_outside_script_tags(self):
        code = ct.extract_code("<p>track('prose_view')</p><script>track('a_view')</script>")
        self.assertEqual(set(code.events), {"a_view"})

    def test_reads_double_quoted_names_and_quoted_keys(self):
        code = ct.extract_code("<script>track(\"a_view\", { 'x': 1, \"y\": 2 });</script>")
        self.assertEqual(code.events, {"a_view": {"x", "y"}})

    def test_flags_non_literal_event_names(self):
        code = ct.extract_code("<script>function track(name, extra) {} track(eventName); trackOnce(`a_${x}`);</script>")
        self.assertEqual(len(code.errors), 2)


class CompareTest(unittest.TestCase):
    def test_matching_code_and_taxonomy_has_no_errors(self):
        tax, _ = ct.load_taxonomy(CSV_OK)
        self.assertEqual(ct.compare(tax, ct.extract_code(HTML_OK)), [])

    def test_reports_event_missing_from_taxonomy(self):
        tax, _ = ct.load_taxonomy(CSV_OK)
        code = ct.extract_code(HTML_OK + "<script>trackOnce('new_click');</script>")
        errors = ct.compare(tax, code)
        self.assertTrue(any("new_click" in e and "not in events.csv" in e for e in errors))

    def test_reports_active_event_missing_from_code(self):
        tax, _ = ct.load_taxonomy(CSV_OK + row("timer", "SDK", "engaged_60s"))
        errors = ct.compare(tax, ct.extract_code(HTML_OK))
        self.assertTrue(any("engaged_60s" in e and "not sent" in e for e in errors))

    def test_reports_property_mismatch(self):
        tax, _ = ct.load_taxonomy(CSV_OK)
        code = ct.extract_code(HTML_OK.replace("answer: o[0]", "choice: o[0]"))
        errors = ct.compare(tax, code)
        self.assertTrue(any("choice" in e for e in errors))
        self.assertTrue(any("answer" in e for e in errors))

    def test_reports_common_property_mismatch(self):
        tax, _ = ct.load_taxonomy(CSV_OK)
        code = ct.extract_code(HTML_OK.replace("COMMON.round", "COMMON.stage"))
        errors = ct.compare(tax, code)
        self.assertTrue(any("stage" in e for e in errors))
        self.assertTrue(any("round" in e for e in errors))

    def test_reports_non_literal_event_names(self):
        tax, _ = ct.load_taxonomy(CSV_OK)
        code = ct.extract_code(HTML_OK + "<script>track(dynamicName);</script>")
        self.assertTrue(any("literal" in e for e in ct.compare(tax, code)))

    def test_reports_pixel_mismatch(self):
        tax, _ = ct.load_taxonomy(CSV_OK)
        code = ct.extract_code(HTML_OK + "<script>fbq('trackCustom', 'InterestClick');</script>")
        errors = ct.compare(tax, code)
        self.assertTrue(any("InterestClick" in e for e in errors))


class RepoTest(unittest.TestCase):
    def test_repository_is_in_sync(self):
        root = pathlib.Path(__file__).resolve().parent.parent
        self.assertEqual(ct.check_repo(root), [])


if __name__ == "__main__":
    unittest.main()
