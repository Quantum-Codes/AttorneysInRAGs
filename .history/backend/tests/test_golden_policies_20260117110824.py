from pathlib import Path
from app.core.clause_splitter import split_into_clauses
from app.core.ontology_mapper import map_domains
from app.core.rule_engine import evaluate_clauses
from app.core.severity_engine import compute_overall_severity

BASE = Path(__file__).parent / "policies"

def analyze(text):
    clauses = []
    for c in split_into_clauses(text):
        c["domains"] = map_domains(c["text"])
        clauses.append(c)
    return compute_overall_severity(evaluate_clauses(clauses))

def test_good_policy():
    text = (BASE / "good_policy.txt").read_text()
    assert analyze(text) in {"LOW", "MEDIUM"}

def test_bad_policy():
    text = (BASE / "bad_policy.txt").read_text()
    assert analyze(text) == "CRITICAL"
