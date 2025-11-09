# AI Development Instructions for Swipe Interview Assistant

## Project Overview

Swipe Interview Assistant is a full-stack application that automates technical interviews:
- **Backend**: FastAPI + SQLAlchemy + SQLite (JWT auth, interview orchestration)
- **Frontend**: React + Vite + Ant Design (interview UI, candidate portal)

## Architecture & Data Flow

### Core Interview Flow
1. Candidate signs up  JWT token issued (`app/routers/auth.py`)
2. Resume uploaded  Text extracted via PyPDF2/python-docx (`app/routers/candidate.py`)
3. Interview started  First question generated from static bank (`app/routers/interview.py`)
4. Answer submitted  Score evaluated, next question generated (2 Easy  2 Medium  2 Hard)
5. 6 questions complete  Interview marked "completed" with total score

### Critical State Management
**Backend**: Interview Q&A pairs stored in JSON column (`Interview.qa_pairs`). Must use `flag_modified(interview, "qa_pairs")` after mutating list to trigger SQLAlchemy updates.

**Frontend**: Interview state persisted to `localStorage` (key: `swipe_interview_state`) for resume capability. Timer state saved on every tick to survive page refreshes.

### Database Schema (`app/models.py`)
```python
Candidate: id, email (unique), name, phone, hashed_password, resume_text, created_at
Interview: id, candidate_id (FK), status ('in_progress'|'completed'), score, summary, qa_pairs (JSON)
```

Relationship: `Candidate.interviews` (1-to-many). No cascade deletes configured.

## Development Patterns

### 1. Authentication
- JWT tokens created with `jose` library (`app/auth.py`)
- Tokens stored in `localStorage.access_token` (frontend)
- All protected routes use `get_current_candidate` dependency (`app/routers/candidate.py`)
- **IMPORTANT**: `SECRET_KEY` hardcoded as "YOUR_SECRET_KEY" in both `app/auth.py` and `app/routers/candidate.py` - must match or auth breaks

### 2. SQLAlchemy JSON Column Gotcha
```python
# WRONG - won't persist changes
interview.qa_pairs.append(new_q)

# RIGHT - must reassign + flag
interview.qa_pairs = list(interview.qa_pairs)  # or interview.qa_pairs.append(new_q)
flag_modified(interview, "qa_pairs")
```

### 3. CORS Configuration (`app/main.py`)
```python
allow_origins=["*"]  # All origins allowed
allow_credentials=False  # Must be False when origins is "*"
```
For production: switch to `allow_origin_regex` with specific origins + `allow_credentials=True`.

### 4. Frontend API Client (`src/api/axios.js`)
```javascript
baseURL: "http://localhost:8000/api"
// Auto-injects Bearer token via interceptor
```

### 5. Question Difficulty Timing (Frontend Convention)
```javascript
Easy: 20s, Medium: 60s, Hard: 120s
// Timer implemented in Interviewee.jsx with countdown via setInterval
```

## Common Development Tasks

### Start Development Servers

**Option 1: Docker (Recommended)**
```powershell
# Start with hot reload
cd swipe-interview-backend
docker-compose up

# Rebuild after dependency changes
docker-compose up --build

# Run in detached mode
docker-compose up -d

# Stop containers
docker-compose down
```

**Option 2: Local Python** (PowerShell):
```powershell
cd swipe-interview-backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
API docs: `http://localhost:8000/docs`

**Frontend** (PowerShell):
```powershell
cd swipe-interview-frontend
npm install
npm run dev
```
Dev server: `http://localhost:5173` (default Vite port)

### Database Management
- SQLite file: `./swipe_interview.db` (auto-created on first run)
- Migrations: Not configured (using `Base.metadata.create_all` - no Alembic despite being in requirements.txt)
- Reset DB: Delete `swipe_interview.db` and restart backend
- **Docker**: Database persisted via volume mount in `docker-compose.yml`

### Docker Commands
```powershell
# Build image manually
docker build -t swipe-interview-backend .

# Run container (production mode, no reload)
docker run -p 8000:8000 swipe-interview-backend

# Run with hot reload (development)
docker run -p 8000:8000 -v ${PWD}/app:/app/app swipe-interview-backend `
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Using docker-compose (preferred)
docker-compose up --build  # Build and start
docker-compose logs -f     # View logs
docker-compose exec backend python -c "from app.database import engine; print(engine)"
```

### Resume Upload Flow
1. Frontend sends `multipart/form-data` with file
2. Backend checks extension (`.pdf` or `.docx`)
3. Text extracted using PyPDF2 (PDFs) or python-docx (Word)
4. `Candidate.resume_text` updated (full text stored, no file saved)

## Key Files Reference

**Backend**:
- `app/main.py`: CORS config, router registration, DB table creation
- `app/routers/interview.py`: Interview state machine (start/answer/status endpoints)
- `app/utils/ai_utils.py`: Static question banks (EASY/MEDIUM/HARD_QUESTIONS) + random selection
- `app/auth.py`: Password hashing (bcrypt), JWT creation (jose)

**Frontend**:
- `src/pages/Interviewee.jsx`: Main interview UI with timer, state persistence logic
- `src/api/axios.js`: Axios instance with auth interceptor

## Anti-Patterns to Avoid

1. **Don't mutate SQLAlchemy JSON columns in-place** - always use `flag_modified()`
2. **Don't assume `.env` file exists** - SECRET_KEY hardcoded (not using python-dotenv despite being installed)
3. **Don't expect migrations** - schema changes require manual DB reset or raw SQL
4. **Don't rely on AI question generation** - `ai_utils.py` uses static banks despite langchain/openai in requirements

## Work in Progress

- **Interviewer Dashboard**: Stub component exists (`InterviewerDashboard.jsx`) but not wired to backend
- **AI Question Generation**: Infrastructure present (langchain-anthropic, openai-agents in requirements) but not integrated
- **Tests**: No test files exist (pytest not configured)

## Debugging Tips

**401 Unauthorized**: Check SECRET_KEY consistency across `app/auth.py` and `app/routers/candidate.py`

**Interview state desync**: Check `flag_modified()` usage when updating `qa_pairs`

**CORS errors**: Verify frontend calls `http://localhost:8000/api` (not `http://127.0.0.1`)

**Timer not resuming**: Inspect `localStorage.swipe_interview_state` - should contain `{timer, answer, interviewStarted}`
