SEVERITY_WEIGHTS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 5
}

def compute_overall_severity(violations):
    score = sum(SEVERITY_WEIGHTS[v["severity"]] for v in violations)

    if score >= 20:
        return "CRITICAL"
    elif score >= 10:
        return "HIGH"
    elif score >= 5:
        return "MEDIUM"
    return "LOW"
