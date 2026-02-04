from pydantic import BaseModel
from typing import List, Optional

class TeamFormationRequest(BaseModel):
    project_id: str
    project_title: str
    required_skills: List[str]
    team_size: int
    timeline: str

class TeamFormationResponse(BaseModel):
    recommendations: list[dict]
    error: Optional[str]