from typing import TypedDict, List, Optional
from pydantic import Field

class ProjectPlannerState(TypedDict):
    # Input
    project_id: str 
    title: str
    category: str
    description: str
    
    # Requirements
    features: List[str]
    required_skills: List[str]
    
    # Team
    team_size: dict # e.g. {"min": 2, "max": 5}
    team_members: List[dict] # List of team members with roles/skills
    team_id: Optional[str]

    # Project Info
    complexity: str
    estimated_duration: str
    status: str
    
    # Intermediate
    extracted_features: List[str]
    milestones: List[dict]
    
    # Output
    roadmap: List[dict] # Final list of sprints/tasks
    error: Optional[str]