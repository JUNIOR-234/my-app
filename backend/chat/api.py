import traceback
from ninja import NinjaAPI, Schema
from django.shortcuts import get_object_or_404
from typing import List
from .models import GuestSession, ChatMessage
from .utils import send_employer_alert
from .ai_engine import run_agent_pipeline, generate_elevenlabs_voice

api = NinjaAPI(title="SaaS Multi-Agent Communication API Hub", version="1.0.0")

# --- PYDANTIC VALIDATION SCHEMAS ---
class SessionOut(Schema):
    token: str

class MessageIn(Schema):
    agent_id: str
    text: str

class MessageOut(Schema):
    id: int
    agent_id: str
    sender: str
    text: str
    audio_url: str = None
    timestamp: str

# --- ASYNC-FRIENDLY API ENDPOINTS ---

@api.get("/session", response=SessionOut)
def initialize_anonymous_handshake(request):
    """Fires a silent session token back to the React UI layout on page-load."""
    session = GuestSession.objects.create(
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )
    return {"token": str(session.token)}

@api.get("/history/{token}/{agent_id}", response=List[MessageOut])
def get_chat_history(request, token: str, agent_id: str):
    """Fetches text streaming sequence logs for our simple long-polling polling sync setup."""
    session = get_object_or_404(GuestSession, token=token)
    messages = ChatMessage.objects.filter(session=session, agent_id=agent_id)
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

@api.post("/execute/{token}", response=MessageOut)
def execute_system_pipeline(request, token: str, payload: MessageIn):
    """Ingests employer requests, stores logs, runs AI tools, and fires hardware notifications."""
    session = get_object_or_404(GuestSession, token=token)
    
    # 1. Save the incoming employer text log
    user_msg = ChatMessage.objects.create(
        session=session, agent_id=payload.agent_id, sender='user', text=payload.text
    )
    
    # 2. Check if routing directly to developer or an agent
    if payload.agent_id == "direct":
        # Immediate notification trigger
        send_employer_alert(session.token, payload.agent_id, payload.text)
        
        agent_response_text = "Your direct message has bypassed the pipeline and hit the engineer's phone via instant Twilio relay. He will review your message immediately."
        system_response = ChatMessage.objects.create(
            session=session, agent_id=payload.agent_id, sender='agent', text=agent_response_text
        )
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

            system_response = ChatMessage.objects.create(
                session=session,
                agent_id=payload.agent_id,
                sender='system',
                text=error_message,
                audio_url=None
            )

            return {
                "id": system_response.id,
                "agent_id": system_response.agent_id,
                "sender": system_response.sender,
                "text": system_response.text,
                "audio_url": system_response.audio_url,
                "timestamp": system_response.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        system_response = ChatMessage.objects.create(
            session=session,
            agent_id=payload.agent_id,
            sender='agent',
            text=agent_response_text,
            audio_url=audio_link
        )

    return {
        "id": system_response.id,
        "agent_id": system_response.agent_id,
        "sender": system_response.sender,
        "text": system_response.text,
        "audio_url": system_response.audio_url,
        "timestamp": system_response.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    }
