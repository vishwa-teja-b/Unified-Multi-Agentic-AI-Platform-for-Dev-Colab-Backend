from pydantic import BaseModel
from typing import List, Optional, Any

class ProjectPlannerRequest(BaseModel):
    project_id: str

class UpdateTaskStatusRequest(BaseModel):
    project_id: str
    task_id: str
    status: str

class AddTaskRequest(BaseModel):
    project_id: str
    sprint_number: int
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    role: Optional[str] = None
    estimate: Optional[str] = None
    priority: Optional[str] = "Medium"
    status: str = "todo"

class UpdateTaskRequest(BaseModel):
    project_id: str
    task_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    role: Optional[str] = None
    estimate: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class ProjectPlannerResponse(BaseModel):
    project_id: str
    roadmap: List[Any]
    extracted_features: List[str]
    error: Optional[str] = None
