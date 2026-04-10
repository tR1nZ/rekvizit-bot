import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def encode_text(self, text: str) -> np.ndarray:
        vector = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return vector.astype(np.float32)