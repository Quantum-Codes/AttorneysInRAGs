import spacy, time
from pathlib import Path
from typing import Dict, Any, List
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.errors import InvalidArgumentError

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
# Ensure we use the PersistentClient to access the DB created in previous steps
paths = project_paths()
client = chromadb.PersistentClient(path=str(paths["chroma_dir"]))
collection = client.get_collection(name="policies")

# Words that change legal meaning - NEVER remove these
LEGAL_OPERATORS = {"not", "no", "never", "only", "unless", "except", "if", "then"}

def legal_distill(text: str) -> str:
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

def process_matches(results: Dict[str, Any], original_texts: List[str], threshold: float = 0.40) -> List[Dict[str, Any]]:
    """
    Filters and formats ChromaDB query results.
    
    Args:
        results: The raw dictionary returned by collection.query()
        original_texts: The list of original ToS sentences (not distilled) corresponding to the query order.
        threshold: The distance cutoff (default 0.45). Matches with distance > threshold are discarded.
        
    Returns:
        A list of dictionaries representing the accepted rules ready for the LLM prompt.
    """
    accepted_rules = []

    # Iterate through each query sentence (i)
    # results['distances'] is a list of lists: [[d1, d2], [d3, d4]]
    for i, distances in enumerate(results['distances']):
        original_tos = original_texts[i]
        
        # Iterate through the matches for this sentence (j)
        for j, dist in enumerate(distances):
            
            # 1. THRESHOLD FILTERING
            if dist < threshold:
                metadata = results['metadatas'][i][j]
                rationale = results['documents'][i][j]
                
                # Parse domain string back to list (it's stored as comma-sep string)
                domain_str = metadata.get('domain', "")
                domain_list = [d.strip() for d in domain_str.split(',')] if domain_str else []

                # 2. FORMATTING
                rule_match = {
                    "rule_id": metadata.get('rule_id'),
                    "distance": dist, # Useful for debugging or sorting priority
                    "domain": domain_list,
                    "raw_law": metadata.get('raw_law'),
                    "TOS_text": original_tos, # The original text for the LLM to analyze
                    "severity": metadata.get('severity'),
                    "rationale": rationale # The cleaned rationale from the DB
                }
                
                accepted_rules.append(rule_match)

    return accepted_rules

def find_violations(original_sentences: List[Any]) -> List[Dict[str, Any]]:
    """
    Main pipeline function: Distill -> Embed -> Query -> Filter -> Format
    """

    # modify format
    """
    {
        "text": text_chunk,
        "metadata": {
            "domains": domains,       # e.g., ['LIABILITY', 'DATA_SHARING']
            "filter_reason": reason   # e.g., "Matched 'indemnify'"
        }
    }

    TO
    sentences = ["sentences"] AND metadata = [{"domains": [...], "filter_reason": "..."}]
    """
    sentences = [item["text"] for item in original_sentences]
    metadata = [item["metadata"] for item in original_sentences]
    original_sentences = sentences
    # 1. Distill
    distilled_sentences = [legal_distill(text) for text in original_sentences]
    
    # 2. Embed
    embeddings = build_embeddings(embedder_model, distilled_sentences)
    
    # 3. Query (Fetch top 2 to check against threshold)
    # We query MORE than 1 (n_results=2) to handle cases where two different laws might apply,
    # but the threshold will ensure we don't return garbage.
    # Assuming 'detected_domains' is a list like ["DATA_RETENTION", "LOGGING_AUDIT"]
    # Flatten domains and build a permissive where clause.
    detected_domain_lists = [item.get("domains", []) for item in metadata]
    flat_domains = sorted({d for lst in detected_domain_lists for d in lst if isinstance(d, str) and d})

    # Attempt metadata prefilter; if rejected by Chroma, fallback to no filter.
    if flat_domains:
        # Use supported operator $in for exact matches on single-domain records
        where_clause = {"domain": {"$in": flat_domains}}
        raw_results = collection.query(
            query_embeddings=embeddings,
            n_results=2,
            where=where_clause,
        )
    else:
        raw_results = collection.query(
            query_embeddings=embeddings,
            n_results=2,
        )
    
    # 4. Process & Filter
    matches = process_matches(raw_results, original_sentences, threshold=0.40)
    
    return matches


# --- TEST ---
if __name__ == "__main__":
    tos_1 = "If a transfer of any Customer Data from Salesforce to Supplier occurs in connection with the Licensed Software then, notwithstanding anything to the contrary, Section 3(v) of these Software Terms shall apply."
    tos_2 = "Supplier will deliver the most current version of the Licensed Software to Salesforce via electronic delivery or load-and-leave services, and will not deliver tangible materials to Salesforce without Salesforce’s advance written consent"

    input_sentences = [tos_1, tos_2]

    t1 = time.time()
    
    # Run the full pipeline
    accepted_matches = find_violations(input_sentences)
    
    t2 = time.time()
    
    print(f"Total Pipeline Time: {t2 - t1:.4f} seconds")
    print(f"Accepted Matches: {len(accepted_matches)}")
    
    import json
    print(json.dumps(accepted_matches, indent=2))