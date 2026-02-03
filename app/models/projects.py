from pydantic import ConfigDict, BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

# Schema for the projects collection in MongoDB

class Project(BaseModel):
    """
    MongoDB Project document schema.
    Links to MySQL users table via auth_user_id field.
    """

    model_config = ConfigDict(extra="ignore")

    # Link to MySQL users.id (foreign reference)
    auth_user_id: int = Field(..., description="MySQL users.id - links profile to authenticated user")
    
    # Basic Info
    title: str
    category: str = Field(description="Full Stack", "Frontend", "Backend", "Mobile", "Data Science", "AI/ML", "Other")
    description: str
    
    features: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)

    team_size : dict[str, int] = Field(default_factory=dict)
    
    complexity : str = Field(..., description="Easy", "Medium", "Hard")
    estimated_duration : str

    status : str = Field(..., description="Open", "In Progress", "Completed")

    team_members : list[dict] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None