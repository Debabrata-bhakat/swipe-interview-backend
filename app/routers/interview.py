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
    
    # Find all questions that have been attempted (have an 'answer' field)
    attempted_indices = [i for i, q in enumerate(qa_pairs) if "answer" in q]
    
    # If we have attempted questions, current_question should be the next one
    # If no questions attempted, start at 0
    current_question = (max(attempted_indices) + 1) if attempted_indices else 0
    
    # Don't exceed the last question index
    if current_question >= len(qa_pairs):
        current_question = len(qa_pairs) - 1
    
    total_questions = TOTAL_QUESTIONS
    
    print(f"Status check - Attempted questions: {attempted_indices}")
    print(f"Status check - Next question to attempt: {current_question}")
    
    print(f"Status check - Total questions in qa_pairs: {len(qa_pairs)}")
    print(f"Status check - Questions attempted (including empty): {current_question}")
    print(f"Status check - Current question index: {current_question}")
    
    print(f"Status check - Questions with any answer: {[i for i, q in enumerate(qa_pairs) if 'answer' in q]}")
    print(f"Status check - Questions with non-empty answers: {[i for i, q in enumerate(qa_pairs) if q.get('answer', '').strip()]}")
    print(f"Status check - Current question index: {current_question}")

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
    # Find the first question without any answer attempt
    current_index = next((i for i, q in enumerate(qa_pairs) if "answer" not in q), len(qa_pairs) - 1)
    
    print(f"Submitting answer for question {current_index}")
    print(f"Current qa_pairs state: {qa_pairs}")
    
    # Record the answer attempt
    qa_pairs[current_index]["answer"] = answer
    if answer.strip():
        qa_pairs[current_index]["score"] = evaluate_answer(answer, qa_pairs[current_index]["difficulty"])
    else:
        qa_pairs[current_index]["score"] = 0

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
    answered_count = len([q for q in qa_pairs if q.get("answer", "").strip()])
    return {
        "message": "Continue answering",
        "questions_done": answered_count,
        "total_questions": total_questions,
    }
