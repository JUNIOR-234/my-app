import os
import requests
from crewai import Agent, Task, Crew, Process

# Mock resume data for 1-day isolation. In production, load via file read.
RESUME_DATA = """
Yiga Junior - Fullstack AI Engineer
Tech Stack: React, Django, Django Ninja, CrewAI, PostgreSQL
, Docker, AWS.
Projects:
1. CoreAI Portfolio: Multi-agent interactive system with ElevenLabs synthesis.
2. ThreatScan: Automated Python static code analysis platform.
Location: Based and staying in Kampala, Uganda. Available for worldwide remote contract.
"""

def get_crew_agent(agent_id: str) -> Agent:
    if agent_id == "cv":
        return Agent(
            role="Corporate Talent Acquisition Executive",
            goal="Analyze career history data accurately and summarize background findings for tech recruiters.",
            backstory="You represent the developer. You interpret his tech stack history directly and answer concisely.",
            verbose=False,
            allow_delegation=False
        )
    elif agent_id == "audit":
        return Agent(
            role="Elite Senior Software Architect & Threat Analyst",
            goal="Examine code fragments directly to locate security vulnerabilities, architectural errors, or bugs.",
            backstory="You are a strict security auditor. You output explicit markdown code adjustments and severity ratings.",
            verbose=False,
            allow_delegation=False
        )
    else: # 'bio' or default identity node
        return Agent(
            role="Virtual Office Chief of Staff",
            goal="Provide accurate personal logistics data, contact methods, and location availability.",
            backstory="You manage the engineer's calendar, geographical availability coordinates, and direct access points.",
            verbose=False,
            allow_delegation=False
        )

def run_agent_pipeline(agent_id: str, prompt: str) -> str:
    """Executes the specific CrewAI context run block."""
    worker = get_crew_agent(agent_id)
    
    context_task = Task(
        description=f"Process this request: '{prompt}'. Context: {RESUME_DATA}. Provide a professional SaaS-styled markdown response.",
        expected_output="A concise, structured evaluation response.",
        agent=worker
    )
    
    crew = Crew(agents=[worker], tasks=[context_task], process=Process.sequential)
    return str(crew.kickoff())

def generate_elevenlabs_voice(text: str) -> str:
    """Synthesizes text input into a streaming speech audio file URL using ElevenLabs."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") # Default natural voice
    if not api_key:
        return None
        
    url = f"https://elevenlabs.io{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    data = {
        "text": text[:250], # Restrict character length for 1-day MVP limits
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            # Note: For a true 1-day production, save response.content bytes 
            # to your public static folder or an S3/Cloudinary media bucket and return the URL link.
            return "/static/audio/latest_response.mp3"
    except Exception as e:
        print(f"Voice generation exception: {e}")
    return None
