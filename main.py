# main.py
import requests
from memory import load_session, save_message, get_full_session_history, summarize_and_save
from rag.rag_engine import RAGEngine

print("🤖 Personal AI Chatbot with RAG memory is running! Type 'exit' to quit.\n")

# Load recent memory
chat_history = load_session()

# Load + build RAG engine
rag = RAGEngine()
rag.build_index()

while True:
    user_input = input("You: ")
    if user_input.strip().lower() == "exit":
        summarize_and_save(get_full_session_history())
        break

    # 🔍 Get relevant past context using RAG
    rag_context = rag.get_context_for(user_input)

    # 🧠 Inject RAG context as messages at the top
    context_msgs = [
        {"role": "system", "content": "Here are some previous messages you might want to remember:"}
    ]
    for msg in rag_context:
        context_msgs.append({"role": msg["role"], "content": msg["content"]})

    # 🧵 Combine context + live session history
    full_prompt = context_msgs + chat_history + [{"role": "user", "content": user_input}]

    # Send to local LLM
    payload = {
        "model": "mixtral-8x7b-instruct-v0.1.Q4_K_M",
        "messages": full_prompt,
        "temperature": 0.6
    }

    try:
        response = requests.post("http://localhost:1234/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        bot_reply = data["choices"][0]["message"]["content"].strip()
        print("Bot:", bot_reply)

        # Save messages to memory
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": bot_reply})
        save_message("user", user_input)
        save_message("assistant", bot_reply)

        # Update FAISS index with new messages
        rag.vector_store.add_messages([{"role": "user", "content": user_input}, {"role": "assistant", "content": bot_reply}])
        rag.vector_store.save()

    except Exception as e:
        print("❌ Request failed:", e)
