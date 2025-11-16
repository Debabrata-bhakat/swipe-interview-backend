# Supabase PostgreSQL Setup Guide

## Step 1: Get Supabase Connection Details

1. Go to your Supabase project dashboard: https://app.supabase.com
2. Click on your project
3. Go to **Settings** > **Database**
4. Scroll down to **Connection Info** or **Connection Pooling**
5. Copy the connection details

## Step 2: Create `.env` File

Create a `.env` file in the backend root directory:

```bash
# Copy the example file
cp .env.example .env
```

Then update with your Supabase credentials:

```env
# Supabase PostgreSQL Database Configuration
DB_USER=postgres
DB_PASSWORD=your_actual_password_here
DB_HOST=db.xxxxxxxxxxxxx.supabase.co
DB_PORT=5432
DB_NAME=postgres

# JWT Secret Key (generate a strong one)
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Finding Your Supabase Connection Details:

- **DB_HOST**: Found in "Host" field (e.g., `db.abcdefghijk.supabase.co`)
- **DB_USER**: Usually `postgres`
- **DB_PASSWORD**: The password you set when creating your Supabase project
- **DB_PORT**: Usually `5432` (or `6543` for connection pooling)
- **DB_NAME**: Usually `postgres`

### Alternative: Use Connection String

If you prefer, you can also use the connection string format. Supabase provides this in the "URI" field:
```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

## Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

This will install `psycopg2-binary` for PostgreSQL support.

## Step 4: Initialize Database Tables

Run the initialization script to create tables:

```powershell
python init_db.py
```

You should see:
```
Creating database tables...
Database tables created successfully!
Connected to PostgreSQL: PostgreSQL 15.x.x...
```

## Step 5: Verify Connection

Test the connection manually:

```powershell
python -c "from app.database import engine; print(engine.connect())"
```

## Step 6: Run the Application

```powershell
# Local development
python -m uvicorn app.main:app --reload

# Or with Docker
docker-compose up --build
```

## Step 7: Deploy to Cloud Run

When deploying to Cloud Run, set environment variables:

```powershell
gcloud run deploy swipe-interview-backend \
  --image asia-south1-docker.pkg.dev/YOUR_PROJECT/swipe-interview/backend:latest \
  --platform managed \
  --region asia-south1 \
  --set-env-vars="DB_USER=postgres,DB_PASSWORD=your_password,DB_HOST=db.xxxxx.supabase.co,DB_PORT=5432,DB_NAME=postgres,SECRET_KEY=your_secret_key" \
  --allow-unauthenticated
```

Or use Secret Manager (recommended):

```powershell
# Create secrets
echo -n "your_db_password" | gcloud secrets create db-password --data-file=-
echo -n "your_secret_key" | gcloud secrets create jwt-secret-key --data-file=-

# Deploy with secrets
gcloud run deploy swipe-interview-backend \
  --image asia-south1-docker.pkg.dev/YOUR_PROJECT/swipe-interview/backend:latest \
  --set-secrets="DB_PASSWORD=db-password:latest,SECRET_KEY=jwt-secret-key:latest" \
  --set-env-vars="DB_USER=postgres,DB_HOST=db.xxxxx.supabase.co,DB_PORT=5432,DB_NAME=postgres" \
  --region asia-south1 \
  --allow-unauthenticated
```

## Troubleshooting

### Connection Refused
- Check if your IP is allowed in Supabase (Settings > Database > Connection Pooling)
- Supabase may require connection pooling for some connections
- Try using port `6543` instead of `5432`

### SSL Certificate Error
If you get SSL errors, update `app/database.py`:

```python
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
```

### Pool Connection Timeout
If using connection pooling (port 6543):

```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
)
```

## Migration from SQLite

If you have existing data in SQLite that you want to migrate:

1. Export data from SQLite:
```python
# export_data.py
import sqlite3
import json

conn = sqlite3.connect('swipe_interview.db')
cursor = conn.cursor()

# Export candidates
cursor.execute("SELECT * FROM candidates")
candidates = cursor.fetchall()
with open('candidates.json', 'w') as f:
    json.dump(candidates, f)

# Export interviews
cursor.execute("SELECT * FROM interviews")
interviews = cursor.fetchall()
with open('interviews.json', 'w') as f:
    json.dump(interviews, f)
```

2. Import to PostgreSQL using a migration script (create this as needed)

## Supabase-Specific Features

### Enable Row Level Security (RLS)
For production, enable RLS in Supabase dashboard:

```sql
-- In Supabase SQL Editor
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;
```

### Create Policies (Optional)
```sql
-- Allow authenticated users to read their own data
CREATE POLICY "Users can view own candidate data"
ON candidates FOR SELECT
USING (auth.uid() = id::text);
```

## Success! 🎉

Your application is now using Supabase PostgreSQL instead of SQLite!
