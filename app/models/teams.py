from pydantic import ConfigDict, BaseModel, Field
from datetime import datetime
from typing import Optional

# Schema for the teams collection in MongoDB

class TeamMember(BaseModel):
    """Embedded document for a single team member."""
    user_id: int = Field(..., description="MySQL users.id")
    role: str = Field(..., description="Member role, e.g. Owner, Frontend Developer")
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class Team(BaseModel):
    """
    MongoDB Team document schema.
    Created atomically alongside a project.
    """

    model_config = ConfigDict(extra="ignore")

    project_id: str = Field(..., description="String ID of the associated project")
    project_title: str
    project_owner: int = Field(..., description="MySQL users.id of the project owner")

    team_members: list[TeamMember] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
