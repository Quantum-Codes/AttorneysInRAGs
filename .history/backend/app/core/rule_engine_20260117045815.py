import json

with open("app/knowledge/laws.json") as f:
    LAWS = json.load(f)

def evaluate_rules(clauses):
    violations = []

    for clause in clauses:
        for law in LAWS:
            if law["category"] in clause["tags"]:
                violations.append({
                    "law": law["law"],
                    "section": law["section"],
                    "clause_id": clause["clause_id"],
                    "severity_weight": law["severity_weight"],
                    "explanation": f"Clause may violate {law['requirement']}"
                })
    return violations
