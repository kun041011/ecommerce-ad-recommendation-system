import time
from dataclasses import dataclass


@dataclass
class FrequencyPolicy:
    ads_per_page: int
    min_interval_sec: int
    daily_cap: int


POLICIES = {
    "high": FrequencyPolicy(ads_per_page=3, min_interval_sec=60, daily_cap=50),
    "normal": FrequencyPolicy(ads_per_page=2, min_interval_sec=120, daily_cap=30),
    "low": FrequencyPolicy(ads_per_page=1, min_interval_sec=300, daily_cap=10),
}


def get_policy(activity_level: str) -> FrequencyPolicy:
    return POLICIES.get(activity_level, POLICIES["normal"])


class FrequencyController:
    def check(
        self, user_id: int, activity_level: str, today_count: int, last_shown_ts: float
    ) -> dict:
        policy = get_policy(activity_level)

        if today_count >= policy.daily_cap:
            return {"allowed": False, "reason": "daily_cap_reached", "max_ads": 0}

        now = time.time()
        if last_shown_ts > 0 and (now - last_shown_ts) < policy.min_interval_sec:
            return {"allowed": False, "reason": "min_interval_not_met", "max_ads": 0}

        remaining = policy.daily_cap - today_count
        max_ads = min(policy.ads_per_page, remaining)
        return {"allowed": True, "reason": "ok", "max_ads": max_ads}
