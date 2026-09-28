from datetime import datetime

from crawler import schedule


def _kst(h, m):
    return datetime(2026, 9, 29, h, m, tzinfo=schedule.KST)


def test_outside_window_no_wait():
    assert schedule.seconds_to_wait(_kst(3, 0)) == 0
    assert schedule.seconds_to_wait(_kst(5, 20)) == 0
    assert schedule.seconds_to_wait(_kst(14, 0)) == 0


def test_inside_window_waits_until_0520():
    assert schedule.seconds_to_wait(_kst(4, 50)) == 30 * 60
    assert schedule.seconds_to_wait(_kst(5, 0)) == 20 * 60
    assert schedule.seconds_to_wait(_kst(5, 19)) == 60


def test_now_iso_has_kst_offset():
    assert schedule.now_iso().endswith("+09:00")
