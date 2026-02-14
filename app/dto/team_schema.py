from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class TeamMemberResponse(BaseModel):
    """Response DTO for an individual team member."""
    user_id: int
    username: Optional[str] = None
    role: str
    joined_at: datetime


class TeamResponse(BaseModel):
    """
    Response DTO for a team document.
    Returned when fetching team info for a project.
    """
    model_config = ConfigDict(extra="ignore")

    id: str  # MongoDB _id as string
    project_id: str
    project_title: str
    project_owner: int

    team_members: list[TeamMemberResponse] = Field(default_factory=list)

    created_at: datetime
