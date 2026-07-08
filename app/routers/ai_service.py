from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_db, get_current_user
from app.models.user import User
from app.models.application import Application
from app.services.ai_service import analyze_job_description
from app.schemas.analysis import JobAnalysis

router = APIRouter(prefix="/applications", tags=["ai-analysis"])

@router.post("/{application_id}/analyze", response_model=JobAnalysis)
def analyze_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app_obj = db.query(Application).filter(
        Application.id == application_id, Application.user_id == current_user.id
    ).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    if not app_obj.job_description:
        raise HTTPException(status_code=400, detail="No job description saved for this application")

    result = analyze_job_description(app_obj.job_description)
    if result is None:
        raise HTTPException(status_code=502, detail="AI analysis failed, please try again")

    return result
