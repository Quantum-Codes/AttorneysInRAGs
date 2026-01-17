def compute_confidence(clause, rule):
    text = clause["text"].lower()

    if any(k.lower() in text for k in rule["domain"]):
        return 0.9

    if clause["domains"]:
        return 0.6

    return 0.4
