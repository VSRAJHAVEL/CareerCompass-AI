"""
FastAPI backend for the Job Guidance Chatbot.
Endpoints:
  POST /chat           — send a message, get a streaming response
  GET  /history/{id}  — get session chat history
  DELETE /history/{id}— clear session history
  GET  /health         — health check
  GET  /               — serve frontend
"""

import uuid
import json
from pathlib import Path
from typing import Optional
import io
import PyPDF2

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ollama_client import chat_stream, check_ollama_health
from nlp_utils import analyze_message
from job_context import build_system_prompt
from nlp_matcher import calculate_resume_match

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CareerCompass — Job Guidance Chatbot",
    description="AI-powered career guidance using Ollama + qwen3-vl:8b",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store: { session_id: [{ role, content }, ...] }
sessions: dict[str, list[dict]] = {}

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# Serve static frontend files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ─── Schemas ──────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    nlp_analysis: dict


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main chat UI."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>CareerCompass API is running. Frontend not found.</h1>")


@app.get("/health")
async def health_check():
    """Health check — verifies Ollama connectivity."""
    ollama_ok = check_ollama_health()
    return {
        "status": "ok" if ollama_ok else "degraded",
        "ollama": "connected" if ollama_ok else "not reachable",
        "model": "qwen3-vl:8b",
    }


@app.post("/extract_resume")
async def extract_resume(file: UploadFile = File(...)):
    """Extract text from an uploaded PDF resume."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    try:
        contents = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return {"text": text.replace('\x00', '').strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint — streams the LLM response token by token.
    Uses NLP analysis to enrich the system prompt dynamically.
    """
    # Create or retrieve session
    session_id = request.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = []

    history = sessions[session_id]

    # NLP analysis
    analysis = analyze_message(request.message)
    intent = analysis["intent"]
    domain = analysis["domain"]

    # Build context-aware system prompt
    system_prompt = build_system_prompt(intent=intent, detected_domain=domain)
    
    # Check if a resume attachment was provided in the message
    resume_match_metadata = None
    if "--- ATTACHED RESUME ---" in request.message and domain:
        # Extract just the resume text out of the prompt
        try:
            resume_part = request.message.split("--- ATTACHED RESUME ---")[1].split("-----------------------")[0]
            resume_match_metadata = calculate_resume_match(resume_part, domain)
            if resume_match_metadata:
                # Add the missing skills to the prompt so the LLM explicitly addresses them
                system_prompt += f"\n\n### Mathematical NLP Analysis of Resume:\n- Score: {resume_match_metadata['match_score']}%\n- Missing Skills to emphasis: {', '.join(resume_match_metadata['missing_skills'])}"
        except Exception as e:
            print(f"Error calculating resume match: {e}")

    # Strip the massive raw resume block from the context so Qwen-VL doesn't crash or output instant EOS
    clean_message = request.message
    if "--- ATTACHED RESUME ---" in request.message:
        clean_message = request.message.split("--- ATTACHED RESUME ---")[0].strip()
        clean_message += "\n\n*(Note: I have attached my resume.)*"

    # Append user message to history
    history.append({"role": "user", "content": clean_message})

    # Keep history within a reasonable window (last 20 messages)
    windowed_history = history[-20:]

    # Stream response  
    full_response = []

    def generate():
        # First, send session_id and NLP metadata as a header chunk
        meta = {
            "type": "meta",
            "session_id": session_id,
            "nlp": analysis,
            "match_data": resume_match_metadata
        }
        yield f"data: {json.dumps(meta)}\n\n"

        # Stream LLM tokens
        for token in chat_stream(windowed_history, system_prompt):
            full_response.append(token)
            payload = {"type": "token", "content": token}
            yield f"data: {json.dumps(payload)}\n\n"

        # Save assistant response to history
        assistant_message = "".join(full_response)
        history.append({"role": "assistant", "content": assistant_message})

        # Send done signal
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """Retrieve chat history for a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": sessions[session_id]}


@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clear chat history for a session."""
    if session_id in sessions:
        sessions.pop(session_id)
    return {"status": "cleared", "session_id": session_id}


@app.get("/sessions")
async def list_sessions():
    """List all active sessions (for debugging)."""
    return {
        "sessions": [
            {"id": sid, "messages": len(msgs)}
            for sid, msgs in sessions.items()
        ]
    }
