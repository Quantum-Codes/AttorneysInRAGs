from app.core.rule_loader import load_rules

def test_rules_loaded():
    rules = load_rules()
    assert len(rules) > 50  # sanity check

def test_rule_structure():
    rules = load_rules()
    rule = rules[0]

    assert "rule_id" in rule
    assert "domain" in rule
    assert "severity" in rule
    assert isinstance(rule["domain"], list)
    