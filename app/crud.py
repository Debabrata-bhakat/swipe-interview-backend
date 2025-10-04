from sqlalchemy.orm import Session
from app import models, auth

def create_candidate(db: Session, candidate):
    hashed_pwd = auth.hash_password(candidate.password)
    db_candidate = models.Candidate(
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        hashed_password=hashed_pwd
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

def get_candidate_by_email(db: Session, email: str):
    return db.query(models.Candidate).filter(models.Candidate.email == email).first()
