# rag/rag_engine.py
import json
from rag.embedder import Embedder
from rag.vector_store import VectorStore
from memory import get_full_session_history
import os

class RAGEngine:
    def __init__(self, session_id=None):
        from datetime import datetime
        self.session_id = session_id or datetime.now().strftime("%Y-%m-%d")
        self.embedder = Embedder()
        self.vector_store = VectorStore(session_id=self.session_id, embedder=self.embedder)

    def build_index(self):
        """Embeds and indexes both session memory and summaries."""
        from glob import glob

        # 👉 Load today’s chat history
        messages = get_full_session_history()
        filtered = [m for m in messages if m["role"] in ("user", "assistant")]

        # 👉 Load summaries too
        # 👉 Load summaries too
        from glob import glob
        summary_files = glob(os.path.join("chat_sessions", "*-summary*.json"))

        for path in summary_files:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    summary_data = json.load(f)
                    summary_text = summary_data.get("summary", "").strip()
                    if summary_text:
                        filtered.append({
                            "role": "system",
                            "content": summary_text
                        })
            except Exception as e:
                print(f"⚠️ Could not read summary file {path}: {e}")


        self.vector_store.add_messages(filtered)
        self.vector_store.save()


    def get_context_for(self, query: str, top_k=5) -> list[dict]:
        """Retrieve top-k relevant memory chunks for the query."""
        return self.vector_store.search(query, top_k=top_k)
