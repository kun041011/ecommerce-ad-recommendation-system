"""依赖注入模块

提供JWT认证和角色权限校验的FastAPI依赖函数。
包括当前用户获取、商家权限校验和管理员权限校验。
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import decode_access_token

# HTTP Bearer认证方案，用于从请求头提取JWT令牌
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """获取当前登录用户（JWT认证依赖）

    从请求头中提取Bearer Token，解码JWT获取用户ID，
    然后从数据库查询对应用户。

    Args:
        credentials: HTTP Bearer认证凭证（包含JWT令牌）
        db: 数据库会话

    Returns:
        User: 当前登录的用户对象

    Raises:
        HTTPException: 令牌无效（401）或用户不存在（401）
    """
    # 解码JWT令牌获取用户ID
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    # 根据用户ID查询数据库
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_merchant(user: User = Depends(get_current_user)) -> User:
    """商家权限校验依赖

    要求当前用户角色为商家或管理员，否则拒绝访问。

    Args:
        user: 当前登录用户（通过get_current_user获取）

    Returns:
        User: 具有商家权限的用户对象

    Raises:
        HTTPException: 无商家权限（403）
    """
    if user.role not in (UserRole.merchant, UserRole.admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Merchant access required")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """管理员权限校验依赖

    要求当前用户角色为管理员，否则拒绝访问。

    Args:
        user: 当前登录用户（通过get_current_user获取）

    Returns:
        User: 具有管理员权限的用户对象

    Raises:
        HTTPException: 无管理员权限（403）
    """
    if user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
