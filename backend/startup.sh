#!/bin/bash
# FastAPI Backend Startup Script

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Create and run database migrations (if using Alembic in the future)
# For now, tables are created automatically by SQLAlchemy on app startup

# Start the FastAPI server
echo "🚀 Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
