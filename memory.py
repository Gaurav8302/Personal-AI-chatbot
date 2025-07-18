# memory.py
# Handles loading/saving chat memory, user profile, and session summaries

import json
import os
import requests
import glob
from datetime import datetime, timedelta

SESSIONS_DIR = "chat_sessions"
SUMMARY_SUFFIX = "-summary.json"
LLM_URL = "http://localhost:1234/v1/chat/completions"

os.makedirs(SESSIONS_DIR, exist_ok=True)

def get_today_filename():
    """Returns today's session chat filename."""
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(SESSIONS_DIR, f"{today}.json")

def get_summary_filename():
    """Returns today's summary filename."""
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(SESSIONS_DIR, f"{today}{SUMMARY_SUFFIX}")

def load_session():
    """Loads the latest chat history and all summaries. Creates a user profile if missing."""
    print("🧠 Loading session and summaries...")
    session_file = get_today_filename()

    # Load or create user profile
    profile_path = os.path.join(SESSIONS_DIR, "user_profile.json")
    if not os.path.exists(profile_path):
        print("👤 First-time setup: Let's create your user profile.")
        name = input("What's your name? 👉 ").strip()
        bio = "someone who uses this assistant"
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump({"name": name}, f, indent=2)
    else:
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
            name = profile.get("name", "User")
            bio = "someone who uses this assistant"

    # Collect recent summaries (last 4 days)
    summary_files = []
    for i in range(4):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        day_files = glob.glob(os.path.join(SESSIONS_DIR, f"{day}-summary_*.json"))
        single_summary = os.path.join(SESSIONS_DIR, f"{day}-summary.json")
        if os.path.exists(single_summary):
            day_files.append(single_summary)
        summary_files.extend(day_files)

    summary_files = sorted(summary_files)
    print("🧠 Found summaries:", summary_files)

    memory = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    for summary_file in summary_files:
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                summary_obj = json.load(f)
                summary = summary_obj.get("summary", "")
                if summary:
                    print(f"🧠 Injecting summary: {summary}")
                    memory.append({"role": "user", "content": f"My name is {name}."})
                    memory.append({"role": "assistant", "content": f"Hello {name}! You just told me your name, and I’ll remember it for this session."})
        except json.JSONDecodeError:
            print(f"⚠️ Could not load summary file {summary_file}. Ignoring.")

    # Append recent session history
    if os.path.exists(session_file):
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                session_history = json.load(f)
                memory.extend(session_history[-10:])
        except json.JSONDecodeError:
            print("⚠️ Could not load session file. Starting fresh.")

    # Append user profile as system messages
    memory.append({"role": "system", "content": f"You are talking to {name}, the user of this personal assistant. {name} is {bio}. When the user says 'me', 'I', or 'myself', assume they mean {name}."})
    memory.append({"role": "assistant", "content": f"Nice to meet you, {name}! I'll remember your name for this session."})

    return memory

def get_full_session_history():
    """Loads the full chat log for today."""
    session_file = get_today_filename()
    if os.path.exists(session_file):
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Could not read full session history.")
    return []

def save_message(role, content):
    """Appends a new message to today's session file."""
    session_file = get_today_filename()
    try:
        messages = []
        if os.path.exists(session_file):
            with open(session_file, "r", encoding="utf-8") as f:
                messages = json.load(f)
        messages.append({"role": role, "content": content})
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Failed to save message: {e}")

def save_summary(summary_text):
    """Saves a summarized memory file with timestamp and context info."""
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    base_name = datetime.now().strftime("%Y-%m-%d")
    existing = glob.glob(os.path.join(SESSIONS_DIR, f"{base_name}-summary_*.json"))
    index = len(existing) + 1
    summary_file = os.path.join(SESSIONS_DIR, f"{base_name}-summary_{index}.json")

    summary_data = {
        "summary": summary_text,
        "created_at": timestamp,
        "context": "auto-generated"
    }

    try:
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        print(f"📁 Summary written to {summary_file}\n\n📌 Summary Content:\n{summary_text}\n")
    except Exception as e:
        print(f"❌ Failed to save summary: {e}")

def summarize_and_save(messages_to_summarize):
    """Uses the local LLM to summarize part of the chat and saves it."""
    print("🧪 summarize_and_save() triggered...")

    from datetime import datetime
    import os
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    filtered_messages = [msg for msg in messages_to_summarize if msg["role"] in ("user", "assistant")]

    summarization_prompt = [
        {"role": "system", "content": "You are an assistant memory tool. Summarize this conversation in bullet points capturing the user's key traits, interests, goals, and background."},
        *filtered_messages,
        {"role": "user", "content": "Please summarize the conversation so far."}
    ]

    payload = {
        "model": "mixtral-8x7b-instruct-v0.1.Q4_K_M",
        "messages": summarization_prompt,
        "temperature": 0.3
    }

    try:
        response = requests.post(LLM_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        print("🧪 Full model response:")
        print(json.dumps(data, indent=2))

        if "choices" in data and len(data["choices"]) > 0:
            summary = data["choices"][0]["message"]["content"].strip()
            if summary:
                save_summary(summary)

                # 🏷️ Generate a short title (second call)
                title_prompt = summarization_prompt[:-1] + [
                    {"role": "user", "content": "Give a 3-5 word title for this chat."}
                ]
                title_payload = {**payload, "messages": title_prompt}

                try:
                    title_response = requests.post(LLM_URL, json=title_payload)
                    title_response.raise_for_status()
                    title_data = title_response.json()
                    title = title_data["choices"][0]["message"]["content"].strip()

                    # Save metadata
                    title_file = os.path.join(SESSIONS_DIR, f"{timestamp}-meta.json")
                    with open(title_file, "w", encoding="utf-8") as f:
                        json.dump({"title": title, "created_at": timestamp}, f, indent=2)
                    print(f"\n🏷️ Session Title: {title}")
                except Exception as e:
                    print(f"❌ Failed to save session title: {e}")

        else:
            print("❌ Unexpected response format:", data)
    except Exception as e:
        print(f"❌ Failed to summarize: {e}")
