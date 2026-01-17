COMPLIANT_PATTERNS = {
    "DATA_COLLECTION": [
        "only with consent",
        "with user consent",
        "after consent"
    ],
    "DATA_RETENTION": [
        "deleted once",
        "erase after",
        "retained only as long as necessary"
    ]
}
#TODO add more of this kind 

def is_compliant_clause(clause):
    text = clause["text"].lower()

    for domain, patterns in COMPLIANT_PATTERNS.items():
        if domain in clause["domains"]:
            if any(p in text for p in patterns):
                return True

    return False
