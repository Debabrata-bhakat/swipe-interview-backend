from sqlalchemy import JSON, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    resume_text = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
     # Relationships
    interviews = relationship("Interview", back_populates="candidate")

class Interview(Base):
    __tablename__ = "interviews"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    status = Column(String, default="in_progress")  # in_progress | completed
    score = Column(Integer, nullable=True)
    summary = Column(String, nullable=True)
    qa_pairs = Column(JSON, default=list)  # <-- use default=list instead of default=[]

    candidate = relationship("Candidate", back_populates="interviews")

    def __repr__(self):
        return (
            f"<Interview(id={self.id}, candidate_id={self.candidate_id}, "
            f"status='{self.status}', score={self.score}, "
            f"summary='{self.summary}', qa_pairs={self.qa_pairs})>"
        )

