# main.py
# Launches the chatbot, handles interaction loop and memory calls

import requests
from memory import load_session, save_message, get_full_session_history, summarize_and_save

print("🤖 Personal AI Chatbot with smart memory is running! Type 'exit' to quit.\n")

# Load prior memory (session + summary + profile)
chat_history = load_session()

# Continuous prompt loop
while True:
    user_input = input("You: ")
    if user_input.strip().lower() == "exit":
        summarize_and_save(get_full_session_history())
        break

    # Append user input to history
    chat_history.append({"role": "user", "content": user_input})

    # Prepare and send payload to local LLM
    payload = {
        "model": "mixtral-8x7b-instruct-v0.1.Q4_K_M",
        "messages": chat_history,
        "temperature": 0.6
    }

    try:
        response = requests.post("http://localhost:1234/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        bot_reply = data["choices"][0]["message"]["content"].strip()
        print("Bot:", bot_reply)

        # Save assistant response to memory
        chat_history.append({"role": "assistant", "content": bot_reply})
        save_message("user", user_input)
        save_message("assistant", bot_reply)

    except Exception as e:
        print("❌ Request failed:", e)
