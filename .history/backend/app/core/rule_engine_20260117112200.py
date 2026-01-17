from app.core.rule_loader import load_rules
from app.core.evidence_builder import build_evidence
from app.core.confidence_engine import compute_confidence
from app.core.compliance_guard import is_compliant_clause

def evaluate_clauses(clauses):
    rules = load_rules()
    violations = []

    for clause in clauses:

        # ✅ Skip compliant clauses
        if is_compliant_clause(clause):
            continue

        for rule in rules:
            if set(rule["domain"]) & set(clause["domains"]):
                violations.append({
                    "rule_id": rule["rule_id"],
                    "severity": rule["severity"],
                    "confidence": compute_confidence(clause, rule),
                    "evidence": build_evidence(clause, rule),
                    "rationale": rule["rationale"],
                    "clause_id": clause.get("clause_id")
                })

    return violations
