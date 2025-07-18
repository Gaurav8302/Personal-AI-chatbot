from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import json

app = FastAPI(title="AI Chatbot API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
sessions_db: Dict[str, Dict] = {}
messages_db: Dict[str, List[Dict]] = {}

# Pydantic models
class SessionCreate(BaseModel):
    title: Optional[str] = "New Chat"

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str

class MessageRequest(BaseModel):
    message: str
    session_id: str

class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: str

class ChatResponse(BaseModel):
    user_message: MessageResponse
    ai_message: MessageResponse

# Helper functions
def generate_session_id() -> str:
    return str(uuid.uuid4())

def get_current_timestamp() -> str:
    return datetime.now().isoformat()

def simulate_ai_response(user_message: str, session_history: List[Dict]) -> str:
    """
    Simulate AI response. Later this will connect to your RAG system and LLM.
    """
    responses = [
        f"That's interesting! You mentioned: '{user_message}'. Tell me more about that.",
        f"I understand you're saying '{user_message}'. How can I help you with that?",
        f"Thanks for sharing that. Regarding '{user_message}', here's what I think...",
        "I'm processing your message and learning from our conversation history.",
        "Based on our chat so far, I can see you're interested in various topics. What would you like to explore next?"
    ]
    
    # Simple logic based on message content
    message_lower = user_message.lower()
    if "hello" in message_lower or "hi" in message_lower:
        return "Hello! I'm your AI assistant. How can I help you today?"
    elif "summarize" in message_lower:
        if len(session_history) > 2:
            return f"So far we've exchanged {len(session_history)} messages. You've been asking about various topics and I've been trying to help you explore them."
        else:
            return "We've just started our conversation! There isn't much to summarize yet."
    elif "fact" in message_lower:
        return "Here's a fun fact: Octopuses have three hearts and blue blood! Two hearts pump blood to the gills, while the third pumps blood to the rest of the body."
    else:
        return responses[len(session_history) % len(responses)]

# API Endpoints
@app.post("/sessions", response_model=SessionResponse)
async def create_session(session_data: SessionCreate):
    """Create a new chat session"""
    session_id = generate_session_id()
    timestamp = get_current_timestamp()
    
    session = {
        "id": session_id,
        "title": session_data.title,
        "created_at": timestamp
    }
    
    sessions_db[session_id] = session
    messages_db[session_id] = []
    
    return SessionResponse(**session)

@app.get("/sessions", response_model=List[SessionResponse])
async def get_sessions():
    """Get all chat sessions"""
    sessions = list(sessions_db.values())
    # Sort by created_at descending (newest first)
    sessions.sort(key=lambda x: x["created_at"], reverse=True)
    return [SessionResponse(**session) for session in sessions]

@app.get("/meta/{session_id}", response_model=SessionResponse)
async def get_session_meta(session_id: str):
    """Get session metadata"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions_db[session_id]
    return SessionResponse(**session)

@app.get("/memory/{session_id}", response_model=List[MessageResponse])
async def get_session_memory(session_id: str):
    """Get chat history for a session"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = messages_db.get(session_id, [])
    return [MessageResponse(**msg) for msg in messages]

@app.post("/chat", response_model=ChatResponse)
async def chat(request: MessageRequest):
    """Send a message and get AI response"""
    if request.session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    timestamp = get_current_timestamp()
    
    # Create user message
    user_message = {
        "role": "user",
        "content": request.message,
        "timestamp": timestamp
    }
    
    # Get session history for context
    session_history = messages_db.get(request.session_id, [])
    
    # Generate AI response (this will later connect to your RAG + LLM)
    ai_content = simulate_ai_response(request.message, session_history)
    
    ai_message = {
        "role": "assistant",
        "content": ai_content,
        "timestamp": get_current_timestamp()
    }
    
    # Store both messages
    if request.session_id not in messages_db:
        messages_db[request.session_id] = []
    
    messages_db[request.session_id].extend([user_message, ai_message])
    
    # Update session title if it's the first message
    if len(messages_db[request.session_id]) == 2:  # First exchange
        # Generate a title from the first message
        title_words = request.message.split()[:4]
        new_title = " ".join(title_words) + ("..." if len(request.message.split()) > 4 else "")
        sessions_db[request.session_id]["title"] = new_title
    
    return ChatResponse(
        user_message=MessageResponse(**user_message),
        ai_message=MessageResponse(**ai_message)
    )

@app.get("/")
async def root():
    return {"message": "AI Chatbot API is running!", "sessions": len(sessions_db)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)