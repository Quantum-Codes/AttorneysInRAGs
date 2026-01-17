from app.core.severity_engine import compute_overall_severity

def test_low_severity():
    violations = [{"severity": "LOW"}]
    assert compute_overall_severity(violations) == "LOW"

def test_medium_severity():
    violations = [{"severity": "MEDIUM"}, {"severity": "LOW"}]
    assert compute_overall_severity(violations) == "MEDIUM"

def test_critical_severity():
    violations = [
        {"severity": "CRITICAL"},
        {"severity": "HIGH"},
        {"severity": "HIGH"}
    ]
    assert compute_overall_severity(violations) == "CRITICAL"
    