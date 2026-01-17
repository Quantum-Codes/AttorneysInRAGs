from app.core.rule_loader import load_rules
from app.core.evidence_builder import build_evidence
from app.core.confidence_engine import compute_confidence

def evaluate_clauses(clauses):
    rules = load_rules()
    violations = []

    for clause in clauses:
        for rule in rules:
            if set(rule["domain"]) & set(clause["domains"]):
                evidence = build_evidence(clause, rule)
                confidence = compute_confidence(clause, rule)

                violations.append({
                    "rule_id": rule["rule_id"],
                    "severity": rule["severity"],
                    "confidence": confidence,
                    "evidence": evidence,
                    "rationale": rule["rationale"]
                })

    return violations
