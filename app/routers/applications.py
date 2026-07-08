from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_db, get_current_user
from app.models.user import User
from app.models.application import Application
from app.models.status_history import StatusHistory
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("", response_model=ApplicationResponse)
def create_application(
    app_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_app = Application(
        user_id=current_user.id,
        company=app_data.company,
        role=app_data.role,
        source=app_data.source,
        job_description=app_data.job_description,
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    first_status = StatusHistory(application_id=new_app.id, status="applied")
    db.add(first_status)
    db.commit()

    return new_app

@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Application).filter(Application.user_id == current_user.id).all()

@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app_obj = db.query(Application).filter(
        Application.id == application_id, Application.user_id == current_user.id
    ).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj

@router.patch("/{application_id}/status", response_model=ApplicationResponse)
def update_status(
    application_id: int,
    update: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app_obj = db.query(Application).filter(
        Application.id == application_id, Application.user_id == current_user.id
    ).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    app_obj.current_status = update.current_status
    db.add(StatusHistory(application_id=app_obj.id, status=update.current_status))
    db.commit()
    db.refresh(app_obj)
    return app_obj

@router.delete("/{application_id}")
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app_obj = db.query(Application).filter(
        Application.id == application_id, Application.user_id == current_user.id
    ).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app_obj)
    db.commit()
    return {"message": "Deleted successfully"}