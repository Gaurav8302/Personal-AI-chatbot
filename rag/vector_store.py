# rag/vector_store.py

import faiss
import numpy as np
import json
import os
from typing import List, Dict
from .embedder import Embedder

class VectorStore:
    def __init__(self, session_id: str, embedder: Embedder, db_dir: str = "rag_db"):
        self.session_id = session_id
        self.embedder = embedder
        self.db_dir = db_dir
        self.index_path = os.path.join(db_dir, f"{session_id}.index")
        self.meta_path = os.path.join(db_dir, f"{session_id}_meta.json")
        self.index = None
        self.metadata = []
        os.makedirs(db_dir, exist_ok=True)
        self._load()

    def _load(self):
        # Load FAISS index and metadata if they exist
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            # New flat index with 384-dim vectors (MiniLM)
            self.index = faiss.IndexFlatL2(384)
            self.metadata = []

    def add_messages(self, messages: List[Dict]):
        """
        Embed and add messages to the index and metadata list.
        Expected format: {"role": "user"|"assistant", "content": "..."}
        """
        texts = [msg["content"] for msg in messages if msg["content"].strip()]
        if not texts:
            return  # Skip empty input

        vectors = self.embedder.embed_texts(texts)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        self.index.add(vectors)
        self.metadata.extend([msg for msg in messages if msg["content"].strip()])


    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for top_k most similar messages to the query.
        Returns message metadata.
        """
        if self.index.ntotal == 0:
            return []

        query_vec = self.embedder.embed_text(query).reshape(1, -1)
        distances, indices = self.index.search(query_vec, top_k)

        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results


    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
