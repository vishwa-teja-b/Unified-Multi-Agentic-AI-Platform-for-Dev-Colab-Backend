from fastapi import APIRouter, HTTPException, Request, Depends
from app.dependencies.auth import get_current_user_id
from app.dependencies.collections import get_project_plans_collection, get_projects_collection
from app.models.project_plan import ProjectPlan
from app.dto.project_planner_schema import UpdateTaskStatusRequest
from datetime import datetime

planned_projects_router = APIRouter(prefix="/api/planned-projects", tags=["Planned Projects"])

@planned_projects_router.get("/project/{project_id}", status_code=200)
async def get_project_plan(
    request: Request, 
    project_id: str, 
    auth_user_id: int = Depends(get_current_user_id)
):
    """
    Retrieve the saved project plan (roadmap) for a specific project.
    """
    project_plans_collection = get_project_plans_collection(request)
    
    # Fetch the plan
    plan = await project_plans_collection.find_one({"project_id": project_id})
    
    if not plan:
        raise HTTPException(status_code=404, detail="Project plan not found. Generate one first.")
    
    plan_obj = ProjectPlan(**plan)
    
    # Compute current sprint number based on dates
    now = datetime.utcnow()
    current_sprint_number = 1  # Default to first sprint
    for sprint in plan_obj.roadmap:
        start_date_str = sprint.get("start_date") if isinstance(sprint, dict) else None
        end_date_str = sprint.get("end_date") if isinstance(sprint, dict) else None
        sprint_num = sprint.get("sprint_number", 1) if isinstance(sprint, dict) else 1
        
        if start_date_str and end_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str)
                end_date = datetime.fromisoformat(end_date_str)
                if start_date <= now < end_date:
                    current_sprint_number = sprint_num
                    break
                elif now >= end_date:
                    current_sprint_number = sprint_num + 1
            except (ValueError, TypeError):
                pass
    
    # Clamp to valid range
    max_sprint = max(
        (s.get("sprint_number", 1) for s in plan_obj.roadmap if isinstance(s, dict)),
        default=1
    )
    current_sprint_number = min(current_sprint_number, max_sprint)
    
    # Return plan with current_sprint_number injected
    response = plan_obj.model_dump()
    response["current_sprint_number"] = current_sprint_number
    return response

@planned_projects_router.patch("/tasks", status_code=200)
async def update_task_status(
    request: Request,
    body: UpdateTaskStatusRequest,
    auth_user_id: int = Depends(get_current_user_id)
):
    """
    Update the status of a specific task within a project plan.
    """
    project_plans_collection = get_project_plans_collection(request)
    
    # Fetch the plan
    plan_data = await project_plans_collection.find_one({"project_id": body.project_id})
    
    if not plan_data:
        raise HTTPException(status_code=404, detail="Project plan not found")
    
    # Parse into model to work with objects
    plan = ProjectPlan(**plan_data)
    
    task_found = False
    
    # Iterate through roadmap to find the task
    for sprint in plan.roadmap:
        # Check uniqueness of task ID across sprints is not guaranteed by LLM, 
        # but we assume the frontend sends the correct one.
        # We will update the first matching ID.
        if "tasks" in sprint:
            for task in sprint["tasks"]:
                if task.get("id") == body.task_id:
                    task["status"] = body.status
                    task_found = True
                    break
        if task_found:
            break
            
    if not task_found:
        raise HTTPException(status_code=404, detail=f"Task {body.task_id} not found in roadmap")
    
    # Update timestamp
    plan.updated_at = datetime.utcnow()
    
    # Save back to DB
    # We update the 'roadmap' field specifically
    await project_plans_collection.update_one(
        {"project_id": body.project_id},
        {"$set": {
            "roadmap": plan.roadmap,
            "updated_at": plan.updated_at
        }}
    )
    
    return {"message": "Task status updated successfully", "task_id": body.task_id, "new_status": body.status}
