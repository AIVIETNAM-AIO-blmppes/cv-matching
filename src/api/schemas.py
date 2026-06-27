from pydantic import BaseModel
from typing import List, Dict, Any

class JDRequest(BaseModel):
    job_title: str
    required_skills: List[str]

class MatchResponse(BaseModel):
    candidate_id: str
    filename: str
    match_score: float
    extracted_skills: List[str]
    match_details: Dict[str, Any]