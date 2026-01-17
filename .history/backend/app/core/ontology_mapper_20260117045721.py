ONTOLOGY = {
    "data": ["data", "information", "personal"],
    "retention": ["retain", "store", "keep"],
    "consent": ["consent", "agree", "permission"],
    "sharing": ["share", "third party"]
}

def map_ontology(clause_text: str):
    tags = []
    lower = clause_text.lower()

    for tag, keywords in ONTOLOGY.items():
        if any(k in lower for k in keywords):
            tags.append(tag)

    return tags
