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
    return create_review(db, user.id, data.product_id, data.rating, data.content)


@router.get("/api/reviews/product/{product_id}", response_model=List[ReviewResponse])
def list_reviews(product_id: int, db: Session = Depends(get_db)):
    return get_product_reviews(db, product_id)


@router.post("/api/reviews/{review_id}/helpful", response_model=ReviewResponse)
def helpful(review_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    review = mark_helpful(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.post("/api/qa", response_model=QAResponse, status_code=status.HTTP_201_CREATED)
def post_question(data: QACreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return create_question(db, user.id, data.product_id, data.question)


@router.get("/api/qa/product/{product_id}", response_model=List[QAResponse])
def list_qa(product_id: int, db: Session = Depends(get_db)):
    return get_product_qa(db, product_id)


@router.post("/api/qa/{qa_id}/answer", response_model=QAResponse)
def post_answer(qa_id: int, data: QAAnswerCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    qa = answer_question(db, qa_id, user.id, data.answer)
    if not qa:
        raise HTTPException(status_code=404, detail="Question not found")
    return qa
