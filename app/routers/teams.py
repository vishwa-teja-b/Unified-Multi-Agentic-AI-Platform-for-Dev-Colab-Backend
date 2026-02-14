from fastapi import APIRouter, HTTPException, Request, Depends
from bson import ObjectId
from sqlmodel import Session, select
from app.dependencies.collections import get_teams_collection
from app.dependencies.auth import get_current_user_id
from app.dto.team_schema import TeamResponse, TeamMemberResponse
from app.db.mysql_connection import get_session
from app.models.User import User

teams_router = APIRouter(prefix="/api/teams", tags=["Teams"])


def _enrich_members_with_usernames(team: dict, session: Session) -> dict:
    """Resolve user_ids to usernames from the SQL User table."""
    user_ids = [m["user_id"] for m in team.get("team_members", [])]
    if not user_ids:
        return team

    # Batch query all users at once
    statement = select(User).where(User.id.in_(user_ids))  # type: ignore
    users = session.exec(statement).all()
    id_to_username = {u.id: u.username for u in users}

    for member in team.get("team_members", []):
        member["username"] = id_to_username.get(member["user_id"])

    return team


@teams_router.get("/team/{team_id}", response_model=TeamResponse, status_code=200)
async def get_team_by_id(
    request: Request,
    team_id: str,
    auth_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Fetch a team by its ID."""
    teams_collection = get_teams_collection(request)
    team = await teams_collection.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team["id"] = str(team.pop("_id"))
    team = _enrich_members_with_usernames(team, session)
    return TeamResponse(**team)


@teams_router.get("/project/{project_id}", response_model=TeamResponse, status_code=200)
async def get_team_by_project_id(
    request: Request,
    project_id: str,
    auth_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session),
):
    """Fetch a team by the project ID it belongs to."""
    teams_collection = get_teams_collection(request)
    team = await teams_collection.find_one({"project_id": project_id})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found for this project")
    team["id"] = str(team.pop("_id"))
    team = _enrich_members_with_usernames(team, session)
    return TeamResponse(**team)
