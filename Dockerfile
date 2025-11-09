# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for Python packages
# - gcc, g++: Required for compiling some Python packages
# - libpq-dev: PostgreSQL client library (if needed in future)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Create directory for SQLite database (optional, for volume mounting)
RUN mkdir -p /app/data

# Expose port 8080 for FastAPI
EXPOSE 8080

# Health check to verify the container is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/')" || exit 1

# Run the application
# Note: --reload is removed for production (use it only in development)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

# For development with hot reload, override CMD with:
# docker run -p 8080:8080 -v $(pwd)/app:/app/app <image_name> \
#   python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
