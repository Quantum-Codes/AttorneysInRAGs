from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[2]

def load_json(name):
    with open(BASE_DIR / "app" / "config" / name, encoding="utf-8") as f:
        return json.load(f)

SEVERITY_POLICY = load_json("severity_policy.json")
DOMAIN_POLICY = load_json("domain_policy.json")
