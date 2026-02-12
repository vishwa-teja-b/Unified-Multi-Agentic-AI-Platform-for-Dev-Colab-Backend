from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Invitation(SQLModel, table=True):
    id : Optional[int] = Field(default=None, primary_key=True)
    project_id : str = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    sender_id : int
    receiver_id : int
    project_title : str
    role : str
    status : str # PENDING / ACCEPTED / REJECTED
    created_at : datetime = Field(default_factory=datetime.utcnow)
    updated_at : datetime = Field(default_factory=datetime.utcnow)