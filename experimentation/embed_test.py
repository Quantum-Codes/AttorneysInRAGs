from sentence_transformers import SentenceTransformer
import time

def build_embeddings(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    """Encode texts to 384-dim normalized embeddings for cosine similarity."""
    # Normalize embeddings for cosine: improves recall and consistency
    return model.encode(texts, normalize_embeddings=True).tolist()

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
model2 = SentenceTransformer("all-MiniLM-L6-v2")

t1 = time.time()
embeddings = build_embeddings(model, ["Hello world", "hey"])
t2 = time.time()
print(f"Time taken: {t2 - t1} seconds")

t1 = time.time()
embeddings2 = build_embeddings(model2, ["Hello world", "hey"])
t2 = time.time()
print(f"Time taken: {t2 - t1} seconds")
