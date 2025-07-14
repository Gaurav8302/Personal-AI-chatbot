# 🤖 Smart Local AI Chatbot with Memory

A personalized, privacy-friendly AI chatbot that runs entirely on your system using local Large Language Models (LLMs) with long-term memory capabilities and user context tracking.

Built with 🧠 smart memory injection, session summaries, and profile recall. Inspired by ChatGPT — but fully offline and customizable!

---

## 🚀 Features

- 🗣️ Natural conversation using local LLMs (like Mixtral, LLaMA, Mistral, etc.)
- 🧠 Persistent memory through session summaries
- 👤 Personalized memory per user (remembers your name & topics)
- 📁 Local JSON-based storage of history and memory
- 💡 Summarization triggered after every chat session
- 🖥️ Run on Windows/Linux/macOS with LM Studio

---

## 🛠️ Requirements

Python 3.10+ and the following packages:

```bash
pip install -r requirements.txt

```

## 💾 Local LLM Setup

1. **Install [LM Studio](https://lmstudio.ai)**
2. Download a compatible model:
   - 🔥 Recommended: `mixtral-8x7b-instruct-v0.1.Q4_K_M`
   - OR try `Nous-Hermes-2-Mistral-7B-DPO`
3. Enable OpenAI-compatible API server in LM Studio
   - Start it at: `http://localhost:1234/v1/chat/completions`

---

## 📂 Project Structure

```
chat_sessions/               # All chat logs and summaries stored here
├── 2025-07-13.json           # Full chat log of a session
├── 2025-07-13-summary.json   # Summary generated after session
├── user_profile.json         # Stores your name

main.py                      # Runs the chat and loop
memory.py                    # Handles memory, profile, and summaries
requirements.txt             # Python packages
README.md                    # This file
```

---

## 🧠 Memory System Explained

- **Summaries**: Every 20-ish exchanges, the bot generates a bullet-point summary using the LLM and stores it.
- **User Profile**: First-time run asks for your name. Stored locally.
- **Memory Injection**: At every startup, previous summaries and user info are added to the system prompt so the model "remembers."

---

## ✅ Running the Chatbot

```bash
python main.py
```

You’ll see:
```bash
🤖 Personal AI Chatbot with smart memory is running! Type 'exit' to quit.
```

Then just type and chat naturally. Exit with:
```bash
You: exit
```

---

## 📌 Example Interaction

```
You: hey my name is Gaurav
Bot: Hello Gaurav! I'll remember that.
...
You: do you remember my name?
Bot: Yes! You said your name is Gaurav.
```

---

## 🛡️ Privacy

This bot **does not use any online services**. Everything — chats, names, summaries — is stored **locally**.

---

## 📈 Future Plans

- Add GUI using Tkinter or Gradio
- Multi-user login
- File attachment understanding
- Vector embedding-based memory (Chroma/FAISS)

---

## 🧑‍💻 Credits

Built with ❤️ by Gaurav (2025). Powered by open-source AI.
