from fastapi import APIRouter, HTTPException, Request, Depends, status
from app.dependencies.auth import get_current_user_id
from app.dependencies.collections import get_project_plans_collection, get_projects_collection
from app.models.room import Room, RoomCreate, RoomResponse
from app.db.mongo import get_database
from bson import ObjectId
from datetime import datetime

rooms_router = APIRouter(prefix="/api/rooms", tags=["Collaboration Rooms"])


@rooms_router.get("", response_model=list[dict], status_code=200)
async def list_my_rooms(
    request: Request,
    auth_user_id: int = Depends(get_current_user_id)
):
    """
    List all rooms where the current user owns the project or is a team member.
    Returns rooms enriched with project_title.
    """
    db = await get_database()
    rooms_collection = db["rooms"]
    projects_collection = get_projects_collection(request)

    # Get user's project IDs (projects they own)
    owned_cursor = projects_collection.find(
        {"auth_user_id": auth_user_id},
        {"_id": 1}
    )
    owned_ids = set()
    async for p in owned_cursor:
        owned_ids.add(str(p["_id"]))

    # Get project IDs where user is a team member
    teams_collection = db["teams"]
    team_cursor = teams_collection.find(
        {"team_members.user_id": auth_user_id},
        {"project_id": 1}
    )
    team_project_ids = set()
    async for t in team_cursor:
        team_project_ids.add(t["project_id"])

    all_project_ids = list(owned_ids | team_project_ids)
    if not all_project_ids:
        return []

    # Fetch rooms for these projects
    rooms_cursor = rooms_collection.find({"project_id": {"$in": all_project_ids}})
    rooms = []
    async for room in rooms_cursor:
        room.pop("_id", None)
        rooms.append(room)

    # Enrich with project titles
    title_cursor = projects_collection.find(
        {"_id": {"$in": [ObjectId(pid) for pid in all_project_ids if ObjectId.is_valid(pid)]}},
        {"_id": 1, "title": 1}
    )
    id_to_title = {}
    async for p in title_cursor:
        id_to_title[str(p["_id"])] = p.get("title", "Untitled")

    for room in rooms:
        room["project_title"] = id_to_title.get(room["project_id"], "Untitled")

    return rooms

@rooms_router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    request: Request,
    room_data: RoomCreate,
    auth_user_id: int = Depends(get_current_user_id)
):
    """
    Create a new collaboration room.
    Prerequisite: Project Plan must exist.
    """
    project_plans_collection = get_project_plans_collection(request)
    
    # 1. Check for Project Plan
    plan = await project_plans_collection.find_one({"project_id": room_data.project_id})
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project Plan required to start session. Please use the Project Planner Agent first."
        )
        
    db = await get_database()
    rooms_collection = db["rooms"]
    
    # Check if room already exists for this project
    existing_room = await rooms_collection.find_one({"project_id": room_data.project_id})
    if existing_room:
        return RoomResponse(**existing_room)
    
    # Create new Room
    new_room = Room(
        room_id=room_data.project_id, # Simplify: 1 Room per Project
        project_id=room_data.project_id,
        created_at=datetime.utcnow(),
        participants=[]
    )
    
    await rooms_collection.insert_one(new_room.model_dump())
    
    return RoomResponse(**new_room.model_dump())

@rooms_router.get("/{project_id}", response_model=RoomResponse)
async def get_room(
    request: Request,
    project_id: str,
    auth_user_id: int = Depends(get_current_user_id)
):
    """
    Get room details by Project ID.
    """
    db = await get_database()
    rooms_collection = db["rooms"]
    
    room = await rooms_collection.find_one({"project_id": project_id})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    return RoomResponse(**room)
