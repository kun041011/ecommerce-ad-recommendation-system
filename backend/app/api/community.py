"""社区路由模块

提供商品评价和问答（Q&A）功能的REST API接口。
包括发布评价、标记评价有用、提问和回答等功能。
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.community import QAAnswerCreate, QACreate, QAResponse, ReviewCreate, ReviewResponse
from app.services.community_service import (
    answer_question, create_question, create_review, get_product_qa, get_product_reviews, mark_helpful,
)

router = APIRouter(tags=["community"])


@router.post("/api/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def post_review(data: ReviewCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """发布商品评价

    参数:
        data: 评价信息（商品ID、评分、评价内容）
        db: 数据库会话
        user: 当前登录用户

    返回:
        Review: 创建成功的评价信息
    """
    return create_review(db, user.id, data.product_id, data.rating, data.content)


@router.get("/api/reviews/product/{product_id}", response_model=List[ReviewResponse])
def list_reviews(product_id: int, db: Session = Depends(get_db)):
    """获取指定商品的评价列表

    参数:
        product_id: 商品ID
        db: 数据库会话

    返回:
        list[Review]: 该商品的所有评价，按时间倒序
    """
    return get_product_reviews(db, product_id)


@router.post("/api/reviews/{review_id}/helpful", response_model=ReviewResponse)
def helpful(review_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    """标记评价为有用（点赞）

    参数:
        review_id: 评价ID
        db: 数据库会话
        _user: 当前登录用户（用于登录校验）

    返回:
        Review: 更新后的评价信息（helpful_count加1）
    """
    review = mark_helpful(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.post("/api/qa", response_model=QAResponse, status_code=status.HTTP_201_CREATED)
def post_question(data: QACreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """发布商品提问

    参数:
        data: 提问信息（商品ID、问题内容）
        db: 数据库会话
        user: 当前登录用户

    返回:
        QA: 创建成功的问答记录
    """
    return create_question(db, user.id, data.product_id, data.question)


@router.get("/api/qa/product/{product_id}", response_model=List[QAResponse])
def list_qa(product_id: int, db: Session = Depends(get_db)):
    """获取指定商品的问答列表

    参数:
        product_id: 商品ID
        db: 数据库会话

    返回:
        list[QA]: 该商品的所有问答，按时间倒序
    """
    return get_product_qa(db, product_id)


@router.post("/api/qa/{qa_id}/answer", response_model=QAResponse)
def post_answer(qa_id: int, data: QAAnswerCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """回答商品问题

    参数:
        qa_id: 问答记录ID
        data: 回答内容
        db: 数据库会话
        user: 当前登录用户（回答者）

    返回:
        QA: 更新后的问答记录（包含回答内容）
    """
    qa = answer_question(db, qa_id, user.id, data.answer)
    if not qa:
        raise HTTPException(status_code=404, detail="Question not found")
    return qa
