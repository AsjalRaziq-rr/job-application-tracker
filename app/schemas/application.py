from pydantic import BaseModel
from datetime import datetime

class ApplicationCreate(BaseModel):
    company: str
    role: str
    source: str | None = None
    job_description: str | None = None

class ApplicationUpdate(BaseModel):
    current_status: str

class ApplicationResponse(BaseModel):
    id: int
    company: str
    role: str
    source: str | None
    current_status: str
    job_description: str | None
    applied_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True