"""社区Pydantic模式

定义社区模块（评价、问答、行为追踪、活跃度）的请求/响应数据校验模式。
"""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, field_validator


class ReviewCreate(BaseModel):
    """商品评价创建请求模式"""
    product_id: int        # 被评价的商品ID
    rating: int            # 评分（1-5星）
    content: str = ""      # 评价文字内容

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """校验评分范围，必须在1到5之间"""
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewResponse(BaseModel):
    """商品评价响应模式"""
    id: int                # 评价ID
    user_id: int           # 评价用户ID
    product_id: int        # 商品ID
    rating: int            # 评分
    content: str           # 评价内容
    helpful_count: int     # "有帮助"投票数
    created_at: datetime   # 评价时间

    model_config = {"from_attributes": True}  # 允许从ORM模型属性构造


class QACreate(BaseModel):
    """商品提问请求模式"""
    product_id: int    # 关联商品ID
    question: str      # 问题内容


class QAAnswerCreate(BaseModel):
    """问题回答请求模式"""
    answer: str        # 回答内容


class QAResponse(BaseModel):
    """商品问答响应模式"""
    id: int                                # 问答ID
    product_id: int                        # 商品ID
    user_id: int                           # 提问用户ID
    question: str                          # 问题内容
    answer: Optional[str] = None           # 回答内容，未回答时为空
    answered_by: Optional[int] = None      # 回答者用户ID
    created_at: datetime                   # 提问时间

    model_config = {"from_attributes": True}  # 允许从ORM模型属性构造


class BehaviorTrack(BaseModel):
    """用户行为追踪上报模式"""
    product_id: Optional[int] = None   # 关联商品ID（搜索、登录等行为可为空）
    behavior_type: str                 # 行为类型（view/click/cart/purchase/search/login）
    context: Optional[Dict] = None     # 行为上下文信息


class ActivityScoreResponse(BaseModel):
    """用户活跃度评分响应模式"""
    score: float               # 活跃度评分（0-100）
    level: str                 # 活跃度等级（如：低、中、高）
    ad_frequency_level: str    # 对应的广告频控等级
