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


class TwoProportionTest(unittest.TestCase):
    def test_known_values(self):
        z, p = mr.two_proportion_z(204, 6869, 181, 6545)
        self.assertAlmostEqual(z, 0.709, places=3)
        self.assertAlmostEqual(p, 0.479, places=3)

    def test_equal_rates_give_p_of_one(self):
        z, p = mr.two_proportion_z(10, 1000, 10, 1000)
        self.assertEqual(z, 0)
        self.assertAlmostEqual(p, 1.0)

    def test_large_gap_is_significant(self):
        _, p = mr.two_proportion_z(60, 1000, 20, 1000)
        self.assertLess(p, 0.001)

    def test_sign_follows_direction(self):
        z, p = mr.two_proportion_z(181, 6545, 204, 6869)
        self.assertLess(z, 0)
        self.assertAlmostEqual(p, mr.two_proportion_z(204, 6869, 181, 6545)[1])

    def test_degenerate_inputs_do_not_crash(self):
        for args in ((0, 0, 3, 100), (0, 100, 0, 100), (5, 5, 7, 7)):
            self.assertEqual(mr.two_proportion_z(*args), (0.0, 1.0))


class DiffIntervalTest(unittest.TestCase):
    def test_known_values(self):
        low, high = mr.diff_interval(204, 6869, 181, 6545)
        self.assertAlmostEqual(low, -0.36, places=2)
        self.assertAlmostEqual(high, 0.77, places=2)

    def test_degenerate_inputs_do_not_crash(self):
        self.assertEqual(mr.diff_interval(0, 0, 3, 100), (0.0, 0.0))


class AxisTest(unittest.TestCase):
    def test_ticks_cover_the_peak_in_round_steps(self):
        self.assertEqual(mr.nice_ticks(2506), [0, 1000, 2000, 3000])
        self.assertEqual(mr.nice_ticks(3.99), [0, 1, 2, 3, 4])
        self.assertEqual(mr.nice_ticks(0), [0.0, 1.0])

    def test_day_labels_show_the_month_once_and_the_weekday(self):
        labels, weekdays = mr.day_labels(["10/30", "10/31", "11/1"], 2026)
        self.assertEqual(labels, ["10/30", "31", "11/1"])
        self.assertEqual(weekdays, ["금", "토", "일"])

    def test_off_days_are_weekends_and_listed_holidays(self):
        days = ["10/2", "10/3", "10/4", "10/5", "10/6", "10/9"]
        self.assertEqual(mr.off_days(days, 2026, {"10/5": "대체공휴일", "10/9": "한글날"}), {1, 2, 3, 5})
        self.assertEqual(mr.off_days(["10/6"], 2026, {}), set())


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
            "원료 " + mr.pct(*r1["same_days"]["ingredient"]) + ", 사용감 " + mr.pct(*r1["same_days"]["texture"]),
            mr.pct(a["impressions"], a["impressions"] + b["impressions"], 1) + " 대",
        ]
        for text in expected:
            self.assertIn(text, self.html)

    def test_landing_interest_shown_as_rates(self):
        landing = DATA["landing"]
        for key in ("round1", "round2"):
            rate = mr.pct(landing[key]["interest"], landing[key]["arrived"], 1)
            self.assertIn(f"{rate}({landing[key]['interest']} / {mr.num(landing[key]['arrived'])})", self.html)

    def test_round2_test_result_comes_from_data(self):
        a, b = DATA["round2"]["a"], DATA["round2"]["b"]
        z, p = mr.two_proportion_z(a["clicks"], a["impressions"], b["clicks"], b["impressions"])
        self.assertIn(f"z = {z:.2f}, p = {p:.2f}", self.html)

    def test_cost_per_interested_device(self):
        r1, r2, landing = DATA["round1"], DATA["round2"], DATA["landing"]
        r1_spend = r1["ingredient"]["spend"] + r1["texture"]["spend"]
        r2_spend = r2["a"]["spend"] + r2["b"]["spend"]
        self.assertIn(f"{mr.num(r1_spend / landing['round1']['interest'])}원", self.html)
        self.assertIn(f"{mr.num(r2_spend / landing['round2']['interest'])}원", self.html)

    def test_result_sections_show_the_ads(self):
        for src in ("r1-ingredient.webp", "r1-texture.webp"):
            self.assertIn(src, self.html)
        self.assertGreaterEqual(self.html.count("r2-ad-review.webp"), 2)

    def test_significance_sentence_follows_p(self):
        data = copy.deepcopy(DATA)
        self.assertIn("5% 기준에서 통계적으로 유의하지 않다", mr.render(data))
        data["round2"]["a"]["clicks"] += 200
        data["round2"]["daily"][0]["a"][0] += 200
        html = mr.render(data)
        self.assertNotIn("5% 기준에서 통계적으로 유의하지 않다", html)
        self.assertIn("5% 기준에서 통계적으로 유의하다", html)

    def test_gap_matches_the_printed_rates(self):
        data = copy.deepcopy(DATA)
        data["round2"]["a"].update(clicks=2976, impressions=100000)
        data["round2"]["b"].update(clicks=2774, impressions=100000)
        data["round2"]["daily"] = [{"day": "10/9", "a": [1488, 50000], "b": [1387, 50000]}, {"day": "10/10", "a": [1488, 50000], "b": [1387, 50000]}]
        html = mr.render(data)
        self.assertIn("0.21%p", html)

    def test_interval_is_shown_with_the_test(self):
        a, b = DATA["round2"]["a"], DATA["round2"]["b"]
        low, high = mr.diff_interval(a["clicks"], a["impressions"], b["clicks"], b["impressions"])
        self.assertIn(f"95% 신뢰구간 {low:.2f}%p ~ {high:.2f}%p", self.html.replace("\u2212", "-"))

    def test_after_click_funnel_comes_from_data(self):
        a, b, l2 = DATA["round2"]["a"], DATA["round2"]["b"], DATA["landing"]["round2"]
        for value in (a["impressions"] + b["impressions"], a["clicks"] + b["clicks"], l2["arrived"]):
            self.assertIn(f">{mr.num(value)}<", self.html)
        self.assertIn(mr.pct(l2["interest"], l2["arrived"], 1), self.html)

    def test_sources_and_ai_use_are_disclosed(self):
        for needle in ("출처와 AI 사용", "business.hwahae.co.kr", "GPT", "Claude"):
            self.assertIn(needle, self.html)

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

    def test_line_charts_have_a_scale_and_rest_day_bands(self):
        charts = mr.charts(DATA)
        for key, expected_bands, unit in (("r1-daily-impressions", 4, "3,000"), ("r2-ctr", 3, "4%")):
            svg = charts[key]
            self.assertEqual(svg.count('class="vz-off"'), expected_bands, key)
            self.assertIn(f'font-size="11">{unit}</text>', svg, key)
        self.assertIn("음영은 10/3 개천절, 10/5 대체공휴일, 10/9 한글날, 10/3~4 주말", self.html)
        self.assertIn("음영은 10/9 한글날, 10/10~11 주말", self.html)

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

    def test_r2_daily_ctr_is_a_line_chart_like_round1(self):
        extra = [{"day": f"10/{d}", "a": [20, 900], "b": [21, 900]} for d in (16, 17)]
        svg = mr.charts(self.with_days(extra))["r2-ctr"]
        self.assertIn('class="vz-la"', svg)
        self.assertNotIn("누적", svg)
        # only the latest day is labeled, one label per line
        self.assertEqual(len(re.findall(r'font-size="12">[0-9.]+%</text>', svg)), 2)

    def test_labels_of_equal_bars_do_not_share_a_line(self):
        svg = mr.grouped_bars(["x"], [("one", "vz-a", [5], ["5.00%"]), ("two", "vz-b", [5], ["5.00%"])], "t")
        ys = re.findall(r'y="([0-9.]+)" text-anchor="middle" font-size="12">5.00%', svg)
        self.assertEqual(len(set(ys)), 2)

    def test_label_clears_a_taller_neighbour_it_spills_over(self):
        days = [f"d{i}" for i in range(8)]
        series = [("one", "vz-a", [2.97] * 8, ["2.97%"] * 8), ("two", "vz-b", [2.55] * 8, ["2.55%"] * 8)]
        svg = mr.grouped_bars(days, series, "t")
        bars = [
            (float(x), float(top), float(right))
            for x, top, right in re.findall(r'd="M([0-9.]+),[0-9.]+ V[0-9.]+ Q[0-9.]+,([0-9.]+) [0-9.]+,[0-9.]+ H[0-9.]+ Q([0-9.]+),', svg)
        ]
        labels = re.findall(r'x="([0-9.]+)" y="([0-9.]+)" text-anchor="middle" font-size="12">([0-9.]+%)</text>', svg)
        self.assertEqual(len(labels), 2)
        for cx, y, text in labels:
            half = len(text) * 12 * 0.3
            for left, top, right in bars:
                if float(cx) - half < right and float(cx) + half > left:
                    self.assertLessEqual(float(y), top - 4, f"{text} at y={y} overlaps a bar whose top is {top}")


if __name__ == "__main__":
    unittest.main()
