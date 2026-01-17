import json
from app.core.domain_normalizer import normalize_domain

def load_rules():
    with open("app/knowledge/database.json", "r", encoding="utf-8") as f:
        rules = json.load(f)

    for r in rules:
        r["domain"] = [normalize_domain(d) for d in r["domain"]]
        r["severity"] = r["severity"].upper()

    return rules
