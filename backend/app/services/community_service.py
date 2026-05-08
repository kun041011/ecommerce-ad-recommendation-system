from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.community import QA, Review


def create_review(db: Session, user_id: int, product_id: int, rating: int, content: str) -> Review:
    review = Review(user_id=user_id, product_id=product_id, rating=rating, content=content)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_product_reviews(db: Session, product_id: int) -> list:
    return db.query(Review).filter(Review.product_id == product_id).order_by(Review.created_at.desc()).all()


def mark_helpful(db: Session, review_id: int) -> Optional[Review]:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return None
    review.helpful_count += 1
    db.commit()
    db.refresh(review)
    return review


def create_question(db: Session, user_id: int, product_id: int, question: str) -> QA:
    qa = QA(user_id=user_id, product_id=product_id, question=question)
    db.add(qa)
    db.commit()
    db.refresh(qa)
    return qa


def answer_question(db: Session, qa_id: int, user_id: int, answer: str) -> Optional[QA]:
    qa = db.query(QA).filter(QA.id == qa_id).first()
    if not qa:
        return None
    qa.answer = answer
    qa.answered_by = user_id
    db.commit()
    db.refresh(qa)
    return qa


def get_product_qa(db: Session, product_id: int) -> list:
    return db.query(QA).filter(QA.product_id == product_id).order_by(QA.created_at.desc()).all()
