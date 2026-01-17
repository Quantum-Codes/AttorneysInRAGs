import requests
from bs4 import BeautifulSoup

LEGAL_PATHS = ["/privacy", "/terms", "/legal"]

def fetch_legal_text(url: str) -> str:
    for path in LEGAL_PATHS:
        try:
            r = requests.get(url + path, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                return soup.get_text(separator=" ")
        except Exception:
            continue
    raise Exception("Legal page not found")
