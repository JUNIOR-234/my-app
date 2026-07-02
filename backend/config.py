from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Core settings
    debug: bool = True
    api_title: str = "SaaS Multi-Agent Communication API Hub"
    api_version: str = "1.0.0"
    
    # Database
    database_url: str = "sqlite:///./db.sqlite3"
    
    # AI APIs
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    elevenlabs_voice_id: str = os.getenv("ELEVENLABS_VOICE_ID", "")
    
    # Notifications
    personal_phone_number: str = os.getenv("PERSONAL_PHONE_NUMBER", "")
    personal_email: str = os.getenv("PERSONAL_EMAIL", "")
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    resend_api_key: str = os.getenv("RESEND_API_KEY", "")
    
    # CORS
    allowed_origins: list = ["*"]  # Update in production
    
    class Config:
        env_file = ".env"

settings = Settings()
