"""认证服务模块

提供密码哈希、JWT令牌生成与解码、用户注册和登录验证等核心认证功能。
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User

# 密码哈希上下文，使用bcrypt算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """对明文密码进行哈希加密

    参数:
        password: 用户输入的明文密码

    返回:
        str: bcrypt哈希后的密码字符串
    """
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """验证明文密码与哈希密码是否匹配

    参数:
        plain: 用户输入的明文密码
        hashed: 数据库中存储的哈希密码

    返回:
        bool: 密码匹配返回True，否则False
    """
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    """生成JWT访问令牌

    参数:
        user_id: 用户ID，作为令牌的主体（sub）

    返回:
        str: 编码后的JWT令牌字符串
    """
    # 计算令牌过期时间
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # 构建JWT载荷
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    """解码JWT访问令牌，提取用户ID

    参数:
        token: JWT令牌字符串

    返回:
        Optional[int]: 解码成功返回用户ID，失败返回None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return int(payload["sub"])
    except Exception:
        return None


def register_user(db: Session, username: str, email: str, password: str) -> User:
    """注册新用户

    创建用户记录并将密码哈希后存储到数据库。

    参数:
        db: 数据库会话
        username: 用户名
        email: 邮箱地址
        password: 明文密码（将被哈希后存储）

    返回:
        User: 创建成功的用户对象
    """
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户登录凭证

    根据用户名查找用户，并验证密码是否正确。

    参数:
        db: 数据库会话
        username: 用户名
        password: 明文密码

    返回:
        Optional[User]: 验证成功返回用户对象，失败返回None
    """
    # 根据用户名查找用户
    user = db.query(User).filter(User.username == username).first()
    # 验证密码是否匹配
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
