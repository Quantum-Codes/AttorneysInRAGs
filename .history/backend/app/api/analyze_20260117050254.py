from fastapi import APIRouter
from app.core.crawler import fetch_legal_text
from app.utils.text_cleaner import clean_text
from app.core.clause_splitter import split_into_clauses
from app.core.ontology_mapper import map_domains
from app.core.rule_engine import evaluate_clauses
from app.core.severity_engine import compute_overall_severity
from app.core.risk_predictor import predict_future_risks

router = APIRouter()

@router.post("/analyze")
def analyze(url: str):
    raw = fetch_legal_text(url)
    text = clean_text(raw)

    raw_clauses = split_into_clauses(text)
    clauses = []

    for c in raw_clauses:
        c["domains"] = map_domains(c["text"])
        clauses.append(c)

    violations = evaluate_clauses(clauses)
    overall_risk = compute_overall_severity(violations)
    future_risks = predict_future_risks(clauses)

    return {
        "website": url,
        "overall_risk": overall_risk,
        "violations": violations,
        "future_risks": future_risks
    }
