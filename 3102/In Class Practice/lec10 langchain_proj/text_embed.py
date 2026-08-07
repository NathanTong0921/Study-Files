from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")
texts = [
    "The canine barked loudly.",
    "The dog made a noisy bark.",
    "He ate a lot of pizza.",
    "He devoured a large quantity of pizza pie.",
]
text_embeddings = model.encode(texts)

type(text_embeddings) # <class 'numpy.ndarray'>
print(text_embeddings.shape) # (4, 384)

def compute_cosine_similarity(u: np.ndarray, v: np.ndarray) -> float:
    """Compute the cosine similarity between two vectors"""
    return (u @ v) / (np.linalg.norm(u) * np.linalg.norm(v))


print(compute_cosine_similarity(text_embeddings[0,],text_embeddings[1,]))
print(compute_cosine_similarity(text_embeddings[1,],text_embeddings[2,]))
print(compute_cosine_similarity(text_embeddings[2,],text_embeddings[3,]))
print(compute_cosine_similarity(text_embeddings[3,],text_embeddings[0,]))

