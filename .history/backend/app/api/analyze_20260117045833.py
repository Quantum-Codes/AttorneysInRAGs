from fastapi import APIRouter
from app.core.crawler import fetch_legal_text
from app.utils.text_cleaner import clean_text
from app.core.clause_splitter import split_into_clauses
from app.core.ontology_mapper import map_ontology
from app.core.rule_engine import evaluate_rules
from app.core.severity_engine import compute_severity
from app.core.risk_predictor import predict_risks

router = APIRouter()

@router.post("/analyze")
def analyze_website(url: str):
    raw_text = fetch_legal_text(url)
    text = clean_text(raw_text)

    clauses_raw = split_into_clauses(text)

    clauses = []
    for c in clauses_raw:
        c["tags"] = map_ontology(c["text"])
        clauses.append(c)

    violations = evaluate_rules(clauses)
    overall_risk = compute_severity(violations)
    future_risks = predict_risks(clauses)

    return {
        "website": url,
        "overall_risk": overall_risk,
        "violations": violations,
        "future_risks": future_risks
    }
