from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app import database, models, schemas
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
import PyPDF2, docx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
SECRET_KEY = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY")

def get_current_candidate(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        candidate = db.query(models.Candidate).filter(models.Candidate.email == email).first()
        if not candidate:
            raise HTTPException(status_code=401, detail="Candidate not found")
        return candidate
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/profile", response_model=schemas.CandidateResponse)
def get_profile(candidate: models.Candidate = Depends(get_current_candidate)):
    return candidate

@router.post("/upload_resume", response_model=schemas.CandidateResponse)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(database.get_db),
                  candidate: models.Candidate = Depends(get_current_candidate)):
    text = ""
    if file.filename.endswith(".pdf"):
        pdf = PyPDF2.PdfReader(file.file)
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    elif file.filename.endswith(".docx"):
        doc = docx.Document(file.file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")

    candidate.resume_text = text
    db.commit()
    db.refresh(candidate)
    return candidate
