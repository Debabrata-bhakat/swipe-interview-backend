from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any

class CandidateCreate(BaseModel):
    name: Optional[str]
    email: EmailStr
    phone: Optional[str]
    password: str

class CandidateLogin(BaseModel):
    email: EmailStr
    password: str

class CandidateResponse(BaseModel):
    id: int
    name: Optional[str]
    email: EmailStr
    phone: Optional[str]
    resume_text: Optional[str]

    class Config:
        orm_mode = True

class QAItem(BaseModel):
    question: str
    answer: Optional[str] = None
    difficulty: str
    score: Optional[int] = None

class InterviewBase(BaseModel):
    candidate_id: int
    status: str = "in_progress"
    qa_pairs: List[QAItem] = []
    score: Optional[int] = None
    summary: Optional[str] = None

class InterviewCreate(InterviewBase):
    pass

class InterviewResponse(InterviewBase):
    id: int

    class Config:
        orm_mode = True

class AnswerRequest(BaseModel):
    answer: str
