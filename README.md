# Swipe AI Interview Assistant Backend

This is the backend service for the Swipe AI Interview Assistant, built with FastAPI and SQLAlchemy.

## Features

- User authentication and authorization using JWT tokens
- Candidate management system
- RESTful API endpoints
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
│   │   └── candidate.py    # Candidate management routes
│   ├── auth.py            # Authentication utilities
│   ├── crud.py           # Database CRUD operations
│   ├── database.py       # Database configuration
│   ├── main.py          # FastAPI application setup
│   ├── models.py        # SQLAlchemy models
│   └── schemas.py       # Pydantic models/schemas
├── requirement.txt      # Project dependencies
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/token` - Get access token
- `GET /api/auth/me` - Get current user info

### Candidate Management
- `POST /api/candidate/` - Create new candidate
- `GET /api/candidate/me` - Get candidate profile

## Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation (provided by Swagger UI) will be available at `http://localhost:8000/docs`

## Database

The project uses SQLite as the database. The database file `swipe_interview.db` will be created automatically when you first run the application.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Add your license here]
