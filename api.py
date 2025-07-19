from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import json
from memory import get_full_session_history
from chatbot import chat_with_memory

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3004"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHAT_SESSIONS_DIR = "chat_sessions"

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.get("/sessions")
def list_sessions():
    # List all session files in chat_sessions/
    sessions = []
    for fname in os.listdir(CHAT_SESSIONS_DIR):
        if fname.endswith(".json") and not fname.endswith("-summary.json") and not fname == "user_profile.json":
            session_id = fname[:-5]
            # Try to get title from meta file
            meta_path = os.path.join(CHAT_SESSIONS_DIR, f"{session_id}-meta.json")
            title = None
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        title = meta.get("title")
                except Exception:
                    pass
            sessions.append({"id": session_id, "title": title or f"Chat with AI ({session_id[:6]})"})
    return sessions

@app.post("/sessions")
def create_session():
    session_id = str(uuid.uuid4())
    # Create empty session file
    path = os.path.join(CHAT_SESSIONS_DIR, f"{session_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump([], f)
    return {"id": session_id}

@app.get("/memory/{session_id}")
def get_memory(session_id: str):
    messages = get_full_session_history(session_id=session_id)
    return messages

@app.get("/meta/{session_id}")
def get_meta(session_id: str):
    meta_path = os.path.join(CHAT_SESSIONS_DIR, f"{session_id}-meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            return {"title": meta.get("title", f"Chat with AI ({session_id[:6]})")}
    return {"title": f"Chat with AI ({session_id[:6]})"}

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    try:
        reply = chat_with_memory(req.message, req.session_id)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 