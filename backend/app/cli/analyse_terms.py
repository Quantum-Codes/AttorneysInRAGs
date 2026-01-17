import sys
from app.core.clause_splitter import split_into_clauses
from app.core.ontology_mapper import map_domains
from app.core.rule_engine import evaluate_clauses
from app.core.severity_engine import compute_overall_severity
from app.core.risk_predictor import predict_future_risks
from app.utils.text_cleaner import clean_text

def analyze_terms(text: str):
    text = clean_text(text)

    clauses = []
    for c in split_into_clauses(text):
        c["domains"] = map_domains(c["text"])
        clauses.append(c)

    violations = evaluate_clauses(clauses)
    severity = compute_overall_severity(violations)
    risks = predict_future_risks(clauses)

    print("\n================ ANALYSIS RESULT ================\n")
    print(f"OVERALL SEVERITY: {severity}\n")

    print("📌 CLAUSES & DOMAINS:")
    for c in clauses:
        print(f"- {c['text']}")
        print(f"  Domains: {c['domains']}\n")

    print("⚖️ VIOLATIONS:")
    for v in violations:
        print(f"- Rule: {v['rule_id']}")
        print(f"  Severity: {v['severity']}")
        print(f"  Matched Domains: {v['matched_domains']}")
        print(f"  Rationale: {v['rationale']}\n")

    print("🔮 FUTURE RISKS:")
    for r in risks:
        print(f"- {r['risk']} (confidence={r['confidence']})")

if __name__ == "__main__":
    print("Paste Terms & Conditions text.")
    print("End input with CTRL+Z + Enter (Windows) or CTRL+D (Linux/macOS):\n")

    input_text = sys.stdin.read()
    analyze_terms(input_text)
