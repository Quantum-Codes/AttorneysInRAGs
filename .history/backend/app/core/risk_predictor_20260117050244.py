def predict_future_risks(clauses):
    risks = []

    for c in clauses:
        d = set(c["domains"])

        if {"DATA_RETENTION", "CONSENT"} <= d:
            risks.append({
                "risk": "Indefinite data retention after consent withdrawal",
                "confidence": 0.82
            })

        if {"CHILDREN_DATA", "DATA_COLLECTION"} <= d:
            risks.append({
                "risk": "Regulatory action for unlawful child data processing",
                "confidence": 0.9
            })

        if {"SECURITY_PRACTICES", "SENSITIVE_DATA"} <= d:
            risks.append({
                "risk": "High breach impact due to sensitive data exposure",
                "confidence": 0.85
            })

    return risks
