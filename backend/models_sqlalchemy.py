import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import UUID
from database import Base

class GuestSession(Base):
    __tablename__ = "chat_guestsession"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(UUID(as_uuid=False), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)  # Supports IPv6
    user_agent = Column(Text, nullable=True)
    
    # Relationship
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __str__(self):
        return f"Guest_{self.token[:8]}"

class ChatMessage(Base):
    __tablename__ = "chat_chatmessage"
    
    SENDER_CHOICES = [
        ('user', 'Employer/Guest'),
        ('system', 'System Pipeline'),
        ('agent', 'AI Agent Workhorse'),
    ]
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_guestsession.id"), index=True)
    agent_id = Column(String(50))  # 'direct', 'cv', 'audit', 'bio', 'voice'
    sender = Column(String(10))  # 'user', 'system', 'agent'
    text = Column(Text)
    audio_url = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    session = relationship("GuestSession", back_populates="messages")
    
    def __str__(self):
        return f"[{self.agent_id}] {self.sender}: {self.text[:30]}"
