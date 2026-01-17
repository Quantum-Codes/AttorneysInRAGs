import json
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from sentence_transformers import SentenceTransformer
import re


"""
GEMINI TOLD:

for a local project on a laptop with an Intel Ultra 7, you need a model that balances "Semantic Density" (how well it understands legal nuances) with "Inference Speed."

Since you are using a Rationale-based retrieval system, you don't need massive 4096-dimension vectors. Smaller, highly-tuned models actually perform better for short-text matching like SVO-to-Rationale.

1. The Recommended Model: BGE-Small-v1.5
The BGE (BAAI General Embedding) series is currently the "gold standard" for local RAG.

Model Name: BAAI/bge-small-en-v1.5

Dimensions: 384

Why this model? * Ultra-Lightweight: It’s only about 130MB. It will load into your RAM instantly and won't compete with Mistral for resources.

High Performance: Despite its size, it consistently outranks much larger models on the MTEB (Massive Text Embedding Benchmark).

384 Dimensions: This is the "sweet spot." It’s enough dimensions to distinguish between "sharing" and "collecting," but small enough that your Cosine Similarity math and ChromaDB queries will be near-instant.

2. Alternative: all-MiniLM-L6-v2
If BGE feels too "heavy" or you have compatibility issues, this is the classic choice.

Dimensions: 384

Why: It is the fastest model available. If your ToS is massive (100+ pages), and you need to embed thousands of filtered sentences quickly, this is your best bet. However, BGE-Small is generally "smarter" for legal logic.
"""


def project_paths() -> Dict[str, Path]:
    """Resolve key project paths using pathlib, independent of CWD."""
    here = Path(__file__).resolve()
    root = here.parent.parent  # AttorneysInRAGs/
    db_json = root / "backend" / "database" / "db.json"
    chroma_dir = root / "backend" / "database" / "chroma_db"
    return {"root": root, "db_json": db_json, "chroma_dir": chroma_dir}


def load_rules(db_json: Path) -> List[Dict[str, Any]]:
    """Load all rules from db.json."""
    with db_json.open("r", encoding="utf-8") as f:
        return json.load(f)


_cite_pattern = re.compile(r"\s*\[cite:[^\]]*\]\s*\.?\s*$")


def clean_rationale(text: str) -> str:
    """Remove trailing [cite: ...] tokens from the rationale string.

    - Robust to varying whitespace and optional trailing period.
    - If multiple citations appear at the end, remove them iteratively.
    """
    if not isinstance(text, str):
        return ""
    cleaned = text.strip()
    # Iteratively strip trailing citation blocks
    while True:
        new = _cite_pattern.sub("", cleaned)
        if new == cleaned:
            break
        cleaned = new.strip()
    return cleaned


def build_embeddings(model: SentenceTransformer, texts: List[str]) -> List[List[float]]:
    """Encode texts to 384-dim normalized embeddings for cosine similarity."""
    # Normalize embeddings for cosine: improves recall and consistency
    return model.encode(texts, normalize_embeddings=True).tolist()


def main() -> None:
    paths = project_paths()

    # Ensure ChromaDB directory exists
    paths["chroma_dir"].mkdir(parents=True, exist_ok=True)

    # Initialize Chroma persistent client with cosine space for HNSW
    client = chromadb.PersistentClient(path=str(paths["chroma_dir"]))

    # Prefer get_or_create to avoid errors if it already exists
    collection = client.get_or_create_collection(
        name="policies",
        metadata={
            "hnsw:space": "cosine",
        },
        embedding_function=None,  # We provide embeddings manually
    )

    # Load data
    rules = load_rules(paths["db_json"])

    # Prepare payloads
    ids: List[str] = []
    documents: List[str] = []  # cleaned rationales
    metadatas: List[Dict[str, Any]] = []

    for row in rules:
        rule_id = row.get("rule_id")
        if not rule_id:
            # Skip entries without an ID to avoid collision
            continue
        rationale = row.get("rationale", "")
        cleaned = clean_rationale(rationale)

        ids.append(str(rule_id))
        documents.append(cleaned)
        # Chroma metadata must be primitives; convert lists to comma strings
        domain_val = row.get("domain", [])
        if isinstance(domain_val, list):
            domain_str = ", ".join(map(str, domain_val))
        else:
            domain_str = str(domain_val) if domain_val is not None else ""

        metadatas.append(
            {
                "rule_id": str(rule_id),
                "domain": domain_str,
                "raw_law": row.get("raw_law", ""),
                "severity": row.get("severity", ""),
            }
        )

    # Decide embeddings approach: local SentenceTransformer (384-dim)
    # This aligns with Gemini guidance and runs fully offline.
    model = SentenceTransformer("BAAI/bge-small-en-v1.5") # "all-MiniLM-L6-v2" is 3x faster but the current is supposed to be better.
    embeddings = build_embeddings(model, documents)

    # Optional: remove any existing items with the same IDs to avoid duplicates
    try:
        collection.delete(ids=ids)
    except Exception:
        # Ignore if deletion not supported or IDs not present
        pass

    # Persist to Chroma
    collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    # Explicit persist not required for PersistentClient, but keeping for clarity
    # client.persist()  # Uncomment if using non-persistent clients

    print(f"Inserted {len(ids)} rules into Chroma collection 'policies'.")


if __name__ == "__main__":
    main()
