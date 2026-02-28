from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.models.chat import ChatRoom, Message
from app.dependencies.auth import get_current_user_id
from app.dto.chat_schema import NewChatRequest, TeamChatRequest, SendMessageRequest

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.get("/get-chat-rooms")
async def get_chat_rooms(
    request: Request,
    current_user_id: int = Depends(get_current_user_id)
):
    """Fetch all chat rooms (direct and team) for the current user."""
    db = request.app.state.db
    rooms_cursor = db.chats.find({"participants": current_user_id}).sort("updated_at", -1)
    rooms = []
    
    async for room in rooms_cursor:
        # Convert ObjectId to string for JSON serialization
        room["_id"] = str(room["_id"])
        
        # Enrich the room with the names of the other participants if it's a direct chat
        if room.get("room_type") == "direct":
            other_user_ids = [uid for uid in room.get("participants", []) if uid != current_user_id]
            if other_user_ids:
                other_uid = other_user_ids[0]
                # Fetch profile of the other user
                profile = await db.profiles.find_one({"auth_user_id": other_uid})
                if profile:
                    room["other_user_name"] = profile.get("name")
                    room["other_user_pic"] = profile.get("profile_picture")
        elif room.get("room_type") == "team" and room.get("team_id"):
            team = await db.teams.find_one({"project_id": room["team_id"]})
            if team:
                room["project_title"] = team.get("project_title", f"Team: {room['team_id']}")
            else:
                room["project_title"] = f"Team: {room['team_id']}"
                    
        # Also convert last_message _id
        if "last_message" in room and room["last_message"] and "_id" in room["last_message"]:
            room["last_message"]["_id"] = str(room["last_message"]["_id"])
            
        rooms.append(room)
        
    return {"rooms": rooms}

@router.post("/new-chat")
async def create_or_get_direct_chat(
    req: NewChatRequest,
    request: Request,
    current_user_id: int = Depends(get_current_user_id)
):
    """Create a new direct chat room between the current user and target user, or return existing."""
    db = request.app.state.db
    
    # Check if a direct room already exists with exactly these two participants
    existing_room = await db.chats.find_one({
        "room_type": "direct",
        "participants": {"$all": [current_user_id, req.other_user_id], "$size": 2}
    })
    
    if existing_room:
        existing_room["_id"] = str(existing_room["_id"])
        if "last_message" in existing_room and existing_room["last_message"] and "_id" in existing_room["last_message"]:
            existing_room["last_message"]["_id"] = str(existing_room["last_message"]["_id"])
        return {"room": existing_room}

    # Create new room
    new_room = ChatRoom(
        room_type="direct",
        participants=[current_user_id, req.other_user_id]
    )
    
    result = await db.chats.insert_one(new_room.model_dump())
    new_room_data = await db.chats.find_one({"_id": result.inserted_id})
    new_room_data["_id"] = str(new_room_data["_id"])
    
    return {"room": new_room_data}

@router.post("/team-chat")
async def create_or_get_team_chat(
    req: TeamChatRequest,
    request: Request,
    current_user_id: int = Depends(get_current_user_id)
):
    """Get the team chat room, create it if it doesn't exist."""
    db = request.app.state.db
    
    # First, verify the user is actually in this team.
    team_data = await db.teams.find_one({"project_id": req.team_id, "team_members.user_id": current_user_id})
    if not team_data:
        raise HTTPException(status_code=403, detail="You are not a member of this team.")
        
    all_team_member_ids = [member["user_id"] for member in team_data.get("team_members", [])]
    
    # Check if team room exists
    existing_room = await db.chats.find_one({
        "room_type": "team",
        "team_id": req.team_id
    })
    
    if existing_room:
        # Ensure all team members are listed as participants in case someone joined
        await db.chats.update_one(
            {"_id": existing_room["_id"]},
            {"$set": {"participants": all_team_member_ids}}
        )
        existing_room["_id"] = str(existing_room["_id"])
        if "last_message" in existing_room and existing_room["last_message"] and "_id" in existing_room["last_message"]:
            existing_room["last_message"]["_id"] = str(existing_room["last_message"]["_id"])
        return {"room": existing_room}
        
    # Create the team room
    new_room = ChatRoom(
        room_type="team",
        participants=all_team_member_ids,
        team_id=req.team_id
    )
    
    result = await db.chats.insert_one(new_room.model_dump())
    new_room_data = await db.chats.find_one({"_id": result.inserted_id})
    new_room_data["_id"] = str(new_room_data["_id"])
    
    return {"room": new_room_data}


@router.get("/search-dev")
async def search_developers(
    query: str,
    request: Request,
    current_user_id: int = Depends(get_current_user_id)
):
    """Search profiles by name or username for chatting."""
    db = request.app.state.db
    
    if len(query) < 2:
        return {"users": []}
        
    # Case-insensitive regex search
    regex_query = {"$regex": query, "$options": "i"}
    search_criteria = {
        "$and": [
            {"auth_user_id": {"$ne": current_user_id}}, 
            {"$or": [
                {"name": regex_query},
                {"username": regex_query}
            ]}
        ]
    }
    
    cursor = db.profiles.find(search_criteria).limit(10)
    users = []
    
    async for profile in cursor:
        users.append({
            "auth_user_id": profile.get("auth_user_id"),
            "name": profile.get("name"),
            "username": profile.get("username"),
            "profile_picture": profile.get("profile_picture")
        })
        
    return {"users": users}

@router.get("/{room_id}/messages")
async def get_messages_for_room(
    room_id: str,
    request: Request,
    current_user_id: int = Depends(get_current_user_id)
):
    """Fetch previous messages for a room."""
    db = request.app.state.db
    
    # Validate user is part of the room
    room = await db.chats.find_one({"_id": ObjectId(room_id), "participants": current_user_id})
    if not room:
        raise HTTPException(status_code=403, detail="Not authorized to view this room")
        
    messages_cursor = db.messages.find({"room_id": room_id}).sort("timestamp", 1)
    
    # Fetch user profiles to attach usernames
    user_ids = room.get("participants", [])
    profiles_cursor = db.profiles.find({"auth_user_id": {"$in": user_ids}})
    user_names = {}
    async for p in profiles_cursor:
        user_names[p["auth_user_id"]] = p.get("username", "Unknown")

    messages = []
    async for msg in messages_cursor:
        msg["_id"] = str(msg["_id"])
        msg["sender_name"] = user_names.get(msg["sender_id"], "Unknown")
        messages.append(msg)
        
    return {"messages": messages}



@router.post("/{room_id}/messages")
async def send_message_to_room(
    room_id: str,
    req: SendMessageRequest,
    request: Request,
    current_user_id: int = Depends(get_current_user_id)
):
    """Save a new message to the database."""
    db = request.app.state.db
    
    room = await db.chats.find_one({"_id": ObjectId(room_id), "participants": current_user_id})
    if not room:
        raise HTTPException(status_code=403, detail="Not authorized to post to this room")
        
    new_msg = Message(
        sender_id=current_user_id,
        text=req.text
    )
    msg_dict = new_msg.model_dump()
    msg_dict["room_id"] = room_id
    
    result = await db.messages.insert_one(msg_dict)
    
    # Update last_message on the chat room
    await db.chats.update_one(
        {"_id": ObjectId(room_id)},
        {"$set": {
            "last_message": msg_dict,
            "updated_at": datetime.utcnow()
        }}
    )
    
    saved_msg = await db.messages.find_one({"_id": result.inserted_id})
    saved_msg["_id"] = str(saved_msg["_id"])
    
    # Attach sender username before returning via socket/http
    sender_profile = await db.profiles.find_one({"auth_user_id": current_user_id})
    saved_msg["sender_name"] = sender_profile.get("username", "Unknown") if sender_profile else "Unknown"
    
    return {"message": saved_msg}


@router.post("/{room_id}/mark-read")
async def mark_room_as_read(
    room_id: str,
    request: Request,
    current_user_id: int = Depends(get_current_user_id)
):
    """Mark all unseen messages in a room as read for the current user."""
    db = request.app.state.db
    
    room = await db.chats.find_one({"_id": ObjectId(room_id), "participants": current_user_id})
    if not room:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Mark individual messages as read where sender is NOT current user
    await db.messages.update_many(
        {
            "room_id": room_id,
            "sender_id": {"$ne": current_user_id},
            "is_read": False
        },
        {"$set": {"is_read": True}}
    )
    
    # Also update the denormalized last_message on the chat room if it matches
    if room.get("last_message") and room["last_message"].get("sender_id") != current_user_id:
        await db.chats.update_one(
            {"_id": ObjectId(room_id)},
            {"$set": {"last_message.is_read": True}}
        )
        
    return {"status": "success"}