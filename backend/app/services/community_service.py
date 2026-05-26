"""社区服务模块

提供商品评价和问答（Q&A）功能的数据库操作。
包括创建评价、标记有用、发布问题和回答问题等功能。
"""

from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.community import QA, Review


def create_review(db: Session, user_id: int, product_id: int, rating: int, content: str) -> Review:
    """创建商品评价

    参数:
        db: 数据库会话
        user_id: 评价用户ID
        product_id: 商品ID
        rating: 评分（如1-5分）
        content: 评价内容

    返回:
        Review: 创建成功的评价对象
    """
    review = Review(user_id=user_id, product_id=product_id, rating=rating, content=content)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_product_reviews(db: Session, product_id: int) -> list:
    """获取指定商品的所有评价

    参数:
        db: 数据库会话
        product_id: 商品ID

    返回:
        list[Review]: 该商品的所有评价，按创建时间倒序排列
    """
    return db.query(Review).filter(Review.product_id == product_id).order_by(Review.created_at.desc()).all()


def mark_helpful(db: Session, review_id: int) -> Optional[Review]:
    """标记评价为有用（helpful_count加1）

    参数:
        db: 数据库会话
        review_id: 评价ID

    返回:
        Optional[Review]: 更新后的评价对象，评价不存在则返回None
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return None
    # 有用计数加1
    review.helpful_count += 1
    db.commit()
    db.refresh(review)
    return review


def create_question(db: Session, user_id: int, product_id: int, question: str) -> QA:
    """创建商品问题

    参数:
        db: 数据库会话
        user_id: 提问用户ID
        product_id: 商品ID
        question: 问题内容

    返回:
        QA: 创建成功的问答记录
    """
    qa = QA(user_id=user_id, product_id=product_id, question=question)
    db.add(qa)
    db.commit()
    db.refresh(qa)
    return qa


def answer_question(db: Session, qa_id: int, user_id: int, answer: str) -> Optional[QA]:
    """回答商品问题

    参数:
        db: 数据库会话
        qa_id: 问答记录ID
        user_id: 回答用户ID
        answer: 回答内容

    返回:
        Optional[QA]: 更新后的问答记录，问题不存在则返回None
    """
    qa = db.query(QA).filter(QA.id == qa_id).first()
    if not qa:
        return None
    # 设置回答内容和回答者ID
    qa.answer = answer
    qa.answered_by = user_id
    db.commit()
    db.refresh(qa)
    return qa


def get_product_qa(db: Session, product_id: int) -> list:
    """获取指定商品的所有问答

    参数:
        db: 数据库会话
        product_id: 商品ID

    返回:
        list[QA]: 该商品的所有问答，按创建时间倒序排列
    """
    return db.query(QA).filter(QA.product_id == product_id).order_by(QA.created_at.desc()).all()
