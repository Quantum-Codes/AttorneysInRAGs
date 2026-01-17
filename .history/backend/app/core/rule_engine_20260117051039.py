from app.core.rule_loader import load_rules

def evaluate_clauses(clauses):
    rules = load_rules()   # ← LOAD AT RUNTIME, NOT IMPORT TIME
    violations = []

    for clause in clauses:
        clause_domains = set(clause["domains"])

        for rule in rules:
            rule_domains = set(rule["domain"])

            if clause_domains & rule_domains:
                violations.append({
                    "rule_id": rule["rule_id"],
                    "law_text": rule["raw_law"],
                    "matched_domains": list(clause_domains & rule_domains),
                    "severity": rule["severity"],
                    "clause_id": clause["clause_id"],
                    "rationale": rule["rationale"]
                })

    return violations
