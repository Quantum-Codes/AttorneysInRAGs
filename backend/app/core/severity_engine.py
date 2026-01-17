SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def compute_overall_severity(violations):
    if not violations:
        return "LOW"

    severities = {v["severity"] for v in violations}

    # Dominant severity logic (legal-first)
    if "CRITICAL" in severities:
        return "CRITICAL"
    if "HIGH" in severities:
        return "HIGH"
    if "MEDIUM" in severities:
        return "MEDIUM"

    return "LOW"
