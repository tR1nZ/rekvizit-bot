from io import BytesIO
import numpy as np


def vector_to_blob(vector: np.ndarray) -> bytes:
    bio = BytesIO()
    np.save(bio, vector)
    return bio.getvalue()


def blob_to_vector(blob: bytes) -> np.ndarray:
    bio = BytesIO(blob)
    bio.seek(0)
    return np.load(bio)