from pydantic import ConfigDict, BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Schema for the chats collection in MongoDB

class Message(BaseModel):
    """Embedded document or separate collection for individual messages."""
    sender_id: int = Field(..., description="MySQL users.id of the sender")
    text: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = Field(default=False)

class ChatRoom(BaseModel):
    """
    MongoDB Chat Room schema.
    Can be a 'direct' message room between 2 people,
    or a 'team' message room for an entire team.
    """
    model_config = ConfigDict(extra="ignore")

    room_type: str = Field(..., description="'direct' or 'team'")
    
    # User IDs of all participants (MySQL users.id)
    participants: List[int] = Field(default_factory=list)
    
    # If room_type == 'team', store the team_id (which is usually the project_id string)
    team_id: Optional[str] = None

    # Redundant denormalization to keep chat list loading fast
    last_message: Optional[Message] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
