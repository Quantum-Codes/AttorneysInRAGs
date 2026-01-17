import uuid

def split_into_clauses(text: str):
    sentences = text.split(". ")
    clauses = []

    for sent in sentences:
        if len(sent) > 40:
            clauses.append({
                "clause_id": str(uuid.uuid4())[:8],
                "section": "GENERAL",
                "text": sent.strip(),
            })
    return clauses
