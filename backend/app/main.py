from fastapi import FastAPI
from app.api.analyze import router

app = FastAPI(title="Legal Compliance Analyzer")

app.include_router(router)

@app.get("/")
def root():
    return {"status": "Legal Analyzer running"}
