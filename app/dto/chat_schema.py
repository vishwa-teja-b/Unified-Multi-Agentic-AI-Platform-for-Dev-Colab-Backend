from pydantic import BaseModel

class NewChatRequest(BaseModel):
    other_user_id: int

class TeamChatRequest(BaseModel):
    team_id: str

class SendMessageRequest(BaseModel):
    text: str