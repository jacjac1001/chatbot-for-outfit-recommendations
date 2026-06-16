from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer


def load_text_chunks(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        return []

    text = file_path.read_text(encoding="utf-8")

    raw_chunks = text.split("\n\n")

    chunks = []

    for chunk in raw_chunks:
        cleaned = chunk.strip()

        if cleaned:
            chunks.append(cleaned)

    return chunks


class SimpleRAG:
    def __init__(self, knowledge_file="knowledge_base.txt"):
        self.knowledge_file = knowledge_file
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        self.chunks = load_text_chunks(self.knowledge_file)

        if self.chunks:
            self.embeddings = self.model.encode(
                self.chunks,
                normalize_embeddings=True
            )
        else:
            self.embeddings = np.array([])

    def search(self, query, top_k=3):
        if not self.chunks:
            return []

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )[0]

        scores = np.dot(self.embeddings, query_embedding)

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []

        for index in top_indices:
            results.append({
                "chunk": self.chunks[index],
                "score": float(scores[index])
            })

        return results