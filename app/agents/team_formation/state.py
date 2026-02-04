from typing import TypedDict, List, Optional

class TeamFormationState(TypedDict):
    # Input
    project_id: str
    project_title: str
    required_skills: List[str]
    team_size: int
    timeline: str
    
    # Intermediate
    roles: List[dict]           # From role analyzer
    candidates: List[dict]      # From skill matcher
    
    # Output
    recommendations: List[dict] # Final scored candidates
    error: Optional[str]