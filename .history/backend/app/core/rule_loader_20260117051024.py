import json
from pathlib import Path
from app.core.domain_normalizer import normalize_domain

# Resolve path relative to THIS file
BASE_DIR = Path(__file__).resolve().parents[1]   # backend/app
DB_PATH = BASE_DIR / "knowledge" / "database.json"

def load_rules():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"database.json not found at {DB_PATH}")

    with open(DB_PATH, "r", encoding="utf-8") as f:
        rules = json.load(f)

    for r in rules:
        r["domain"] = [normalize_domain(d) for d in r["domain"]]
        r["severity"] = r["severity"].upper()

    return rules
