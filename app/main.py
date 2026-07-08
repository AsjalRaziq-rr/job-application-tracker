from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, applications, ai_analysis, analytics

app = FastAPI(title="Job Application Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(ai_analysis.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"message": "Job tracker API is running"}