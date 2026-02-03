from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# Users table using SQLMODEL

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)  # Email verified
    profile_complete: bool = Field(default=False)  # Profile wizard completed
    refresh_token: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)