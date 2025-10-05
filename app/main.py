from fastapi import FastAPI
from app.routers import auth, candidate, interview
from app.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Swipe AI Interview Assistant Backend")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(candidate.router, prefix="/api/candidate", tags=["candidate"])
app.include_router(interview.router, prefix="/api/interview", tags=["interview"])

@app.get("/")
def root():
    return {"message": "Backend is running!"}
