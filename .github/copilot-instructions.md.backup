# AI Development Instructions for Swipe Interview Assistant

This document provides key information for AI agents working with the Swipe Interview Assistant codebase.

## Project Overview

Swipe Interview Assistant is a full-stack application that automates technical interviews:
- Backend: FastAPI + SQLite (JWT auth, interview logic)
- Frontend: React + Vite (Ant Design components)

## Architecture

### Backend (`swipe-interview-backend/`)

Key components:
- `app/main.py`: FastAPI application setup and middleware
- `app/models.py`: SQLAlchemy models (Candidate, Interview)
- `app/schemas.py`: Pydantic validation schemas
- `app/auth.py`: JWT authentication utilities
- `app/crud.py`: Database operations
- `app/routers/`: API endpoints organized by domain
  - `auth.py`: Authentication routes
  - `candidate.py`: Profile management
  - `interview.py`: Interview session handling

### Frontend (`swipe-interview-frontend/`)

Key components:
- `src/api/axios.js`: Centralized API client with auth interceptors
- `src/pages/`: React components by route
  - `Login.jsx`, `Signup.jsx`: Auth flows
  - `Interviewee.jsx`: Main interview interface
  - `InterviewerDashboard.jsx`: Admin view (WIP)

## Development Patterns

### 1. Authentication Flow
- JWT tokens stored in localStorage
- Token automatically added to requests via axios interceptor
- Protected routes require valid token

Example auth header setup:
```javascript
// src/api/axios.js
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

### 2. Interview Session Management
- Questions progress from Easy → Medium → Hard
- Each difficulty has predefined time limits:
  - Easy: 20s
  - Medium: 60s
  - Hard: 120s
- Interview state persisted in localStorage for resume capability

### 3. Data Models

The core entities are:

```python
# Backend models (app/models.py)
class Candidate:
    id: int
    email: str  # unique
    name: str
    phone: str
    resume_text: str
    interviews: List[Interview]

class Interview:
    id: int
    candidate_id: int
    status: str  # 'in_progress' | 'completed'
    score: int
    summary: str
    qa_pairs: List[dict]  # JSON field storing Q&A history
```

## Common Tasks

### Setting Up Development Environment

1. Backend:
```bash
cd swipe-interview-backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. Frontend:
```bash
cd swipe-interview-frontend
npm install
npm run dev
```

### Running Tests (TBD)
Test infrastructure not yet set up. When adding tests, follow these conventions:
- Backend: pytest in `tests/` directory
- Frontend: Jest + React Testing Library

## API Examples

See comprehensive API documentation with request/response examples in `swipe-interview-backend/README.md`.

## Work in Progress

1. Interviewer Dashboard
   - Currently a placeholder component
   - Will show interview results and candidate management

2. AI Question Generation
   - Currently uses static question bank
   - Plan to integrate with LLM API for dynamic questions

## Contributing Guidelines

1. Follow existing patterns for new features:
   - Group backend routes by domain in `app/routers/`
   - Frontend components in appropriate `src/pages/` or `src/components/`
   - Use Ant Design components for UI consistency

2. Data validation:
   - Backend: Define Pydantic schemas in `app/schemas.py`
   - Frontend: Form validation using Ant Design Form components

3. Error handling:
   - Backend: Use FastAPI's HTTPException with appropriate status codes
   - Frontend: Use Ant Design message system for user feedback