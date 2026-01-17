def compute_severity(violations):
    score = sum(v["severity_weight"] for v in violations)

    if score > 1.5:
        return "HIGH"
    elif score > 0.7:
        return "MEDIUM"
    return "LOW"
