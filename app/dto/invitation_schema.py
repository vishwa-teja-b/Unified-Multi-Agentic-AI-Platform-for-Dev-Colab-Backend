from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime

class SendInvitation(BaseModel):
    """
    DTO for sending invitation after AI recommends some teammates for a project
    """
    project_id : str = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    sender_id : int
    receiver_id : Optional[int] = None
    receiver_username : Optional[str] = None
    project_title : str
    role : str
    status : str = "PENDING"# PENDING / ACCEPTED / REJECTED

class UpdateInvitation(BaseModel):

    invitation_id : str
    status : str

class JoinRequest(BaseModel):
    """
    DTO for a non-owner requesting to join a project
    """
    project_id : str
    role : str  # Role the user wants to play
    message : Optional[str] = None  # Optional cover message