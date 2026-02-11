from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime


class ProfileCreateRequest(BaseModel):
    """
    Request schema for creating a profile.
    auth_user_id is NOT included - it comes from the JWT token.
    """
    # Basic Info
    name: str
    username: str
    email: EmailStr
    bio: str
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    # auth_user_id removed as it comes from token

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
    availability_hours: Optional[int] = None
    open_to: list[str] = Field(default_factory=list)
    preferred_role: Optional[str] = None
    
    # Social Links
    github: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None


class ProfileResponse(BaseModel):
    """
    Response schema for profile operations.
    Includes id and auth_user_id for client reference.
    """
    model_config = ConfigDict(extra="ignore")
    
    id: str  # MongoDB _id as string
    auth_user_id: int  # MySQL users.id
    
    # Basic Info
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
    experience_level: Optional[str] = None
    experience: list[dict] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    
    # Preferences
    interests: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    availability_hours: Optional[int] = None
    open_to: list[str] = Field(default_factory=list)
    preferred_role: Optional[str] = None
    
    # Social Links
    github: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None

