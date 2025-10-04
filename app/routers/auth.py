from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app import schemas, crud, database, auth

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@router.post("/signup", response_model=schemas.CandidateResponse)
def signup(candidate: schemas.CandidateCreate, db: Session = Depends(database.get_db)):
    existing = crud.get_candidate_by_email(db, candidate.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_candidate = crud.create_candidate(db, candidate)
    return new_candidate

@router.post("/login")
def login(candidate: schemas.CandidateLogin, db: Session = Depends(database.get_db)):
    db_candidate = crud.get_candidate_by_email(db, candidate.email)
    if not db_candidate or not auth.verify_password(candidate.password, db_candidate.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": db_candidate.email})
    return {"access_token": token, "token_type": "bearer"}
