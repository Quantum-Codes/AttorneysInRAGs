from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
from backend.module_2 import RelevanceFilter
from backend.module_3_4 import find_violations
from backend.module_5 import run_inference
import json

app = FastAPI(title="AttorneysInRAGs API")

legal_filter = RelevanceFilter()

class TextInput(BaseModel):
    text: str

class Violation(BaseModel):
    violating_rule: str
    actual_rule: str
    source: str
    severity: str
    reason: str

class Aggregations(BaseModel):
    total_violations: int
    critical_severity: int
    high_severity: int
    medium_severity: int
    low_severity: int

class AnalysisOutput(BaseModel):
    summary: str
    aggregations: Aggregations
    violations: list[Violation]

def build_response(accepted_matches: list[dict], inference_result: dict) -> dict:
    analysis = inference_result.get("analysis", [])
    summary = inference_result.get("summary", "Analysis complete.")
    
    violations = []
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    
    for item in analysis:
        idx = item.get("id", 1) - 1
        if item.get("violated") and not item.get("irrelevant"):
            if 0 <= idx < len(accepted_matches):
                match = accepted_matches[idx]
                sev = match.get("severity", "MEDIUM").upper()
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                
                violations.append({
                    "violating_rule": match.get("TOS_text", ""),
                    "actual_rule": match.get("raw_law", ""),
                    "source": f"[{match.get('rule_id', 'Unknown')}] {', '.join(match.get('domain', []))}",
                    "severity": sev,
                    "reason": item.get("reason", ""),
                })
    
    total = len(violations)
    
    return {
        "summary": summary,
        "aggregations": {
            "total_violations": total,
            "critical_severity": severity_counts.get("CRITICAL", 0),
            "high_severity": severity_counts.get("HIGH", 0),
            "medium_severity": severity_counts.get("MEDIUM", 0),
            "low_severity": severity_counts.get("LOW", 0),
        },
        "violations": violations,
    }

@app.post("/analyze", response_model=AnalysisOutput)
def analyze_text(input_data: TextInput):
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        clean_chunks = legal_filter.process_document(input_data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")
    
    if not clean_chunks:
        raise HTTPException(status_code=422, detail="No valid legal clauses found")
    
    try:
        accepted_matches = find_violations(clean_chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Violation detection failed: {str(e)}")
    
    if not accepted_matches:
        return AnalysisOutput(
            summary="No potential violations found.",
            aggregations=Aggregations(
                total_violations=0,
                critical_severity=0,
                high_severity=0,
                medium_severity=0,
                low_severity=0,
            ),
            violations=[],
        )
    
    inference_result = run_inference(accepted_matches)
    
    if "error" in inference_result:
        raise HTTPException(status_code=503, detail=f"LLM inference failed: {inference_result.get('error')}")
    
    try:
        return build_response(accepted_matches, inference_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response building failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
