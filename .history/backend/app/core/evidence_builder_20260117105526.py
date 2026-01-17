def build_evidence(clause, rule):
    matched_terms = []

    for domain in rule["domain"]:
        if domain in clause["domains"]:
            matched_terms.append(domain)

    return {
        "clause_text": clause["text"],
        "matched_domains": matched_terms,
        "rule_id": rule["rule_id"],
        "law_excerpt": rule["raw_law"]
    }
