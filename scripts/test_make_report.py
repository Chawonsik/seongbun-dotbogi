import copy
import json
import pathlib
import re
import unittest

import make_report as mr

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "docs" / "report" / "data.json").read_text(encoding="utf-8"))


def rect_heights(svg, cls):
    return [float(h) for h in re.findall(rf'<path class="{cls}" data-h="([0-9.]+)"', svg)]


class PctTest(unittest.TestCase):
    def test_two_decimals(self):
        self.assertEqual(mr.pct(28, 1000), "2.80%")

    def test_one_decimal(self):
        self.assertEqual(mr.pct(2136, 4233, 1), "50.5%")

    def test_zero_denominator(self):
        self.assertEqual(mr.pct(3, 0), "-")

    def test_small_share_keeps_a_decimal(self):
        self.assertEqual(mr.share(1, 210), "0.5%")

    def test_large_share_is_rounded(self):
        self.assertEqual(mr.share(208, 210), "99%")


class GroupedBarsTest(unittest.TestCase):
    def setUp(self):
        self.svg = mr.grouped_bars(
            ["a", "b"],
            [("one", "vz-a", [10, 20], ["10", "20"]), ("two", "vz-b", [40, 0], ["40", "0"])],
            "title",
        )

    def test_heights_follow_values(self):
        one = rect_heights(self.svg, "vz-a")
        two = rect_heights(self.svg, "vz-b")
        self.assertAlmostEqual(one[1] / one[0], 2, places=2)
        self.assertAlmostEqual(two[0] / one[0], 4, places=2)

    def test_zero_value_draws_no_bar(self):
        self.assertEqual(len(rect_heights(self.svg, "vz-b")), 1)

    def test_every_value_is_labeled(self):
        for label in ("10", "20", "40", "0"):
            self.assertIn(f">{label}</text>", self.svg)

    def test_has_accessible_title(self):
        self.assertIn("<title>title</title>", self.svg)


class ShareBarsTest(unittest.TestCase):
    def test_widths_follow_shares(self):
        svg = mr.share_bars([("r", [("x", "vz-a", 1), ("y", "vz-b", 3)])], "t")
        widths = [float(w) for w in re.findall(r'data-w="([0-9.]+)"', svg)]
        self.assertEqual(len(widths), 2)
        self.assertAlmostEqual(widths[1] / widths[0], 3, places=1)


class StepBarsTest(unittest.TestCase):
    def test_first_step_is_the_base(self):
        svg = mr.step_bars([("s1", 200), ("s2", 100), ("s3", 0)], "t")
        widths = [float(w) for w in re.findall(r'data-w="([0-9.]+)"', svg)]
        self.assertAlmostEqual(widths[1] / widths[0], 0.5, places=2)
        self.assertIn("50%", svg)
        self.assertIn(">0대", svg)


class RenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = mr.render(DATA)

    def test_numbers_come_from_data(self):
        r1, r2, landing = DATA["round1"], DATA["round2"], DATA["landing"]
        a, b = r2["a"], r2["b"]
        expected = [
            f"{mr.pct(a['clicks'], a['impressions'])} 대 {mr.pct(b['clicks'], b['impressions'])}",
            f"{mr.num(DATA['background']['hwahae_pdrn_products'])}개",
            f"{landing['round1']['interest']} / {mr.num(landing['round1']['arrived'])}",
            mr.pct(*r1["same_days"]["ingredient"]) + "와",
            mr.pct(a["impressions"], a["impressions"] + b["impressions"], 1) + " 대",
        ]
        for text in expected:
            self.assertIn(text, self.html)

    def test_text_from_data_is_escaped(self):
        data = copy.deepcopy(DATA)
        data["headline"]["result_title"] = "<b>A & B</b>"
        html = mr.render(data)
        self.assertNotIn("<b>A & B</b>", html)
        self.assertIn("&lt;b&gt;A &amp; B&lt;/b&gt;", html)

    def test_no_tracking_code(self):
        lowered = self.html.lower()
        for needle in ("<script", "amplitude", "fbq", "gtag", "facebook", "googletagmanager"):
            self.assertNotIn(needle, lowered)

    def test_no_em_dash(self):
        self.assertNotIn("\u2014", self.html)

    def test_four_charts_each_described(self):
        self.assertEqual(self.html.count('<svg class="vz"'), 4)
        self.assertEqual(self.html.count("<desc>"), 4)

    def test_standalone_charts_carry_their_own_colors(self):
        charts = mr.charts(DATA)
        self.assertEqual(len(charts), 4)
        for svg in charts.values():
            self.assertIn("<style>", mr.standalone(svg))


class DataEditTest(unittest.TestCase):
    """The round 2 numbers get refreshed by hand, so plausible edits must not break the build."""

    def with_days(self, extra):
        data = copy.deepcopy(DATA)
        for key in ("a", "b"):
            data["round2"][key]["clicks"] += sum(d[key][0] for d in extra)
            data["round2"][key]["impressions"] += sum(d[key][1] for d in extra)
        data["round2"]["daily"] += extra
        return data

    def test_a_day_without_impressions_still_renders(self):
        mr.render(self.with_days([{"day": "10/12", "a": [0, 0], "b": [0, 0]}]))

    def test_totals_must_match_the_daily_rows(self):
        data = copy.deepcopy(DATA)
        data["round2"]["a"]["clicks"] += 1
        with self.assertRaises(ValueError):
            mr.render(data)

    def test_many_days_label_only_the_cumulative_group(self):
        extra = [{"day": f"10/{d}", "a": [20, 900], "b": [21, 900]} for d in (12, 13, 14, 15)]
        svg = mr.charts(self.with_days(extra))["r2-ctr"]
        self.assertEqual(len(re.findall(r'font-size="12">[0-9.]+%</text>', svg)), 2)

    def test_labels_of_equal_bars_do_not_share_a_line(self):
        svg = mr.grouped_bars(["x"], [("one", "vz-a", [5], ["5.00%"]), ("two", "vz-b", [5], ["5.00%"])], "t")
        ys = re.findall(r'y="([0-9.]+)" text-anchor="middle" font-size="12">5.00%', svg)
        self.assertEqual(len(set(ys)), 2)


if __name__ == "__main__":
    unittest.main()
