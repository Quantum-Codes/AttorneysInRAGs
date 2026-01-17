from app.core.risk_predictor import predict_future_risks

def test_retention_consent_risk():
    clauses = [
        {
            "domains": ["DATA_RETENTION", "CONSENT"]
        }
    ]

    risks = predict_future_risks(clauses)

    assert len(risks) > 0
    assert risks[0]["confidence"] >= 0.8

def test_no_risk():
    clauses = [
        {
            "domains": ["USER_RIGHTS"]
        }
    ]

    risks = predict_future_risks(clauses)
    assert risks == []
