"""화해 랭킹은 매일 05:00 KST 에 바뀐다. 그 앞뒤 시간대(04:50~05:20)를 피한다."""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))
WINDOW_START = (4, 50)
WINDOW_END = (5, 20)


def now_kst() -> datetime:
    return datetime.now(KST)


def now_iso() -> str:
    return now_kst().isoformat(timespec="seconds")


def seconds_to_wait(now: datetime) -> int:
    n = now.astimezone(KST)
    start = n.replace(hour=WINDOW_START[0], minute=WINDOW_START[1], second=0, microsecond=0)
    end = n.replace(hour=WINDOW_END[0], minute=WINDOW_END[1], second=0, microsecond=0)
    if start <= n < end:
        return int((end - n).total_seconds())
    return 0


def wait_if_refresh_window(log=print) -> None:
    wait = seconds_to_wait(now_kst())
    if wait:
        log(f"[schedule] 랭킹 갱신 시간대(04:50~05:20 KST). {wait}초 기다립니다")
        time.sleep(wait)
