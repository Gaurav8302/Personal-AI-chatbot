# 🤖 Personal AI Chatbot with RAG-Based Memory

A fully offline, privacy-first AI chatbot with **long-term memory**, **user profiles**, and **context-aware responses** — powered by **local LLMs** and a **retrieval-augmented generation (RAG)** system using FAISS.

Inspired by ChatGPT — but runs **completely on your machine**, with **zero cloud dependency**.

---

## 🚀 Features

- 🧠 **RAG Memory**: Retrieves relevant past info via vector embeddings (FAISS)
- 💬 Natural chat flow using local LLMs (Mixtral, Mistral, LLaMA, etc.)
- 👤 Personalized context memory (name, interests, routines)
- 📝 Automatic session summarization with title generation
- 📂 Fully local JSON storage for chats, summaries, and profiles
- 🖥️ LM Studio integration for model serving (OpenAI-compatible API)

---

## 🛠️ Requirements

- Python 3.10+
- [LM Studio](https://lmstudio.ai) running locally
- Install dependencies:

```bash
pip install -r requirements.txt
````

---

## 🤖 Local LLM Setup

1. **Install LM Studio**
2. **Download a compatible model** (e.g.):

   * `mixtral-8x7b-instruct-v0.1.Q4_K_M`
   * `Nous-Hermes-2-Mistral-7B-DPO`
3. **Start LM Studio’s OpenAI API Server**:

   * `http://localhost:1234/v1/chat/completions`

---

## 🧠 Memory System

* ✅ **RAG Engine** (`rag/`):

  * Uses SentenceTransformers to embed messages & summaries
  * Stores in FAISS vector index
  * Retrieves top-k context chunks per user query

* ✅ **Summarization** (`memory.py`):

  * Generates structured summaries using LLM
  * Saved and injected into memory on startup

* ✅ **User Profile**:

  * Name, preferences, and key traits saved locally

---

## 📂 Project Structure

```
chat_sessions/             ← Chat logs, summaries, and user profile
rag/                       ← Embedder, VectorStore, and RAGEngine modules
main.py                    ← CLI entrypoint with chat + RAG + memory
memory.py                  ← Session, summary, and profile logic
requirements.txt           ← Python dependencies
```

> All volatile data (chats, vector DB, profiles) is excluded via `.gitignore`

---

## ▶️ Run the Chatbot

```bash
python main.py
```

You’ll see:

```
🤖 Personal AI Chatbot with RAG memory is running! Type 'exit' to quit.
```

---

## 💬 Example Memory Recall

```
You: My dog's name is Pluto.
You: I love the movie Interstellar.
You: I'm building a skincare app.
...
You: What's my dog's name?
Bot: You mentioned your dog's name is Pluto.
```

---

## 🔐 Privacy First

This bot runs **100% offline**. No cloud, no tracking, no data leaks.
All chat and memory are stored **locally on your device**.

---

## 🧩 Future Improvements

* Web frontend (Next.js + FastAPI API)
* Session renaming + metadata UI
* Embedding cache for faster boot
* Multi-user login
* Gradio or Tkinter UI

---

## 👨‍💻 Author

Built with ❤️ by [Gaurav](https://github.com/Gaurav8302)
MIT Licensed · Powered by Open Source LLMs

```

---

### ✅ What’s New
- Added `rag/` structure
- Described FAISS RAG pipeline
- Updated run instructions
- Future roadmap and privacy note
- GitHub-friendly formatting

Let me know if you'd like a version with screenshots or badges next!
```
