# rag/embedder.py

from sentence_transformers import SentenceTransformer
import numpy as np
import os

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"🔍 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed a single piece of text and return a numpy vector.
        """
        return self.model.encode(text, convert_to_numpy=True)

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """
        Embed a list of texts and return a 2D numpy array.
        """
        return self.model.encode(texts, convert_to_numpy=True)
