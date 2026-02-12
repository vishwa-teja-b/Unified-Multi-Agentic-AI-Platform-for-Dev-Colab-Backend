from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime
from app.dto.invitation_schema import SendInvitation, UpdateInvitation, JoinRequest
from app.models.teams import TeamMember
from app.dependencies.collections import get_profiles_collection , get_invitations_collection, get_projects_collection, get_teams_collection
from bson import ObjectId
from app.dependencies.auth import get_current_user_id

invitation_router = APIRouter(prefix="/api/projects", tags=["Projects"])

@invitation_router.post("/send-invitation", status_code=201)
async def send_invitation(request : Request,
                            request_body : SendInvitation,
                            auth_user_id : int = Depends(get_current_user_id),
                        ):
    
    profiles_collection = get_profiles_collection(request)
    projects_collection = get_projects_collection(request)
    invitations_collection = get_invitations_collection(request)
    
    existing_profile = await profiles_collection.find_one({"auth_user_id": auth_user_id})

    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    existing_project = await projects_collection.find_one({"_id" : ObjectId(request_body.project_id)})

    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")

    existing_invitation = await invitations_collection.find_one({"project_id" : request_body.project_id, "receiver_id" : request_body.receiver_id})

    if existing_invitation:
        raise HTTPException(status_code=400, detail="Invitation already sent")

    # Fix: existing_project is a dict, so use ["auth_user_id"] instead of .auth_user_id
    if existing_project["auth_user_id"] != auth_user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to send invitation for this project")

    # Fix: Use the request body data, but override/add server-side fields
    invitation_data = request_body.model_dump()

    invitation_data.update({
        "sender_id": auth_user_id, # Ensure sender is the authenticated user
        "status": "PENDING",
        "created_at": datetime.utcnow(),
        "updated_at": None
    })

    result = await invitations_collection.insert_one(invitation_data)

    # send email to the receiver

    return {"message" : "Invitation sent successfully", "invitation_id": str(result.inserted_id)}

@invitation_router.post("/update-invitation", status_code=200)
async def update_invitation(request : Request,
                            request_body : UpdateInvitation,
                            auth_user_id : int = Depends(get_current_user_id),
                        ):
    
    invitations_collection = get_invitations_collection(request)

    invitation = await invitations_collection.find_one({"_id" : ObjectId(request_body.invitation_id)})

    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    if invitation["receiver_id"] != auth_user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this invitation")

    new_status = request_body.status.upper()
    updated_at = datetime.utcnow()

    result = await invitations_collection.update_one(
        {"_id" : ObjectId(request_body.invitation_id)}, 
        {"$set" : {"status": new_status, "updated_at": updated_at}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Invitation status not updated or already same")

    return {"message" : "Invitation updated successfully"}

@invitation_router.get("/get-my-invitations", status_code=200)
async def get_my_invitations(request : Request, auth_user_id : int = Depends(get_current_user_id)):

    invitations_collection = get_invitations_collection(request)

    invitations = await invitations_collection.find({"receiver_id" : auth_user_id}).to_list(length=None)

    for invitation in invitations:
        invitation["id"] = str(invitation.pop("_id"))

    return invitations

# ==================== JOIN REQUESTS ====================

@invitation_router.post("/request-to-join", status_code=201)
async def request_to_join(request: Request,
                          request_body: JoinRequest,
                          auth_user_id: int = Depends(get_current_user_id)):
    
    projects_collection = get_projects_collection(request)
    invitations_collection = get_invitations_collection(request)

    # Find the project
    existing_project = await projects_collection.find_one({"_id": ObjectId(request_body.project_id)})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_owner_id = existing_project["auth_user_id"]

    # Can't request to join your own project
    if project_owner_id == auth_user_id:
        raise HTTPException(status_code=400, detail="You cannot request to join your own project")

    # Check for duplicate request
    existing_request = await invitations_collection.find_one({
        "project_id": request_body.project_id,
        "sender_id": auth_user_id,
        "type": "JOIN_REQUEST"
    })
    if existing_request:
        raise HTTPException(status_code=400, detail="You have already requested to join this project")

    invitation_data = {
        "project_id": request_body.project_id,
        "project_title": existing_project.get("title", ""),
        "sender_id": auth_user_id,
        "receiver_id": project_owner_id,
        "role": request_body.role,
        "message": request_body.message,
        "type": "JOIN_REQUEST",
        "status": "PENDING",
        "created_at": datetime.utcnow(),
        "updated_at": None
    }

    # also send email

    result = await invitations_collection.insert_one(invitation_data)

    return {"message": "Join request sent successfully", "invitation_id": str(result.inserted_id)}


@invitation_router.get("/get-join-requests", status_code=200)
async def get_join_requests(request: Request, auth_user_id: int = Depends(get_current_user_id)):
    """
    Get all JOIN_REQUEST invitations where the current user is the project owner (receiver).
    """
    invitations_collection = get_invitations_collection(request)

    join_requests = await invitations_collection.find({
        "receiver_id": auth_user_id,
        "type": "JOIN_REQUEST"
    }).to_list(length=None)

    for req in join_requests:
        req["id"] = str(req.pop("_id"))

    return join_requests


@invitation_router.post("/respond-join-request", status_code=200)
async def respond_join_request(request: Request,
                               request_body: UpdateInvitation,
                               auth_user_id: int = Depends(get_current_user_id)):
    """
    Owner accepts or rejects a join request.
    On ACCEPT: adds the requester to the existing team document.
    """
    invitations_collection = get_invitations_collection(request)
    teams_collection = get_teams_collection(request)

    invitation = await invitations_collection.find_one({"_id": ObjectId(request_body.invitation_id)})

    if not invitation:
        raise HTTPException(status_code=404, detail="Join request not found")

    # Only the project owner (receiver) can respond
    if invitation["receiver_id"] != auth_user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to respond to this request")

    if invitation.get("type") != "JOIN_REQUEST":
        raise HTTPException(status_code=400, detail="This is not a join request")

    if invitation["status"] != "PENDING":
        raise HTTPException(status_code=400, detail="This request has already been responded to")

    new_status = request_body.status.upper()

    if new_status not in ("ACCEPTED", "REJECTED"):
        raise HTTPException(status_code=400, detail="Status must be ACCEPTED or REJECTED")

    # Update invitation status
    await invitations_collection.update_one(
        {"_id": ObjectId(request_body.invitation_id)},
        {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
    )

    # On ACCEPT: add member to team (single source of truth)
    if new_status == "ACCEPTED":
        project_id = invitation["project_id"]
        sender_id = invitation["sender_id"]
        role = invitation.get("role", "Member")

        new_member = TeamMember(
            user_id=sender_id,
            role=role,
            joined_at=datetime.utcnow()
        )

        # Team is always created at project creation time
        existing_team = await teams_collection.find_one({"project_id": project_id})

        if not existing_team:
            raise HTTPException(status_code=404, detail="Team not found for this project")

        # Add member (avoid duplicates)
        already_member = any(m["user_id"] == sender_id for m in existing_team.get("team_members", []))
        if not already_member:
            await teams_collection.update_one(
                {"project_id": project_id},
                {"$push": {"team_members": new_member.model_dump()}}
            )

        return {"message": "Join request accepted. Member added to team."}

    return {"message": "Join request rejected."}