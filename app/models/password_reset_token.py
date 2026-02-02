from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class PasswordResetToken(SQLModel, table=True):
    id : Optional[int] = Field(default=None, primary_key=True)
    user_id : int = Field(foreign_key="user.id", index=True, ondelete="CASCADE")
    otp  :str
    expires_at : datetime
    is_used : bool = False
    created_at : datetime = Field(default_factory=datetime.utcnow)