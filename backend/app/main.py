"""FastAPI应用入口

创建FastAPI应用实例，配置CORS中间件，注册所有API路由模块，并提供数据库初始化和健康检查接口。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, products, orders, community, behavior, ads, activity, recommend, analytics

# 创建FastAPI应用实例
app = FastAPI(title="E-Commerce Ad Recommendation System", version="1.0.0")

# 配置CORS中间件，允许前端（Vite开发服务器）跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册各功能模块的API路由
app.include_router(auth.router)         # 认证模块（注册、登录）
app.include_router(products.router)     # 商品模块（CRUD、搜索）
app.include_router(orders.router)       # 订单模块（下单、查询）
app.include_router(community.router)    # 社区模块（评价、问答）
app.include_router(behavior.router)     # 行为追踪模块
app.include_router(ads.router)          # 广告模块（投放、竞价、统计）
app.include_router(activity.router)     # 活跃度模块（评分计算）
app.include_router(recommend.router)    # 推荐模块（UserCF、MMR）
app.include_router(analytics.router)    # 数据分析模块


def init_db():
    """初始化数据库，创建data目录并建表"""
    import os
    os.makedirs("data", exist_ok=True)
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health_check():
    """健康检查接口，用于监控服务是否正常运行"""
    return {"status": "ok"}
