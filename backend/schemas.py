from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SessionOut(BaseModel):
    token: str
    
    class Config:
        from_attributes = True

class MessageIn(BaseModel):
    agent_id: str
    text: str

class MessageOut(BaseModel):
    id: int
    agent_id: str
    sender: str
    text: str
    audio_url: Optional[str] = None
    timestamp: str
    
    class Config:
        from_attributes = True
