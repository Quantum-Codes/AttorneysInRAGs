# THIS IS NOT SVO. BUT THIS REMOVES STOPWORDS AND REPEATS FOR THE COSINE SIMILARITY CALCULATION
# THIS IS ACCEPTABLE

import spacy, time
from pathlib import Path
from typing import Dict, Any, List
import chromadb
from sentence_transformers import SentenceTransformer

def project_paths() -> Dict[str, Path]:
    """Resolve key project paths using pathlib, independent of CWD."""
    here = Path(__file__).resolve()
    root = here.parent.parent  # AttorneysInRAGs/
    db_json = root / "backend" / "database" / "db.json"
    chroma_dir = root / "backend" / "database" / "chroma_db"
    return {"root": root, "db_json": db_json, "chroma_dir": chroma_dir}


# init
nlp = spacy.load("en_core_web_sm")
embedder_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = chromadb.Client()
paths = project_paths()
client = chromadb.PersistentClient(path=str(paths["chroma_dir"]))
collection = client.get_collection(name="policies")

# Words that change legal meaning - NEVER remove these
LEGAL_OPERATORS = {"not", "no", "never", "only", "unless", "except", "if", "then"}

def legal_distill(text):
    doc = nlp(text)
    clean_tokens = []
    
    for token in doc:
        # Keep Numbers (for retention logic), Nouns, and Verbs
        if token.pos_ in ["NOUN", "PROPN", "VERB", "NUM"] or token.text.lower() in LEGAL_OPERATORS:
            if token.lemma_.lower() not in ["be", "have", "occur", "apply"]:
                clean_tokens.append(token.lemma_.lower())
    
    # Deduplicate while preserving order
    seen = set()
    final_tokens = []
    for t in clean_tokens:
        if t in LEGAL_OPERATORS or t not in seen:
            final_tokens.append(t)
            seen.add(t)
            
    return " ".join(final_tokens)

def build_embeddings(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    """Encode texts to 384-dim normalized embeddings for cosine similarity."""
    # Normalize embeddings for cosine: improves recall and consistency
    return model.encode(texts, normalize_embeddings=True).tolist()

def cosine_similarity(embeddings: list[list[float]]) -> dict:
    """
    EXAMPLE RETURN in experimentation/cosine.json

    SCORES ARE:
    Distance = 0.0: The embeddings are identical (Exact same direction).
    Distance = 1.0: The embeddings are orthogonal (Unrelated).
    Distance = 2.0: The embeddings are opposites (Pointing in different directions).

    threshold can be < 0.45 for valid.
    IMPLEMENT WHERE CLAUSE ON domain LATER
    IMPLEMENT THRESHOLDING HERE LATER if makes sense
    """
    laws = collection.query(
        query_embeddings=embeddings,
        n_results=2,
    )
    return laws


# --- TEST ---
if __name__ == "__main__":
    tos_1 = "If a transfer of any Customer Data from Salesforce to Supplier occurs in connection with the Licensed Software then, notwithstanding anything to the contrary, Section 3(v) of these Software Terms shall apply."
    tos_2 = "Supplier will deliver the most current version of the Licensed Software to Salesforce via electronic delivery or load-and-leave services, and will not deliver tangible materials to Salesforce without Salesforce’s advance written consent"


    # module 3
    t1 = time.time()
    tos1 = legal_distill(tos_1)
    tos2 = legal_distill(tos_2)
    print(f"Distilled 1: {tos1}")
    print(f"Distilled 2: {tos2}")
    print(f"Time taken: {time.time() - t1} seconds")
    
    # module 4
    t1 = time.time()
    embeddings = build_embeddings(embedder_model, [tos1, tos2])
    laws = cosine_similarity(embeddings)
    t2 = time.time()
    print(f"ChromaDB query time taken: {t2 - t1} seconds")
    

    

"""
OUT:
Distilled 1: if transfer customer data salesforce supplier connection licensed software then contrary section 3(v term
Distilled 2: supplier deliver version licensed software salesforce delivery load leave service not material advance write consent
Time taken: 0.012683868408203125 seconds
"""