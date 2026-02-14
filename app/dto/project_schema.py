from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal
from datetime import datetime


class TeamSize(BaseModel):
    """Team size range"""
    min: int = Field(default=1, ge=1)
    max: int = Field(default=5, ge=1)


class ProjectCreateRequest(BaseModel):
    """
    Request schema for creating a project.
    auth_user_id is NOT included - it comes from the JWT token.
    """
    # Basic Info
    title: str = Field(..., min_length=3, max_length=100)
    category: Literal["Full Stack", "Frontend", "Backend", "Mobile", "Data Science", "AI/ML", "Other"]
    description: str = Field(..., min_length=10, max_length=2000)
    
    # Requirements
    features: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list, min_length=1)
    
    # Team
    team_size: TeamSize = Field(default_factory=TeamSize)
    
    # Project Info
    complexity: Literal["Easy", "Medium", "Hard"]
    estimated_duration: str = Field(..., description="e.g., '2-3 months', '6 weeks'")


class ProjectResponse(BaseModel):
    """
    Response schema for project operations.
    Includes id and auth_user_id for client reference.
    """
    model_config = ConfigDict(extra="ignore")
    
    id: str  # MongoDB _id as string
    auth_user_id: int  # MySQL users.id - project owner
    
    # Basic Info
    title: str
    category: str
    description: str
    
    # Requirements
    features: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    
    # Team
    team_size: TeamSize
    team_id: Optional[str] = None  # Reference to teams collection

    # team_members: list[str] = Field(default_factory=list)
    
    # Project Info
    complexity: str
    estimated_duration: str
    status: str  # "Open", "In Progress", "Completed"
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProjectUpdateRequest(BaseModel):
    """
    Request schema for updating a project.
    All fields are optional for partial updates.
    """
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    category: Optional[Literal["Full Stack", "Frontend", "Backend", "Mobile", "Data Science", "AI/ML", "Other"]] = None
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    features: Optional[list[str]] = None
    required_skills: Optional[list[str]] = None
    team_size: Optional[TeamSize] = None
    complexity: Optional[Literal["Easy", "Medium", "Hard"]] = None
    estimated_duration: Optional[str] = None
    status: Optional[Literal["Open", "In Progress", "Completed"]] = None
