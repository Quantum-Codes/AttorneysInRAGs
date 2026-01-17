from app.core.domain_normalizer import normalize_domain

def test_normalize_domain():
    assert normalize_domain("data_retention") == "DATA_RETENTION"
    assert normalize_domain(" Data_Sharing ") == "DATA_SHARING"
    assert normalize_domain("SECURITY_PRACTICES") == "SECURITY_PRACTICES"
