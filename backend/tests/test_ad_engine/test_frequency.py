import time
from app.ad_engine.frequency import FrequencyController, FrequencyPolicy, get_policy


def test_get_policy_high():
    policy = get_policy("high")
    assert policy.ads_per_page == 3
    assert policy.daily_cap == 50
    assert policy.min_interval_sec == 60


def test_get_policy_normal():
    policy = get_policy("normal")
    assert policy.ads_per_page == 2
    assert policy.daily_cap == 30


def test_get_policy_low():
    policy = get_policy("low")
    assert policy.ads_per_page == 1
    assert policy.daily_cap == 10
    assert policy.min_interval_sec == 300


def test_controller_allows_first_request():
    ctrl = FrequencyController()
    result = ctrl.check(user_id=1, activity_level="normal", today_count=0, last_shown_ts=0)
    assert result["allowed"] is True
    assert result["max_ads"] == 2


def test_controller_blocks_daily_cap():
    ctrl = FrequencyController()
    result = ctrl.check(user_id=1, activity_level="low", today_count=10, last_shown_ts=0)
    assert result["allowed"] is False
    assert result["reason"] == "daily_cap_reached"


def test_controller_blocks_interval():
    ctrl = FrequencyController()
    now = time.time()
    result = ctrl.check(user_id=1, activity_level="normal", today_count=5, last_shown_ts=now - 10)
    assert result["allowed"] is False
    assert result["reason"] == "min_interval_not_met"


def test_controller_allows_after_interval():
    ctrl = FrequencyController()
    now = time.time()
    result = ctrl.check(user_id=1, activity_level="normal", today_count=5, last_shown_ts=now - 200)
    assert result["allowed"] is True
