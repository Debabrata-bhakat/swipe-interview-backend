from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from app import models, schemas, database
from app.utils.ai_utils import generate_question, evaluate_answer
from app.routers.candidate import get_current_candidate  # import auth dependency

router = APIRouter()

@router.post("/start")
def start_interview(
    db: Session = Depends(database.get_db),
    candidate: models.Candidate = Depends(get_current_candidate)  # add auth
):

    interview = models.Interview(candidate_id=candidate.id, qa_pairs=[])
    first_q = generate_question(0)
    interview.qa_pairs.append(first_q)

    db.add(interview)
    db.commit()
    db.refresh(interview)

    return {"interview_id": interview.id, "next_question": first_q}

@router.post("/answer")
def submit_answer(
    req: schemas.AnswerRequest,
    db: Session = Depends(database.get_db),
    candidate: models.Candidate = Depends(get_current_candidate)
):
    answer = req.answer
    # Find the latest active interview for the candidate
    interview = (
        db.query(models.Interview)
        .filter(models.Interview.candidate_id == candidate.id, models.Interview.status != "completed")
        .order_by(models.Interview.id.desc())
        .first()
    )
    if not interview:
        raise HTTPException(status_code=404, detail="Active interview not found")

    qa_pairs = interview.qa_pairs
    current_index = len([q for q in qa_pairs if q.get("answer")])  # count answered
    print(f"interview: {interview}")
    print(f"current_index: {current_index}, len(qa_pairs): {len(qa_pairs)}")
    print(f"qa pairs: {qa_pairs}")
    if current_index >= len(qa_pairs):
        current_index = len(qa_pairs) - 1

    qa_pairs[current_index]["answer"] = answer
    qa_pairs[current_index]["score"] = evaluate_answer(answer, qa_pairs[current_index]["difficulty"])

    interview.qa_pairs = list(qa_pairs)
    flag_modified(interview, "qa_pairs")  # <-- explicitly mark as modified

    # Finalize if 6 questions are present
    if len(qa_pairs) == 6:
        if all(q.get("answer") for q in qa_pairs):
            interview.status = "completed"
            interview.score = sum(q["score"] for q in qa_pairs)
            interview.summary = f"Candidate performed well with total score {interview.score}."
            flag_modified(interview, "qa_pairs")  # mark again if changed
            db.commit()
            db.refresh(interview)
            return {"message": "Interview completed", "score": interview.score, "summary": interview.summary}
        else:
            flag_modified(interview, "qa_pairs")
            db.commit()
            db.refresh(interview)
            return {"message": "Interview completed"}

    # Otherwise, generate next question only if less than 6
    next_index = len(qa_pairs)
    if next_index < 6:
        next_q = generate_question(next_index)
        qa_pairs.append(next_q)
        interview.qa_pairs = list(qa_pairs)
        flag_modified(interview, "qa_pairs")
        print(f"inside next question block, interview: {interview}")
        db.commit()
        db.refresh(interview)
        return {"next_question": next_q}

    return {"message": "Interview completed"}
