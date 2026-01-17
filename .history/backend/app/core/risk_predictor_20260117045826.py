def predict_risks(clauses):
    risks = []

    for clause in clauses:
        if "data" in clause["tags"] and "retention" in clause["tags"]:
            risks.append({
                "risk": "Potential long-term personal data misuse",
                "confidence": 0.78
            })

    return risks
