from fastapi import FastAPI
from app.routers import auth, candidate, interview
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Swipe AI Interview Assistant Backend")

# Allow CORS
# Development: allow all origins
# NOTE: Using a wildcard origin with credentials is not allowed by browsers
# (Access-Control-Allow-Origin cannot be '*' when Access-Control-Allow-Credentials is true).
# If you don't need credentials (cookies, HTTP auth), the simplest is:

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all origins
    allow_credentials=False,     # must be False when allow_origins=['*']
    allow_methods=["*"],       # allow all methods (POST, GET, etc.)
    allow_headers=["*"],       # allow all headers
)

# Alternative (allows credentials and echoes the request Origin):
# Uncomment if you need to allow credentials from any origin (use with caution):
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origin_regex=r".*",   # match any origin
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(candidate.router, prefix="/api/candidate", tags=["candidate"])
app.include_router(interview.router, prefix="/api/interview", tags=["interview"])

@app.get("/")
def root():
    return {"message": "Backend is running!"}
