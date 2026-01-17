from sentence_transformers import SentenceTransformer
import time
from svo import legal_distill_v2
import chromadb
from pathlib import Path
from typing import Dict

def build_embeddings(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    """Encode texts to 384-dim normalized embeddings for cosine similarity."""
    # Normalize embeddings for cosine: improves recall and consistency
    return model.encode(texts, normalize_embeddings=True).tolist()

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
model2 = SentenceTransformer("all-MiniLM-L6-v2")

tos_1 = "If a transfer of any Customer Data from Salesforce to Supplier occurs in connection with the Licensed Software then, notwithstanding anything to the contrary, Section 3(v) of these Software Terms shall apply."
tos_2 = "Supplier will deliver the most current version of the Licensed Software to Salesforce via electronic delivery or load-and-leave services, and will not deliver tangible materials to Salesforce without Salesforce’s advance written consent"

tos_1_distilled = legal_distill_v2(tos_1)
tos_2_distilled = legal_distill_v2(tos_2)

t1 = time.time()
embeddings = build_embeddings(model, [tos_1_distilled, tos_2_distilled])
t2 = time.time()
print(f"Time taken: {t2 - t1} seconds")
"""
t1 = time.time()
embeddings2 = build_embeddings(model2, ["Hello world", "hey"])
t2 = time.time()
print(f"Time taken: {t2 - t1} seconds")
"""

# TEST COSINE SIMILARITY

def project_paths() -> Dict[str, Path]:
    """Resolve key project paths using pathlib, independent of CWD."""
    here = Path(__file__).resolve()
    root = here.parent.parent  # AttorneysInRAGs/
    db_json = root / "backend" / "database" / "db.json"
    chroma_dir = root / "backend" / "database" / "chroma_db"
    return {"root": root, "db_json": db_json, "chroma_dir": chroma_dir}

client = chromadb.Client()
paths = project_paths()
# Initialize Chroma persistent client with cosine space for HNSW
client = chromadb.PersistentClient(path=str(paths["chroma_dir"]))

collection = client.get_collection(name="policies")

t1 = time.time()
laws = collection.query(
    query_embeddings=embeddings,
    n_results=2,
)
t2 = time.time()
print(f"ChromaDB query time taken: {t2 - t1} seconds")
print(laws)
