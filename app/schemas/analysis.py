from pydantic import BaseModel

class JobAnalysis(BaseModel):
    required_skills: list[str]
    seniority_level: str
    years_experience_required: str | None = None
    key_responsibilities: list[str]
    red_flags: list[str]
    match_score: int | None = None