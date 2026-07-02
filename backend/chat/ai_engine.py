import os
import requests
from django.conf import settings
from crewai import Agent, Task, Crew, Process

# ==========================================
# 1. KNOWLEDGE BASE INGESTION TOOL (RAG)
# ==========================================
def load_portfolio_knowledge() -> str:
    """
    Safely reads your static resume text file to feed into the LLM context pool.
    """
    try:
        file_path = os.path.join(settings.BASE_DIR, 'chat', 'resume.txt')
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"🔴 Error loading resume context file: {e}")
        return "John Doe is an Elite Full-Stack AI Engineer specializing in React, TypeScript, and Django Ninja."

# ==========================================
# 2. CREWAI AGENT ORCHESTRATION FACTORY
# ==========================================
def get_specialized_agent(agent_id: str) -> Agent:
    """
    Factory pattern returning specialized CrewAI agents with specific roles, goals, and traits.
    """
    # Force CrewAI to use the OpenAI API Key from your cloud environment variables
    openai_key = os.getenv("OPENAI_API_KEY", "mock-key-for-local-testing")
    
    if agent_id == "cv":
        return Agent(
            role="Corporate Talent Acquisition Director",
            goal="Analyze the developer's tech stack, framework projects, and experience accurately for tech recruiters.",
            backstory="You are an elite silicon-valley technical recruiter. You evaluate matching frameworks and answer project architecture inquiries with professional brevity.",
            verbose=False,
            allow_delegation=False
        )
    elif agent_id == "audit":
        return Agent(
            role="Principal Security Architect & Threat Analyst",
            goal="Review software code blocks for vulnerabilities, architectural malpractices, memory leaks, or syntax errors.",
            backstory="You are a strict, blunt cyber-security auditor. You provide precise code evaluations, rank bug severity (High/Medium/Low), and provide refactored, safe code snippets in beautiful markdown.",
            verbose=False,
            allow_delegation=False
        )
    elif agent_id == "bio":
        return Agent(
            role="Virtual Operations Chief of Staff",
            goal="Provide accurate data regarding the developer's geographic location, contact pathways, and hiring parameters.",
            backstory="You manage John's professional calendar and global logistics operations. You explain explicitly where he stays, how to call him, and call-to-actions.",
            verbose=False,
            allow_delegation=False
        )
    else: # 'voice' or baseline identity ambassador
        return Agent(
            role="Virtual Chief PR Officer",
            goal="Draft a natural, highly engaging professional summary about John's capabilities designed specifically for voice broadcasting.",
            backstory="You are a masterful marketing presenter. You summarize his career in punchy, verbal-friendly sentences that sound incredible when spoken out loud by an audio engine.",
            verbose=False,
            allow_delegation=False
        )

# ==========================================
# 3. PIPELINE WORKFLOW EXECUTION THREAD
# ==========================================
def run_agent_pipeline(agent_id: str, prompt: str) -> str:
    """
    Ingests prompts, links agents to tasks, evaluates grounding context, and returns responses.
    """
    # 1. Fetch grounding context information
    knowledge_base = load_portfolio_knowledge()
    
    # 2. Build the targeted worker agent
    worker_agent = get_specialized_agent(agent_id)
    
    # 3. Establish task guidelines with strict formatting thresholds
    analysis_task = Task(
        description=(
            f"User Prompt: '{prompt}'\n\n"
            f"Grounding Data Context:\n{knowledge_base}\n\n"
            f"Instructions: Process the user prompt strictly using the Grounding Data context. "
            f"Act out your specified role completely. Use tight, professional typography and layout. "
            f"If code is present, supply a clean, optimized solution."
        ),
        expected_output="A clean, concise, executive-level markdown response addressing the prompt directly based on context rules.",
        agent=worker_agent
    )
    
    # 4. Spin up the Crew structure
    crew = Crew(
        agents=[worker_agent],
        tasks=[analysis_task],
        process=Process.sequential
    )
    
    # Execute and return raw completion output string
    return str(crew.kickoff())

# ==========================================
# 4. ELEVENLABS MULTI-MODAL SYNTHESIS ENGINE
# ==========================================
def generate_elevenlabs_voice(text: str) -> str:
    """
    Synthesizes text layouts into physical streaming speech files using ElevenLabs TTS.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") # Standard professional natural tone
    
    if not api_key:
        print("⚠️ Missing ELEVENLABS_API_KEY. Skipping multi-modal audio generation thread.")
        return None
        
    url = f"{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text[:200], # Clamp parameter constraint limit to save free tier allocation bytes
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            # Create a static media folder if it doesn't exist
            audio_dir = os.path.join(settings.BASE_DIR, 'static', 'audio')
            os.makedirs(audio_dir, exist_ok=True)
            
            audio_file = os.path.join(audio_dir, 'latest_voice.mp3')
            with open(audio_file, 'wb') as f:
                f.write(response.content)
                
            # Returns the web accessible absolute url parameter mapping to your server root
            return "/static/audio/latest_voice.mp3"
        else:
            print(f"🔴 ElevenLabs returned status code: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"🔴 Voice synthesis network pipeline failure: {e}")
        
    return None
