from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime
from app.dependencies.collections import get_profiles_collection
from app.dependencies.auth import get_current_user_id
from app.dto.profile_schema import ProfileCreateRequest, ProfileResponse
from app.vector_stores.pinecone_db import index_profile

profile_router = APIRouter(prefix="/api/profiles", tags=["Profiles Creation and Skill Indexing"])


# Simple test endpoint to verify auth works
@profile_router.get("/test-auth")
def test_auth(user_id: int = Depends(get_current_user_id)):
    return {"message": "Auth works!", "user_id": user_id}


@profile_router.post("/create-profile", response_model=ProfileResponse, status_code=201)
async def create_profile(
    request: Request, 
    profile: ProfileCreateRequest,
    auth_user_id: int = Depends(get_current_user_id)
):
    profiles_collection = get_profiles_collection(request)

    # Check if profile already exists for this authenticated user
    existing_profile = await profiles_collection.find_one({"auth_user_id": auth_user_id})
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists for this user")
    
    # Convert to dict and add auth_user_id from JWT
    profile_dict = profile.model_dump()
    profile_dict["auth_user_id"] = auth_user_id
    profile_dict["created_at"] = datetime.utcnow()
    profile_dict["updated_at"] = None
    
    result = await profiles_collection.insert_one(profile_dict)

    # Fetch the created profile
    created_profile = await profiles_collection.find_one({"_id": result.inserted_id})
    
    # Convert MongoDB _id to string for response
    created_profile["id"] = str(created_profile.pop("_id"))

    # Index the profile in Pinecone
    index_profile(created_profile)

    return ProfileResponse(**created_profile)




@profile_router.get("/profile", response_model = ProfileResponse, status_code=200)
async def get_profile(request: Request, auth_user_id: int = Depends(get_current_user_id)):
    profiles_collection = get_profiles_collection(request)
    profile = await profiles_collection.find_one({"auth_user_id": auth_user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile["id"] = str(profile.pop("_id"))
    return ProfileResponse(**profile)




@profile_router.patch("/profile-update", response_model=ProfileResponse, status_code=200)
async def update_profile(
    request: Request, 
    profile_data: ProfileCreateRequest,  # Renamed to avoid collision
    auth_user_id: int = Depends(get_current_user_id)
):
    profiles_collection = get_profiles_collection(request)
    
    # Check if profile exists
    existing_profile = await profiles_collection.find_one({"auth_user_id": auth_user_id})
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Use the new data from request, not the existing profile
    update_dict = profile_data.model_dump()
    update_dict["updated_at"] = datetime.utcnow()
    
    # Update the profile
    await profiles_collection.update_one(
        {"auth_user_id": auth_user_id}, 
        {"$set": update_dict}
    )

    # Fetch the updated profile
    updated_profile = await profiles_collection.find_one({"auth_user_id": auth_user_id})
    
    # Convert MongoDB _id to string for response
    updated_profile["id"] = str(updated_profile.pop("_id"))

    index_profile(updated_profile)  # Re-index with new skills

    return ProfileResponse(**updated_profile)