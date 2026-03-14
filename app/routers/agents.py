from fastapi import APIRouter, Depends, HTTPException, Request
from app.agents.team_formation.team_formation_graph import initiate_team_formation_agent_graph, invoke_team_formation_agent
from app.dto.team_formation_schema import TeamFormationRequest, TeamFormationResponse
from app.dependencies.auth import get_current_user_id
from app.dependencies.collections import get_projects_collection, get_teams_collection, get_project_plans_collection, get_profiles_collection
from bson import ObjectId
from app.agents.project_planner.graph import initiate_project_planner_agent_graph, invoke_project_planner_agent
from app.dto.project_planner_schema import ProjectPlannerRequest, ProjectPlannerResponse
from app.agents.team_formation.state import TeamFormationState
from app.dto.team_schema import TeamResponse
from app.models.project_plan import ProjectPlan
from datetime import datetime, timedelta, timezone
import re
import logging

logger = logging.getLogger(__name__)

agent_router = APIRouter(prefix="/api/agents", tags=["Team Formation Agent"])


def parse_duration_to_days(duration_str: str) -> int:
    """
    Parse a human-readable duration string into a number of days.
    Supports: '2 weeks', '1 month', '10 days', '3 months', etc.
    Defaults to 14 days if parsing fails.
    """
    duration_str = duration_str.strip().lower()
    match = re.match(r'(\d+)\s*(day|days|week|weeks|month|months)', duration_str)
    if not match:
        return 14  # default to 2 weeks
    
    value = int(match.group(1))
    unit = match.group(2)
    
    if 'day' in unit:
        return value
    elif 'week' in unit:
        return value * 7
    elif 'month' in unit:
        return value * 30
    return 14


def compute_sprint_dates(roadmap: list, start_date: datetime) -> list:
    """
    Compute start_date and end_date for each sprint sequentially.
    Each sprint starts when the previous one ends.
    """
    current_start = start_date
    for sprint in roadmap:
        duration_days = parse_duration_to_days(sprint.get("duration", "2 weeks"))
        sprint_end = current_start + timedelta(days=duration_days)
        sprint["start_date"] = current_start.isoformat()
        sprint["end_date"] = sprint_end.isoformat()
        current_start = sprint_end
    return roadmap

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

    logger.debug("Final state: %s", final_state)

    return TeamFormationResponse(
        recommendations=final_state.get("recommendations", []),
        error=final_state.get("error")
    )


@agent_router.post("/project-planner", response_model=ProjectPlannerResponse, status_code=200)
async def project_planner_agent(
    request: Request,
    request_body: ProjectPlannerRequest,
    auth_user_id: int = Depends(get_current_user_id)
):
    logger.info("Project Planner Agent Request Received for Project ID: %s", request_body.project_id)
    
    projects_collection = get_projects_collection(request)
    teams_collection = get_teams_collection(request)
    project_plans_collection = get_project_plans_collection(request)
    
    # Fetch Project
    try:
        project = await projects_collection.find_one({"_id": ObjectId(request_body.project_id)})
        logger.info("Project found: %s", project.get('title', 'Unknown'))
    except:
        logger.warning("Invalid Project ID format: %s", request_body.project_id)
        raise HTTPException(status_code=400, detail="Invalid Project ID format")
        
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Fetch Team (if exists)
    team_members = []
    if project.get("team_id"):
        try:
            team = await teams_collection.find_one({"_id": ObjectId(project["team_id"])})
            if team:
                team_members = team.get("team_members", [])
                logger.info("Team found: %d members", len(team_members))
        except:
            logger.warning("Invalid team ID format or team not found")
    else:
        logger.info("No team assigned to this project yet.")
            
    # Prepare State
    initial_state = {
        "project_id": str(project["_id"]),
        "title": project.get("title", ""),
        "category": project.get("category", ""),
        "description": project.get("description", ""),
        "features": project.get("features", []),
        "required_skills": project.get("required_skills", []),
        "team_size": project.get("team_size", {}), # Pass raw dict
        "team_members": team_members, # Raw list from DB
        "team_id": project.get("team_id"),
        "complexity": project.get("complexity", ""),
        "estimated_duration": project.get("estimated_duration", ""),
        "status": project.get("status", "Open"),
        "extracted_features": [],
        "milestones": [],
        "roadmap": [],
        "error": None
    }
    
    # Run Agent
    try:
        logger.info("Initiating Project Planner Agent Graph...")
        # Using new async structure:
        graph = await initiate_project_planner_agent_graph()
        
        logger.info("Invoking Project Planner Agent...")
        result = await invoke_project_planner_agent(graph, initial_state, thread_id=str(project["_id"]))
        
        logger.info("Project Planner Agent Execution Successful")
        
        # Save Plan to DB
        try:
            # Compute sprint dates before saving
            now = datetime.now(timezone.utc)
            roadmap_with_dates = compute_sprint_dates(result["roadmap"], now)
            
            plan_data = ProjectPlan(
                project_id=result["project_id"],
                roadmap=roadmap_with_dates,
                extracted_features=result["extracted_features"],
                created_at=now,
                updated_at=now
            )
            
            # Upsert: Update if exists, Insert if not
            await project_plans_collection.update_one(
                {"project_id": result["project_id"]},
                {"$set": plan_data.model_dump()},
                upsert=True
            )
            logger.info("Project Plan saved to DB for project: %s", result['project_id'])
        except Exception as db_err:
            logger.error("Failed to save project plan to DB: %s", db_err)
            # We don't raise error here to let the response go through, but log it
        
        return ProjectPlannerResponse(
            project_id=result["project_id"],
            roadmap=roadmap_with_dates,
            extracted_features=result["extracted_features"],
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error("Agent Execution Failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
