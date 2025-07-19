import requests
from memory import save_message, get_full_session_history
from rag.rag_engine import RAGEngine

LLM_URL = "http://localhost:1234/v1/chat/completions"

# You can adjust the model name and temperature as needed
MODEL_NAME = "mixtral-8x7b-instruct-v0.1.Q4_K_M"
TEMPERATURE = 0.6

def chat_with_memory(user_input: str, session_id: str) -> str:
    # Save user message
    save_message("user", user_input, session_id=session_id)

    # Load full session history for this session
    session_history = get_full_session_history(session_id=session_id)

    # Build RAG context
    rag = RAGEngine(session_id=session_id)
    rag_context = rag.get_context_for(user_input)

    # Build prompt: system + context + session history + user input
    context_msgs = [
        {"role": "system", "content": "Here are some previous messages you might want to remember:"}
    ]
    for msg in rag_context:
        context_msgs.append({"role": msg["role"], "content": msg["content"]})

    full_prompt = context_msgs + session_history + [{"role": "user", "content": user_input}]

    payload = {
        "model": MODEL_NAME,
        "messages": full_prompt,
        "temperature": TEMPERATURE
    }

    response = requests.post(LLM_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    bot_reply = data["choices"][0]["message"]["content"].strip()

    # Save assistant reply
    save_message("assistant", bot_reply, session_id=session_id)

    return bot_reply 