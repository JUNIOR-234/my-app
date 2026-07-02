import traceback
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db, engine, Base
from models_sqlalchemy import GuestSession, ChatMessage
from schemas import SessionOut, MessageIn, MessageOut
from chat.utils import send_employer_alert
from chat.ai_engine import run_agent_pipeline, generate_elevenlabs_voice

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="SaaS Multi-Agent Communication API Hub",
    version="1.0.0",
    description="FastAPI backend for multi-agent communication system"
)

# CORS setup (if needed for frontend)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API ENDPOINTS ---

@app.get("/session", response_model=SessionOut)
def initialize_anonymous_handshake(request: Request, db: Session = Depends(get_db)):
    """Fires a silent session token back to the React UI layout on page-load."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    session = GuestSession(ip_address=ip_address, user_agent=user_agent)
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {"token": session.token}

@app.get("/history/{token}/{agent_id}", response_model=List[MessageOut])
def get_chat_history(token: str, agent_id: str, db: Session = Depends(get_db)):
    """Fetches text streaming sequence logs for our simple long-polling polling sync setup."""
    session = db.query(GuestSession).filter(GuestSession.token == token).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id,
        ChatMessage.agent_id == agent_id
    ).all()
    
    return [
        {
            "id": m.id,
            "agent_id": m.agent_id,
            "sender": m.sender,
            "text": m.text,
            "audio_url": m.audio_url,
            "timestamp": m.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for m in messages
    ]

@app.post("/execute/{token}", response_model=MessageOut)
def execute_system_pipeline(
    token: str, 
    payload: MessageIn, 
    db: Session = Depends(get_db)
):
    """Ingests employer requests, stores logs, runs AI tools, and fires hardware notifications."""
    session = db.query(GuestSession).filter(GuestSession.token == token).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 1. Save the incoming employer text log
    user_msg = ChatMessage(
        session_id=session.id,
        agent_id=payload.agent_id,
        sender='user',
        text=payload.text
    )
    db.add(user_msg)
    db.commit()
    
    # 2. Check if routing directly to developer or an agent
    if payload.agent_id == "direct":
        # Immediate notification trigger
        send_employer_alert(session.token, payload.agent_id, payload.text)
        
        agent_response_text = "Your direct message has bypassed the pipeline and hit the engineer's phone via instant Twilio relay. He will review your message immediately."
        system_response = ChatMessage(
            session_id=session.id,
            agent_id=payload.agent_id,
            sender='agent',
            text=agent_response_text
        )
        db.add(system_response)
        db.commit()
        db.refresh(system_response)
    else:
        audio_link = None
        try:
            # Run CrewAI Multi-Agent processing task blocks
            agent_response_text = run_agent_pipeline(payload.agent_id, payload.text)
            
            # Check if the specific text-to-speech engine profile was requested
            if payload.agent_id == "voice":
                audio_link = generate_elevenlabs_voice(agent_response_text)
        except Exception as exc:
            error_message = (
                "⚠️ Execution error. Check API server logging configuration. "
                "The backend pipeline failed to complete."
            )
            print("🔴 Backend pipeline failure:", exc)
            traceback.print_exc()

            system_response = ChatMessage(
                session_id=session.id,
                agent_id=payload.agent_id,
                sender='system',
                text=error_message,
                audio_url=None
            )
            db.add(system_response)
            db.commit()
            db.refresh(system_response)

            return {
                "id": system_response.id,
                "agent_id": system_response.agent_id,
                "sender": system_response.sender,
                "text": system_response.text,
                "audio_url": system_response.audio_url,
                "timestamp": system_response.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        system_response = ChatMessage(
            session_id=session.id,
            agent_id=payload.agent_id,
            sender='agent',
            text=agent_response_text,
            audio_url=audio_link
        )
        db.add(system_response)
        db.commit()
        db.refresh(system_response)

    return {
        "id": system_response.id,
        "agent_id": system_response.agent_id,
        "sender": system_response.sender,
        "text": system_response.text,
        "audio_url": system_response.audio_url,
        "timestamp": system_response.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "SaaS Multi-Agent Communication API Hub is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
