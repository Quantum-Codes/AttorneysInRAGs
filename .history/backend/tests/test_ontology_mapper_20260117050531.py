from app.core.ontology_mapper import map_domains

def test_data_retention_detection():
    text = "We retain user data for as long as necessary."
    domains = map_domains(text)
    assert "DATA_RETENTION" in domains

def test_consent_and_sharing_detection():
    text = "We may share your data with third parties after consent."
    domains = map_domains(text)
    assert "DATA_SHARING" in domains
    assert "CONSENT" in domains

def test_children_data_detection():
    text = "Parental consent is required for children under 18."
    domains = map_domains(text)
    assert "CHILDREN_DATA" in domains
