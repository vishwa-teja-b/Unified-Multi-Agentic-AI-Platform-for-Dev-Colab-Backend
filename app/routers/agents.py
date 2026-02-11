from fastapi import APIRouter, Depends, HTTPException, Request
from app.agents.team_formation.team_formation_graph import initiate_team_formation_agent_graph, invoke_team_formation_agent
from app.dto.team_formation_schema import TeamFormationRequest, TeamFormationResponse
from app.dependencies.auth import get_current_user_id
from app.dependencies.collections import get_projects_collection , get_profiles_collection
from bson import ObjectId

agent_router = APIRouter(prefix="/api/agents", tags=["Team Formation Agent"])

@agent_router.post("/team-formation", response_model=TeamFormationResponse, status_code=200)
async def team_formation_agent(
    request: Request,
    request_body: TeamFormationRequest,
    auth_user_id: int = Depends(get_current_user_id)
):
    # get project from MongoDB
    projects_collection = get_projects_collection(request)
    profiles_collection = get_profiles_collection(request)

    project = await projects_collection.find_one({"_id": ObjectId(request_body.project_id)})

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # GET OWNER'S TIMEZONE FROM THEIR PROFILE (ADD THIS)
    owner_profile = await profiles_collection.find_one({"auth_user_id": auth_user_id})
    owner_timezone = owner_profile.get("timezone", "UTC") if owner_profile else "UTC"

    # Build initial state with keys matching TeamFormationState
    initial_state = {
        "project_id": str(project["_id"]),
        "project_title": project.get("title", ""),
        "required_skills": project.get("required_skills", []),
        "team_size": project.get("team_size", {}).get("max", 4),
        "timeline": project.get("estimated_duration", "4 weeks"),
        "owner_timezone": owner_timezone,
        "roles": [],
        "candidates": [],
        "recommendations": [],
        "error": None
    }

    # initiate team formation agent graph (building the graph)

    team_formation_agent_graph = await initiate_team_formation_agent_graph()

    # invoke team formation agent graph (executing the graph)

    final_state = await invoke_team_formation_agent(
        team_formation_agent_graph, 
        initial_state, 
        str(auth_user_id)
    )

    print(final_state)

    return TeamFormationResponse(
        recommendations=final_state.get("recommendations", []),
        error=final_state.get("error")
    )
