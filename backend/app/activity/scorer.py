"""活跃度评分引擎模块

基于用户行为数据计算活跃度评分，融合电商行为和社区行为，
通过指数时间衰减函数实现动态评估。评分范围为0-100。
"""

import math
from datetime import datetime, timezone
from typing import Dict, List

# 各行为类型对应的权重值，购买行为权重最高，浏览行为权重最低
BEHAVIOR_WEIGHTS = {
    "login": 2,       # 登录行为
    "view": 1,        # 浏览行为
    "search": 1,      # 搜索行为
    "cart": 3,        # 加购行为
    "purchase": 10,   # 购买行为，权重最高
    "review": 5,      # 评价行为
    "answer": 5,      # 回答行为
    "helpful": 2,     # 点赞有用行为
}

# 时间衰减系数，值越大衰减越快
DECAY_LAMBDA = 0.1


def time_decay(days_ago: float) -> float:
    """计算时间衰减因子

    使用指数衰减函数 e^(-λ*t)，距今天数越远衰减越大。

    参数:
        days_ago: 距今天数

    返回:
        float: 衰减因子，范围(0, 1]
    """
    return math.exp(-DECAY_LAMBDA * days_ago)


def calculate_activity_score(behaviors: List[Dict]) -> float:
    """计算用户活跃度评分

    遍历用户行为记录，根据行为类型权重和时间衰减因子加权求和，
    最终评分限制在0-100之间。

    参数:
        behaviors: 用户行为记录列表，每条记录包含 behavior_type 和 created_at

    返回:
        float: 活跃度评分（0-100）
    """
    now = datetime.now(timezone.utc)
    score = 0.0
    # 遍历行为记录，累加加权衰减分数
    for b in behaviors:
        weight = BEHAVIOR_WEIGHTS.get(b["behavior_type"], 0)
        created = b["created_at"]
        # 如果时间戳无时区信息，默认为UTC
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        # 计算距今天数
        days_ago = (now - created).total_seconds() / 86400
        score += weight * time_decay(max(0, days_ago))
    # 分数上限100分，保留两位小数
    return min(100.0, round(score, 2))


def classify_activity_level(score: float) -> str:
    """根据活跃度评分划分用户等级

    将用户分为高活跃、普通和低活跃三个等级，
    用于后续广告频控策略的差异化处理。

    参数:
        score: 活跃度评分

    返回:
        str: 活跃等级（high/normal/low）
    """
    if score >= 60:
        return "high"      # 高活跃用户
    elif score >= 20:
        return "normal"    # 普通用户
    return "low"           # 低活跃用户
