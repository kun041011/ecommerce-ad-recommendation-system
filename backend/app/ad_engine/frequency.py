"""广告频控组件模块

根据用户活跃度等级实施差异化的广告频率控制策略，
包括每页广告数、最小展示间隔和每日展示上限。
"""

import time
from dataclasses import dataclass


@dataclass
class FrequencyPolicy:
    """频控策略数据类

    定义单个活跃等级对应的广告投放限制参数。

    Attributes:
        ads_per_page: 每页最多展示广告数
        min_interval_sec: 两次展示之间的最小间隔（秒）
        daily_cap: 每日展示上限
    """
    ads_per_page: int
    min_interval_sec: int
    daily_cap: int


# 各活跃等级对应的频控策略，高活跃用户频次更高、间隔更短
POLICIES = {
    "high": FrequencyPolicy(ads_per_page=3, min_interval_sec=60, daily_cap=50),      # 高活跃：每页3条，间隔60秒，日上限50
    "normal": FrequencyPolicy(ads_per_page=2, min_interval_sec=120, daily_cap=30),    # 普通：每页2条，间隔120秒，日上限30
    "low": FrequencyPolicy(ads_per_page=1, min_interval_sec=300, daily_cap=10),       # 低活跃：每页1条，间隔300秒，日上限10
}


def get_policy(activity_level: str) -> FrequencyPolicy:
    """根据活跃等级获取对应的频控策略

    Args:
        activity_level: 用户活跃等级（high/normal/low）

    Returns:
        FrequencyPolicy: 对应的频控策略，未匹配时返回普通等级策略
    """
    return POLICIES.get(activity_level, POLICIES["normal"])


class FrequencyController:
    """广告频率控制器

    综合判断用户当前是否允许展示广告，以及最多可展示的广告数量。
    """

    def check(
        self, user_id: int, activity_level: str, today_count: int, last_shown_ts: float
    ) -> dict:
        """检查用户是否允许展示广告

        依次检查每日上限和最小时间间隔两个条件。

        Args:
            user_id: 用户ID
            activity_level: 用户活跃等级
            today_count: 今日已展示次数
            last_shown_ts: 上次展示的时间戳

        Returns:
            dict: 包含 allowed（是否允许）、reason（原因）、max_ads（可展示数量）
        """
        policy = get_policy(activity_level)

        # 检查是否达到每日展示上限
        if today_count >= policy.daily_cap:
            return {"allowed": False, "reason": "daily_cap_reached", "max_ads": 0}

        # 检查距上次展示是否满足最小间隔要求
        now = time.time()
        if last_shown_ts > 0 and (now - last_shown_ts) < policy.min_interval_sec:
            return {"allowed": False, "reason": "min_interval_not_met", "max_ads": 0}

        # 计算剩余可展示数量，取每页上限与剩余配额的较小值
        remaining = policy.daily_cap - today_count
        max_ads = min(policy.ads_per_page, remaining)
        return {"allowed": True, "reason": "ok", "max_ads": max_ads}
