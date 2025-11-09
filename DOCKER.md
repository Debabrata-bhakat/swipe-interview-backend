# Docker Setup Guide

## Files Created

1. **Dockerfile** - Multi-stage Python 3.12 image with FastAPI
2. **docker-compose.yml** - Development environment with hot reload
3. **.dockerignore** - Optimizes build by excluding unnecessary files

## Quick Start

### Development (with hot reload)
```powershell
docker-compose up
```
Backend will be available at `http://localhost:8000`

### Production Build
```powershell
docker build -t swipe-interview-backend .
docker run -p 8000:8000 swipe-interview-backend
```

## Common Commands

```powershell
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild after code changes
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Execute commands inside container
docker-compose exec backend python -m pytest
docker-compose exec backend python -c "from app import models; print(models)"

# Clean up everything
docker-compose down -v  # Remove volumes too
```

## Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

The docker-compose.yml will automatically load these.

### Database Persistence
SQLite database is mounted as a volume:
```yaml
volumes:
  - ./swipe_interview.db:/app/swipe_interview.db
```

To reset the database:
```powershell
docker-compose down
Remove-Item swipe_interview.db
docker-compose up
```

## Dockerfile Highlights

- **Base Image**: Python 3.12 slim (smaller size)
- **Working Directory**: `/app`
- **Port**: 8000 (exposed)
- **Health Check**: Pings root endpoint every 30s
- **Production CMD**: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Development Override**: Uses `--reload` flag in docker-compose

## Hot Reload in Docker

The docker-compose setup mounts your local `app/` directory:
```yaml
volumes:
  - ./app:/app/app
```

This means changes to Python files will automatically reload the server (just like running locally with `--reload`).

## Troubleshooting

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 on host
```

### Database Permission Issues
```powershell
# Ensure database file is writable
icacls swipe_interview.db /grant Everyone:F
```

### Image Build Fails
```powershell
# Clear Docker cache
docker builder prune

# Rebuild without cache
docker-compose build --no-cache
```

### Container Exits Immediately
```powershell
# Check logs
docker-compose logs backend

# Common issues:
# 1. Syntax error in Python code
# 2. Missing environment variables
# 3. Port conflict
```

## Next Steps

1. Consider adding PostgreSQL service in docker-compose for production-like environment
2. Add Redis for caching/session management
3. Create separate `Dockerfile.prod` for production optimizations
4. Set up multi-stage builds to reduce image size
