from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.application import Application
from app.models.status_history import StatusHistory
from sqlalchemy import func, Integer

def get_summary(db: Session, user_id: int) -> dict:
    total = db.query(Application).filter(Application.user_id == user_id).count()

    responded_statuses = ["interviewing", "offer", "rejected"]
    responded = db.query(Application).filter(
        Application.user_id == user_id,
        Application.current_status.in_(responded_statuses),
    ).count()

    response_rate = round((responded / total) * 100, 1) if total > 0 else 0.0

    # average time between "applied" and the next status change, per application
    avg_days_query = (
        db.query(
            func.avg(
                func.extract("epoch", StatusHistory.changed_at) -
                func.extract("epoch", Application.applied_date)
            )
        )
        .join(Application, Application.id == StatusHistory.application_id)
        .filter(
            Application.user_id == user_id,
            StatusHistory.status != "applied",
        )
    )
    avg_seconds = avg_days_query.scalar()
    avg_days = round(avg_seconds / 86400, 1) if avg_seconds else None

    return {
        "total_applications": total,
        "responded": responded,
        "response_rate_percent": response_rate,
        "average_days_to_first_response": avg_days,
    }

def get_funnel(db: Session, user_id: int) -> dict:
    statuses = ["applied", "interviewing", "offer", "rejected"]
    counts = {}
    for status in statuses:
        count = db.query(Application).filter(
            Application.user_id == user_id,
            Application.current_status == status,
        ).count()
        counts[status] = count
    return counts

def get_by_source(db: Session, user_id: int) -> list[dict]:
    results = (
        db.query(
            Application.source,
            func.count(Application.id).label("total"),
            func.sum(
                func.cast(Application.current_status.in_(["interviewing", "offer"]), Integer)
            ).label("responded"),
        )
        .filter(Application.user_id == user_id, Application.source.isnot(None))
        .group_by(Application.source)
        .all()
    )

    output = []
    for source, total, responded in results:
        responded = responded or 0
        rate = round((responded / total) * 100, 1) if total > 0 else 0.0
        output.append({
            "source": source,
            "total_applications": total,
            "responded": responded,
            "response_rate_percent": rate,
        })
    return output