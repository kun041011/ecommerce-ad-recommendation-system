"""用户Pydantic模式

定义用户相关的请求/响应数据校验模式，包括注册、登录、用户信息返回和JWT令牌。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.user import AdFrequencyLevel, UserRole


class UserCreate(BaseModel):
    """用户注册请求模式"""
    username: str   # 用户名
    email: str      # 邮箱地址
    password: str   # 明文密码（服务端会进行哈希处理）


class UserLogin(BaseModel):
    """用户登录请求模式"""
    username: str   # 用户名
    password: str   # 明文密码


class UserResponse(BaseModel):
    """用户信息响应模式，用于返回用户详情"""
    id: int                                   # 用户ID
    username: str                             # 用户名
    email: str                                # 邮箱
    avatar_url: Optional[str] = None          # 头像URL
    role: UserRole                            # 用户角色
    activity_score: float                     # 活跃度评分
    ad_frequency_level: AdFrequencyLevel      # 广告频控等级
    created_at: datetime                      # 注册时间
    last_active_at: datetime                  # 最后活跃时间

    model_config = {"from_attributes": True}  # 允许从ORM模型属性构造


class Token(BaseModel):
    """JWT令牌响应模式"""
    access_token: str            # JWT访问令牌
    token_type: str = "bearer"   # 令牌类型，固定为bearer
