"""认证路由模块

提供用户注册、登录和当前用户信息查询的REST API接口。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import authenticate_user, create_access_token, register_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """用户注册接口

    参数:
        data: 注册信息（用户名、邮箱、密码）
        db: 数据库会话

    返回:
        User: 注册成功的用户信息
    """
    # 检查用户名或邮箱是否已被注册
    existing = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    # 调用注册服务创建新用户
    user = register_user(db, data.username, data.email, data.password)
    return user


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """用户登录接口

    参数:
        data: 登录凭证（用户名、密码）
        db: 数据库会话

    返回:
        Token: 包含JWT访问令牌的响应
    """
    # 验证用户凭证
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # 生成JWT访问令牌
    token = create_access_token(user.id)
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息

    参数:
        current_user: 通过JWT令牌解析出的当前用户

    返回:
        User: 当前用户的详细信息
    """
    return current_user
