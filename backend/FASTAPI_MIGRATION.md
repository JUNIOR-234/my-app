# FastAPI Migration Guide

This guide explains how to migrate from Django Ninja to FastAPI for the backend API.

## What Changed

### Before (Django Ninja)
- Framework: Django + Django Ninja
- ORM: Django ORM
- Entry point: `manage.py`
- Server: Django development server

### After (FastAPI)
- Framework: FastAPI
- ORM: SQLAlchemy
- Entry point: `main.py`
- Server: Uvicorn

## File Structure

```
backend/
├── main.py                 # FastAPI application with all endpoints
├── database.py             # SQLAlchemy database configuration
├── models_sqlalchemy.py    # SQLAlchemy ORM models (replaces chat/models.py)
├── schemas.py              # Pydantic request/response schemas
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── startup.sh              # Shell script to start the server
├── .env                    # Environment variables (unchanged)
├── db.sqlite3              # Database file (compatible with both Django and FastAPI)
└── chat/
    ├── ai_engine.py        # AI orchestration logic (unchanged)
    ├── utils.py            # Utility functions (unchanged)
    └── ... (other files)
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Server

**Option A: Using the startup script**
```bash
chmod +x startup.sh
./startup.sh
```

**Option B: Direct uvicorn command**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the API

- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## API Endpoints

All endpoints remain the same:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/session` | Initialize anonymous session |
| GET | `/history/{token}/{agent_id}` | Get chat history for a session |
| POST | `/execute/{token}` | Execute the agent pipeline |

## Database Migration

### From Django ORM to SQLAlchemy

The SQLAlchemy models in `models_sqlalchemy.py` are compatible with the existing SQLite database created by Django. No database migration is required - the same `db.sqlite3` file will work with both.

**Key mappings:**
- Django `ForeignKey` → SQLAlchemy `ForeignKey`
- Django `models.DateTimeField` → SQLAlchemy `DateTime`
- Django `models.CharField` → SQLAlchemy `String`
- Django `models.TextField` → SQLAlchemy `Text`
- Django `models.URLField` → SQLAlchemy `String`

## Environment Variables

The `.env` file remains the same. FastAPI will automatically load variables via `config.py`:

```env
DEBUG=True
GEMINI_API_KEY=...
ELEVENLABS_API_KEY=...
PERSONAL_PHONE_NUMBER=...
TWILIO_ACCOUNT_SID=...
RESEND_API_KEY=...
```

## Differences and Considerations

### 1. Request/Response Validation
- Django Ninja: Uses `@api.post(response=Schema)`
- FastAPI: Uses Pydantic models and type hints

### 2. Error Handling
- Django Ninja: Uses `get_object_or_404`
- FastAPI: Raises `HTTPException` with appropriate status codes

### 3. Database Sessions
- Django: Uses ORM `objects.create()` implicitly manages transactions
- FastAPI: Must explicitly create sessions and commit transactions

### 4. CORS Configuration
- Django: Configured in `INSTALLED_APPS`
- FastAPI: Added as middleware in `main.py`

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'django'"

**Solution**: You can now remove Django from your Python environment. FastAPI doesn't depend on Django.

### Issue: Database locked error

**Solution**: Ensure you're using SQLite with `check_same_thread=False` (already set in `database.py`).

### Issue: API endpoints not working

**Solution**: 
1. Check the FastAPI docs at http://localhost:8000/docs
2. Verify environment variables in `.env`
3. Check logs in the terminal running the server

## Next Steps

1. **Test all endpoints** using the Swagger docs at `/docs`
2. **Update frontend** to ensure API calls still work (URLs remain the same)
3. **Remove Django files** once fully migrated:
   - `manage.py` (old Django management)
   - `core/` directory (Django config)
   - `chat/models.py` (old Django models - keep logic but use SQLAlchemy)

4. **Add Alembic** for database migrations (optional but recommended for production)

## Production Deployment

For production, use a production-grade ASGI server:

```bash
# Using Gunicorn with Uvicorn workers
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

Or use containers:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
