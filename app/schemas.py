from pydantic import BaseModel, EmailStr
from typing import Optional

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
