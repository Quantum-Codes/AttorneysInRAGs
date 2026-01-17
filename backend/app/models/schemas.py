from pydantic import BaseModel
from typing import List, Optional

class Clause(BaseModel):
    clause_id: str
    section: str
    text: str
    tags: List[str]

class Violation(BaseModel):
    law: str
    section: str
    clause_id: str
    severity: str
    explanation: str

class RiskPrediction(BaseModel):
    risk: str
    confidence: float

class AnalysisResult(BaseModel):
    website: str
    overall_risk: str
    violations: List[Violation]
    future_risks: List[RiskPrediction]
