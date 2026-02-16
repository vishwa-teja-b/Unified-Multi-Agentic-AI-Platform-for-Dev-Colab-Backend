from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class FileItem(BaseModel):
    id: str
    name: str
    content: str
    language: Optional[str] = None

class Participant(BaseModel):
    user_id: str
    username: str
    avatar: Optional[str] = None
    role: str = "viewer"  # viewer, editor, owner

class Room(BaseModel):
    """
    MongoDB Room document schema.
    Stores the state of a collaboration session.
    """
    room_id: str  # Can be same as project_id
    project_id: str
    
    # Session State
    participants: List[Participant] = []
    
    # File System State
    files: List[FileItem] = []
    fileStructure: Dict[str, Any] = {}
    
    # Whiteboard State
    drawingData: Optional[Dict[str, Any]] = None
    
    # Chat History (Optional, could be separate collection if large)
    # messages: List[Message] = [] 

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class RoomCreate(BaseModel):
    project_id: str
    created_by: str

class RoomResponse(BaseModel):
    room_id: str
    project_id: str
    participants: List[Participant]
    created_at: datetime
