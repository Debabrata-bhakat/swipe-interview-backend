from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import database, models

router = APIRouter()


def get_db():
    return database.get_db()


@router.get("/candidates")
def list_candidates(db: Session = Depends(database.get_db)):
    candidates = db.query(models.Candidate).all()
    out = []
    for c in candidates:
        # find best or latest interview score
        score = 0
        if c.interviews:
            # pick latest interview with a score
            interviews_with_score = [iv for iv in c.interviews if iv.score is not None]
            if interviews_with_score:
                # use latest by id
                interviews_with_score.sort(key=lambda x: x.id, reverse=True)
                score = interviews_with_score[0].score or 0
        out.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "score": score,
        })
    # sort by score desc
    out.sort(key=lambda x: x["score"] or 0, reverse=True)
    return out


@router.get("/candidate/{candidate_id}")
def get_candidate(candidate_id: int, db: Session = Depends(database.get_db)):
    c = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    score = 0
    latest_summary = None
    if c.interviews:
        interviews_with_score = [iv for iv in c.interviews if iv.score is not None]
        if interviews_with_score:
            interviews_with_score.sort(key=lambda x: x.id, reverse=True)
            score = interviews_with_score[0].score or 0
            latest_summary = interviews_with_score[0].summary

    return {
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "phone": c.phone,
        "resume_text": c.resume_text,
        "score": score,
        "latest_summary": latest_summary,
    }


@router.get("/candidate/{candidate_id}/chat")
def get_candidate_chat(candidate_id: int, db: Session = Depends(database.get_db)):
    c = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    # pick latest interview
    if not c.interviews:
        return []
    iv = sorted(c.interviews, key=lambda x: x.id, reverse=True)[0]
    messages = []
    for qa in iv.qa_pairs or []:
        # question from system/ai
        messages.append({
            "from": "ai",
            "message": qa.get("question"),
        })
        if qa.get("answer") is not None:
            messages.append({
                "from": "candidate",
                "message": qa.get("answer"),
            })
    return messages


@router.get("/candidate/{candidate_id}/summary")
def get_candidate_summary(candidate_id: int, db: Session = Depends(database.get_db)):
    c = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if not c.interviews:
        return {"final_score": None, "summary": None}
    iv = sorted(c.interviews, key=lambda x: x.id, reverse=True)[0]
    return {"final_score": iv.score, "summary": iv.summary}
