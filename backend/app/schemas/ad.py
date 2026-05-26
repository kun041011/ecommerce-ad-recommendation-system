"""广告Pydantic模式

定义广告相关的请求/响应数据校验模式，包括广告创建、投放返回、曝光记录和效果统计。
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from app.models.ad import AdStatus, BidType, ImpressionType


class AdCreate(BaseModel):
    """广告创建请求模式（商家/广告主使用）"""
    title: str                                 # 广告标题
    content: str = ""                          # 广告文案
    image_url: str = ""                        # 广告图片URL
    target_url: str = ""                       # 点击跳转目标URL
    bid_amount: float                          # 单次竞价金额
    bid_type: BidType = BidType.CPC            # 竞价类型，默认CPC
    daily_budget: float                        # 每日预算上限
    total_budget: float                        # 总预算上限
    target_tags: Optional[List[str]] = None    # 定向标签，用于匹配目标用户


class AdResponse(BaseModel):
    """广告信息响应模式"""
    id: int                                    # 广告ID
    advertiser_id: int                         # 广告主用户ID
    title: str                                 # 广告标题
    content: str                               # 广告文案
    image_url: str                             # 广告图片URL
    target_url: str                            # 点击跳转URL
    bid_amount: float                          # 单次竞价金额
    bid_type: BidType                          # 竞价类型
    daily_budget: float                        # 每日预算
    total_budget: float                        # 总预算
    spent_amount: float                        # 已消耗金额
    target_tags: Optional[List[str]] = None    # 定向标签
    status: AdStatus                           # 广告状态
    created_at: datetime                       # 创建时间

    model_config = {"from_attributes": True}   # 允许从ORM模型属性构造


class AdFetchResponse(BaseModel):
    """广告投放响应模式，返回当前可展示的广告列表及频控信息"""
    ads: List[AdResponse]      # 本次返回的广告列表
    frequency_level: str       # 用户当前的广告频控等级
    remaining_today: int       # 今日剩余可展示广告次数


class ImpressionCreate(BaseModel):
    """广告曝光/点击/转化事件上报模式"""
    ad_id: int                             # 广告ID
    impression_type: ImpressionType        # 事件类型（展示/点击/转化）
    context: Optional[Dict] = None         # 事件上下文信息


class AdStatsResponse(BaseModel):
    """广告效果统计响应模式"""
    ad_id: int              # 广告ID
    total_shows: int        # 总展示次数
    total_clicks: int       # 总点击次数
    total_converts: int     # 总转化次数
    ctr: float              # 点击率（Click-Through Rate）
    spent: float            # 已消耗金额
