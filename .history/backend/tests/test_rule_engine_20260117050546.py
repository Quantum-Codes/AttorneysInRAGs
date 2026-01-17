from app.core.rule_engine import evaluate_clauses

def test_rule_matching():
    clauses = [
        {
            "clause_id": "C1",
            "text": "We retain personal data indefinitely.",
            "domains": ["DATA_RETENTION"]
        }
    ]

    violations = evaluate_clauses(clauses)

    assert len(violations) > 0
    assert violations[0]["clause_id"] == "C1"
    assert "DATA_RETENTION" in violations[0]["matched_domains"]
    