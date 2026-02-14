from pydantic import BaseModel
from typing import List, Optional, Any

class ProjectPlannerRequest(BaseModel):
    project_id: str

class ProjectPlannerResponse(BaseModel):
    project_id: str
    roadmap: List[Any]
    extracted_features: List[str]
    error: Optional[str] = None
