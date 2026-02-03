from pydantic import ConfigDict, BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

# Schema for the profiles collection in MongoDB

class Profile(BaseModel):
    """
    MongoDB Profile document schema.
    Links to MySQL users table via auth_user_id field.
    """

    model_config = ConfigDict(extra="ignore")

    # Link to MySQL users.id (foreign reference)
    auth_user_id: int = Field(..., description="MySQL users.id - links profile to authenticated user")
    
    # Basic Info
    name: str
    username: str
    email: EmailStr
    bio: str
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    
    # Location
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    timezone: str
    
    # Skills & Experience
    primary_skills: list[str] = Field(default_factory=list)
    secondary_skills: list[str] = Field(default_factory=list)
    experience_level: Optional[str] = None  # "junior", "intermediate", "senior"
    experience: list[dict] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    
    # Preferences
    interests: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    availability_hours: Optional[int] = None  # Weekly hours available
    open_to: list[str] = Field(default_factory=list)  # ["Side Projects", "Hackathons", "Startups"]
    preferred_role: Optional[str] = None
    
    # Social Links
    github: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None