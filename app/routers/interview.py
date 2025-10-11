from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from app import models, schemas, database
from app.utils.ai_utils import generate_question, evaluate_answer
from app.routers.candidate import get_current_candidate  # import auth dependency

router = APIRouter()
TOTAL_QUESTIONS = 6

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

    # return counts to help the frontend show progress
    return {
        "interview_id": interview.id,
        "next_question": first_q,
        "questions_done": 0,
        "total_questions": TOTAL_QUESTIONS,
    }

@router.get("/status")
def get_interview_status(
    db: Session = Depends(database.get_db),
    candidate: models.Candidate = Depends(get_current_candidate)
):
    interview = (
        db.query(models.Interview)
        .filter(models.Interview.candidate_id == candidate.id)
        .order_by(models.Interview.id.desc())
        .first()
    )
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    qa_pairs = interview.qa_pairs
    # Find the first question that hasn't been answered yet
    current_question = next((i for i, q in enumerate(qa_pairs) 
                           if "answer" not in q or not q["answer"].strip()), 0)
    
    # If all questions are answered, point to the last question
    if all(q.get("answer", "").strip() for q in qa_pairs):
        current_question = len(qa_pairs) - 1
    
    total_questions = TOTAL_QUESTIONS
    
    print(f"Status check - Current question: {current_question}")
    print(f"Status check - Questions with answers: {[i for i, q in enumerate(qa_pairs) if q.get('answer', '').strip()]}")

    return {
        "interview_id": interview.id,
        "status": interview.status,
        "score": interview.score,
        "summary": interview.summary,
        "qa_pairs": qa_pairs,
        "current_question": current_question,
        "total_questions": total_questions,
    }

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

    # compute progress after recording the answer
    questions_done = len(qa_pairs)
    total_questions = TOTAL_QUESTIONS

    # Finalize if 6 questions are present
    if len(qa_pairs) == 6:
        if all(q.get("answer") for q in qa_pairs):
            interview.status = "completed"
            interview.score = sum(q["score"] for q in qa_pairs)
            interview.summary = f"Candidate performed well with total score {interview.score}."
            flag_modified(interview, "qa_pairs")  # mark again if changed
            db.commit()
            db.refresh(interview)
            return {
                "message": "Interview completed",
                "score": interview.score,
                "summary": interview.summary,
                "questions_done": questions_done,
                "total_questions": total_questions,
            }
        else:
            flag_modified(interview, "qa_pairs")
            db.commit()
            db.refresh(interview)
            return {
                "message": "Interview completed",
                "questions_done": questions_done,
                "total_questions": total_questions,
            }

    # Generate next question if needed
    if len(qa_pairs) < total_questions:
        next_q = generate_question(len(qa_pairs))
        qa_pairs.append(next_q)
        interview.qa_pairs = list(qa_pairs)
        flag_modified(interview, "qa_pairs")
        db.commit()
        db.refresh(interview)
        return {
            "next_question": next_q,
            "questions_done": len(qa_pairs) - 1,  # -1 because we just added a new question
            "total_questions": total_questions,
        }

    # If we have all questions but not all answered
    return {
        "message": "Continue answering",
        "questions_done": len(questions_with_answers),
        "total_questions": total_questions,
    }
