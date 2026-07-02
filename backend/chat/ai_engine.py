import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from django.conf import settings
from crewai import Agent, Task, Crew, Process

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# ==========================================
# 1. KNOWLEDGE BASE INGESTION TOOL (RAG)
# ==========================================
def load_portfolio_knowledge() -> str:
    """
    Safely reads your static resume text file to feed into the LLM context pool.
    """
    try:
        if getattr(settings, 'configured', False):
            file_path = os.path.join(settings.BASE_DIR, 'chat', 'resume.txt')
        else:
            file_path = os.path.join(Path(__file__).resolve().parents[1], 'chat', 'resume.txt')
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"🔴 Error loading resume context file: {e}")
        return "John Doe is an Elite Full-Stack AI Engineer specializing in React, TypeScript, and Django Ninja."


def load_repository_code() -> str:
    """
    Read the project's backend source files for the audit agent to review.
    """
    repo_root = Path(__file__).resolve().parents[2]
    target_dirs = [
        repo_root / "backend" / "chat",
        repo_root / "backend" / "core",
    ]

    source_chunks = []
    total_chars = 0
    max_chars = 20000
    max_files = 20

    for directory in target_dirs:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.py")):
            if len(source_chunks) >= max_files or total_chars >= max_chars:
                break
            try:
                content = path.read_text(encoding="utf-8")
            except Exception:
                continue
            header = f"--- FILE: {path.relative_to(repo_root)} ---\n"
            snippet = header + content + "\n\n"
            if total_chars + len(snippet) > max_chars:
                snippet = snippet[: max_chars - total_chars]
            source_chunks.append(snippet)
            total_chars += len(snippet)

    return "".join(source_chunks)

# ==========================================
# 2. CREWAI AGENT ORCHESTRATION FACTORY
# ==========================================
def get_specialized_agent(agent_id: str) -> Agent:
    """
    Factory pattern returning specialized CrewAI agents with specific roles, goals, and traits.
    """
    # Force CrewAI to use Gemini via CrewAI native provider when available.
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
        os.environ["GOOGLE_API_KEY"] = gemini_key

    gemini_llm = "gemini-2.5-flash"

    if agent_id == "cv":
        return Agent(
            role="Corporate Talent Acquisition Director",
            goal="Analyze the developer's tech stack, framework projects, and experience accurately for tech recruiters.",
            backstory="You are an elite silicon-valley technical recruiter. You evaluate matching frameworks and answer project architecture inquiries with professional brevity.",
            llm=gemini_llm,
            verbose=False,
            allow_delegation=False
        )
    elif agent_id == "audit":
        return Agent(
            role="Principal Security Architect & Threat Analyst",
            goal="Review software code blocks for vulnerabilities, architectural malpractices, memory leaks, or syntax errors.",
            backstory="You are a strict, blunt cyber-security auditor. You provide precise code evaluations, rank bug severity (High/Medium/Low), and provide refactored, safe code snippets in beautiful markdown.",
            llm=gemini_llm,
            verbose=False,
            allow_delegation=False
        )
    elif agent_id == "bio":
        return Agent(
            role="Virtual Operations Chief of Staff",
            goal="Provide accurate data regarding the developer's geographic location, contact pathways, and hiring parameters.",
            backstory="You manage John's professional calendar and global logistics operations. You explain explicitly where he stays, how to call him, and call-to-actions.",
            llm=gemini_llm,
            verbose=False,
            allow_delegation=False
        )
    else: # 'voice' or baseline identity ambassador
        return Agent(
            role="Virtual Chief PR Officer",
            goal="Draft a natural, highly engaging professional summary about John's capabilities designed specifically for voice broadcasting.",
            backstory="You are a masterful marketing presenter. You summarize his career in punchy, verbal-friendly sentences that sound incredible when spoken out loud by an audio engine.",
            llm=gemini_llm,
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
    
    # 1b. For audit requests, include actual project source code into the grounding context
    if agent_id == "audit":
        repository_code = load_repository_code()
        if repository_code:
            knowledge_base = (
                f"{knowledge_base}\n\nRepository Source Code:\n{repository_code}"
            )
        else:
            knowledge_base = (
                f"{knowledge_base}\n\nRepository Source Code:\nUnable to load the project source files for audit."
            )

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

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text[:200], # Clamp parameter constraint limit to save free tier allocation bytes
        "model_id": "eleven_multilingual_v2",
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
