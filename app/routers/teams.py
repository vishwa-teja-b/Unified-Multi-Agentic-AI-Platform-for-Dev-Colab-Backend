from fastapi import APIRouter, HTTPException, Request, Depends
from bson import ObjectId
from app.dependencies.collections import get_teams_collection
from app.dependencies.auth import get_current_user_id
from app.dto.team_schema import TeamResponse, TeamMemberResponse

teams_router = APIRouter(prefix="/api/teams", tags=["Teams"])

@teams_router.get("/team/{team_id}", response_model=TeamResponse, status_code=200)
async def get_team_by_id(request: Request, team_id: str, auth_user_id: int = Depends(get_current_user_id)):
    """Fetch a team by its ID."""
    teams_collection = get_teams_collection(request)
    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team["id"] = str(team.pop("_id"))
    return TeamResponse(**team)

@teams_router.get("/project/{project_id}", response_model=TeamResponse, status_code=200)
async def get_team_by_project_id(request: Request, project_id: str, auth_user_id: int = Depends(get_current_user_id)):
    """Fetch a team by the project ID it belongs to."""
    teams_collection = get_teams_collection(request)
    team = await teams_collection.find_one({"project_id": project_id})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found for this project")
    team["id"] = str(team.pop("_id"))
    return TeamResponse(**team)
