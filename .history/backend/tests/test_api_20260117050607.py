from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_endpoint(monkeypatch):
    # Mock crawler to avoid real HTTP calls
    def mock_fetch(_):
        return "We retain user data and share it with third parties."

    monkeypatch.setattr(
        "app.api.analyze.fetch_legal_text",
        mock_fetch
    )

    response = client.post("/analyze?url=https://example.com")

    assert response.status_code == 200
    body = response.json()

    assert "overall_risk" in body
    assert "violations" in body
    assert "future_risks" in body
