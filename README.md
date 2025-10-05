# Swipe AI Interview Assistant Backend

This is the backend service for the Swipe AI Interview Assistant, built with FastAPI and SQLAlchemy.

## Features

- JWT-based authentication and authorization
- Candidate management (signup, login, profile, resume upload)
- Interview session management with AI-generated questions
- SQLite database integration
- Password hashing with bcrypt

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd swipe-interview-backend
    ```

2. Install the required packages:
    ```bash
    pip install -r requirement.txt
    ```

## Environment Setup

Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Project Structure

```
swipe-interview-backend/
├── app/
│   ├── routers/
│   │   ├── auth.py         # Authentication routes
│   │   ├── candidate.py    # Candidate management routes
│   │   └── interview.py    # Interview session routes
│   ├── auth.py             # Authentication utilities
│   ├── crud.py             # Database CRUD operations
│   ├── database.py         # Database configuration
│   ├── main.py             # FastAPI application setup
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic models/schemas
│   └── utils/
│       └── ai_utils.py     # AI question generation and evaluation
├── requirement.txt         # Project dependencies
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register a new candidate
- `POST /api/auth/login` - Login and get access token

### Candidate Management
- `GET /api/candidate/profile` - Get candidate profile (auth required)
- `POST /api/candidate/upload_resume` - Upload resume (auth required)

### Interview Flow
- `POST /api/interview/start` - Start a new interview session (auth required)
- `POST /api/interview/answer` - Submit answer to current interview question (auth required)

> **Note:** All interview endpoints require a Bearer token in the `Authorization` header.

## Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI) is available at `http://localhost:8000/docs`

## Database

The project uses SQLite as the database. The database file `swipe_interview.db` will be created automatically when you first run the application.

## Usage Example

1. **Signup:**  
   `POST /api/auth/signup` with JSON body:
   ```json
   {
     "name": "John Doe",
     "email": "john@example.com",
     "phone": "1234567890",
     "password": "yourpassword"
   }
   ```

2. **Login:**  
   `POST /api/auth/login` with JSON body:
   ```json
   {
     "email": "john@example.com",
     "password": "yourpassword"
   }
   ```
   Response will include an `access_token`.

3. **Authenticated Requests:**  
   Add header:  
   `Authorization: Bearer <access_token>`

4. **Start Interview:**  
   `POST /api/interview/start` (no body needed, just auth header)

5. **Answer Interview Question:**  
   `POST /api/interview/answer` with JSON body:
   ```json
   {
     "answer": "Your answer here"
   }
   ```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Add your license here]
