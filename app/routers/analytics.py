from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_db, get_current_user
from app.models.user import User
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return analytics_service.get_summary(db, current_user.id)

@router.get("/funnel")
def funnel(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return analytics_service.get_funnel(db, current_user.id)

@router.get("/by-source")
def by_source(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return analytics_service.get_by_source(db, current_user.id)