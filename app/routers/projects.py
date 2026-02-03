from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime
from bson import ObjectId
from app.dto.project_schema import ProjectCreateRequest, ProjectResponse, ProjectUpdateRequest
from app.dependencies.collections import get_projects_collection
from app.dependencies.auth import get_current_user_id

project_router = APIRouter(prefix="/api/projects", tags=["Projects"])

@project_router.post("/create-project", response_model=ProjectResponse, status_code=201)
async def create_project(
    request: Request, 
    project: ProjectCreateRequest,
    auth_user_id: int = Depends(get_current_user_id)
):
    projects_collection = get_projects_collection(request)

    # Check if project already exists for this authenticated user
    existing_project = await projects_collection.find_one({"auth_user_id": auth_user_id})
    if existing_project:
        raise HTTPException(status_code=400, detail="Project already exists for this user")
    
    # Convert to dict and add auth_user_id from JWT
    project_dict = project.model_dump()
    project_dict["auth_user_id"] = auth_user_id
    project_dict["status"] = "Open"  # Default status for new projects
    project_dict["team_members"] = []  # Empty team initially
    project_dict["created_at"] = datetime.utcnow()
    project_dict["updated_at"] = None
    
    result = await projects_collection.insert_one(project_dict)

    # Fetch the created project
    created_project = await projects_collection.find_one({"_id": result.inserted_id})
    
    # Convert MongoDB _id to string for response
    created_project["id"] = str(created_project.pop("_id"))

    # Index the project in Pinecone
    # index_project(created_project)

    return ProjectResponse(**created_project)



@project_router.get("/my-projects", response_model=list[ProjectResponse], status_code=200)
async def get_projects(request: Request, auth_user_id: int = Depends(get_current_user_id)):
    projects_collection = get_projects_collection(request)
    projects = await projects_collection.find({"auth_user_id": auth_user_id}).to_list(length=None)
    if not projects:
        raise HTTPException(status_code=404, detail="Projects not found")
    for project in projects:
        project["id"] = str(project.pop("_id"))
    return [ProjectResponse(**project) for project in projects]



@project_router.get("/project/{project_id}", response_model = ProjectResponse, status_code=200)
async def get_project_by_id(request: Request, project_id: str, auth_user_id: int = Depends(get_current_user_id)):
    projects_collection = get_projects_collection(request)
    project = await projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project["id"] = str(project.pop("_id"))
    return ProjectResponse(**project)



@project_router.patch("/project/{project_id}", response_model = ProjectResponse, status_code=200)
async def update_project(
    request: Request, 
    project_id: str, 
    project_data: ProjectUpdateRequest, 
    auth_user_id: int = Depends(get_current_user_id)
):
    projects_collection = get_projects_collection(request)
    
    # Check if project exists
    existing_project = await projects_collection.find_one({"_id": ObjectId(project_id)})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if the project belongs to the authenticated user
    if existing_project["auth_user_id"] != auth_user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this project")
    
    # Use the new data from request, not the existing project
    update_dict = project_data.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    # Update the project
    await projects_collection.update_one(
        {"_id": ObjectId(project_id)}, 
        {"$set": update_dict}
    )
    
    # Fetch the updated project
    updated_project = await projects_collection.find_one({"_id": ObjectId(project_id)})
    
    # Convert MongoDB _id to string for response
    updated_project["id"] = str(updated_project.pop("_id"))
    
    # Re-index with new skills/data if needed
    # index_project(updated_project)
    
    return ProjectResponse(**updated_project)



@project_router.delete("/project/{project_id}", status_code=200)
async def delete_project(request: Request, project_id: str, auth_user_id: int = Depends(get_current_user_id)):
    projects_collection = get_projects_collection(request)
    project = await projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project["auth_user_id"] != auth_user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this project")
    await projects_collection.delete_one({"_id": ObjectId(project_id)})
    return {"message": "Project deleted successfully"}