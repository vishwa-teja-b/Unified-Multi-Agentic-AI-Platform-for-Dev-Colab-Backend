from pydantic import ConfigDict, BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any

class ProjectPlan(BaseModel):
    """
    MongoDB ProjectPlan document schema.
    Stores the generated roadmap and tasks for a project.
    """
    model_config = ConfigDict(extra="ignore")

    project_id: str = Field(..., description="Reference to the project ID")
    
    # The generated roadmap structure
    roadmap: List[Any] = Field(default_factory=list, description="List of sprints and tasks")
    
    extracted_features: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
