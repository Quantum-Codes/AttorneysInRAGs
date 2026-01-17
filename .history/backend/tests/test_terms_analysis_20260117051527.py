from app.core.clause_splitter import split_into_clauses
from app.core.ontology_mapper import map_domains
from app.core.rule_engine import evaluate_clauses
from app.core.severity_engine import compute_overall_severity
from app.core.risk_predictor import predict_future_risks
from app.utils.text_cleaner import clean_text
from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_terms.txt"

def test_real_terms_and_conditions():
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    text = clean_text(text)

    raw_clauses = split_into_clauses(text)

    clauses = []
    for c in raw_clauses:
        c["domains"] = map_domains(c["text"])
        clauses.append(c)

    violations = evaluate_clauses(clauses)
    overall_severity = compute_overall_severity(violations)
    future_risks = predict_future_risks(clauses)

    # ---- ASSERTIONS (THIS IS IMPORTANT) ----

    assert overall_severity in {"HIGH", "CRITICAL"}

    detected_domains = set()
    for c in clauses:
        detected_domains.update(c["domains"])

    assert "DATA_COLLECTION" in detected_domains
    assert "DATA_RETENTION" in detected_domains
    assert "DATA_SHARING" in detected_domains
    assert "CONSENT" in detected_domains

    assert len(violations) > 0
    assert any(v["severity"] == "CRITICAL" for v in violations)

    assert len(future_risks) > 0
