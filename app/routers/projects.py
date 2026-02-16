from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime
from bson import ObjectId
from app.dto.project_schema import ProjectCreateRequest, ProjectResponse, ProjectUpdateRequest
from app.models.teams import Team, TeamMember
from app.dependencies.collections import get_projects_collection, get_teams_collection
from app.dependencies.auth import get_current_user_id
from app.vector_stores.pinecone_db import index_project, delete_project_index, search_projects as pinecone_search_projects


project_router = APIRouter(prefix="/api/projects", tags=["Projects"])

@project_router.post("/create-project", response_model=ProjectResponse, status_code=201)
async def create_project(
    request: Request, 
    project: ProjectCreateRequest,
    auth_user_id: int = Depends(get_current_user_id)
):
    projects_collection = get_projects_collection(request)
    teams_collection = get_teams_collection(request)
    
    # Convert to dict and add auth_user_id from JWT
    project_dict = project.model_dump()
    project_dict["auth_user_id"] = auth_user_id
    project_dict["status"] = "Open"  # Default status for new projects
    project_dict["team_id"] = None  # Will be set after team creation
    project_dict["created_at"] = datetime.utcnow()
    project_dict["updated_at"] = None
    
    # Step 1: Insert project
    result = await projects_collection.insert_one(project_dict)
    project_id = str(result.inserted_id)

    # Step 2: Create team with owner as first member
    try:
        owner_member = TeamMember(
            user_id=auth_user_id,
            role="Owner",
            joined_at=datetime.utcnow()
        )

        team = Team(
            project_id=project_id,
            project_title=project_dict["title"],
            project_owner=auth_user_id,
            team_members=[owner_member],
            created_at=datetime.utcnow()
        )
        team_result = await teams_collection.insert_one(team.model_dump())
        team_id = str(team_result.inserted_id)

        # Step 3: Update project with team_id reference
        await projects_collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"team_id": team_id}}
        )

    except Exception as e:
        # Rollback: delete the project if team creation fails
        await projects_collection.delete_one({"_id": result.inserted_id})
        raise HTTPException(status_code=500, detail=f"Failed to create team for project. Rolled back. Error: {str(e)}")

    # Fetch the created project
    created_project = await projects_collection.find_one({"_id": result.inserted_id})
    
    # Convert MongoDB _id to string for response
    created_project["id"] = str(created_project.pop("_id"))

    # Index in Pinecone for semantic search
    try:
        index_project(created_project)
    except Exception as e:
        print(f"Warning: Failed to index project in Pinecone: {e}")

    return ProjectResponse(**created_project)


@project_router.get("/my-projects", response_model=list[ProjectResponse], status_code=200)
async def get_projects(request: Request, auth_user_id: int = Depends(get_current_user_id)):
    projects_collection = get_projects_collection(request)
    teams_collection = get_teams_collection(request)

    # 1. Find teams where the user is a member
    teams = await teams_collection.find({"team_members.user_id": auth_user_id}).to_list(length=None)
    
    # Extract project IDs from teams (stored as strings in Team model)
    joined_project_ids = [ObjectId(team["project_id"]) for team in teams]
    
    # 2. Find projects where user is owner OR a team member
    query = {
        "$or": [
            {"auth_user_id": auth_user_id},
            {"_id": {"$in": joined_project_ids}}
        ]
    }

    projects = await projects_collection.find(query).to_list(length=None)
    
    if not projects:
        return []

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
    # Convert MongoDB _id to string for response
    updated_project["id"] = str(updated_project.pop("_id"))

    # Re-index in Pinecone with updated data
    try:
        index_project(updated_project)
    except Exception as e:
        print(f"Warning: Failed to re-index project in Pinecone: {e}")

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

    # Remove from Pinecone index
    try:
        delete_project_index(project_id)
    except Exception as e:
        print(f"Warning: Failed to remove project from Pinecone: {e}")

    return {"message": "Project deleted successfully"}

@project_router.get("/search", response_model=list[ProjectResponse], status_code=200)
async def search_projects_endpoint(
    request: Request,
    q: str,
    auth_user_id: int = Depends(get_current_user_id)
):
    """
    Semantic search over projects using Pinecone.
    Returns projects ranked by relevance to the query.
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")

    projects_collection = get_projects_collection(request)

    # 1. Semantic search in Pinecone
    search_results = pinecone_search_projects(q.strip(), k=20)

    if not search_results:
        return []

    # 2. Get matching project titles from metadata
    matched_titles = [r["metadata"].get("title", "") for r in search_results]

    # 3. Fetch full project docs from MongoDB by title
    matched_projects = await projects_collection.find(
        {"title": {"$in": matched_titles}}
    ).to_list(length=None)

    # 4. Build lookup for ordering
    title_to_project = {}
    for project in matched_projects:
        project["id"] = str(project.pop("_id"))
        title_to_project[project["title"]] = project

    # 5. Return in relevance order
    ordered_results = []
    for r in search_results:
        title = r["metadata"].get("title", "")
        if title in title_to_project:
            ordered_results.append(ProjectResponse(**title_to_project[title]))

    return ordered_results


@project_router.get("/all-projects", response_model=list[ProjectResponse], status_code=200)
async def get_all_projects(request : Request, auth_user_id: int=Depends(get_current_user_id)):
    projects_collection = get_projects_collection(request)

    # Find all projects where auth_user_id is NOT the current user
    projects = await projects_collection.find({"auth_user_id": {"$ne": auth_user_id}}).to_list(length=None)

    # Convert _id to id for response
    for project in projects:
        project["id"] = str(project.pop("_id"))

    return [ProjectResponse(**project) for project in projects]