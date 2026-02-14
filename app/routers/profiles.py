from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime
from app.dependencies.collections import get_profiles_collection
from app.dependencies.auth import get_current_user_id
from app.dto.profile_schema import ProfileCreateRequest, ProfileResponse
from app.vector_stores.pinecone_db import index_profile

profile_router = APIRouter(prefix="/api/profiles", tags=["Profiles Creation and Skill Indexing"])


# Helper function to construct full URLs from usernames
def construct_social_urls(profile: dict) -> dict:
    """
    Transform username-only social fields into full URLs.
    Database stores just the username, API returns full URLs.
    """
    if profile.get("github") and not profile["github"].startswith("http"):
        profile["github"] = f"https://github.com/{profile['github']}"
    
    if profile.get("linkedin") and not profile["linkedin"].startswith("http"):
        profile["linkedin"] = f"https://linkedin.com/in/{profile['linkedin']}"
    
    if profile.get("portfolio") and not profile["portfolio"].startswith("http"):
        profile["portfolio"] = f"https://{profile['portfolio']}"
    
    return profile


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

    # Check if a partial profile already exists (auto-created during registration)
    existing_profile = await profiles_collection.find_one({"auth_user_id": auth_user_id})
    
    # Convert to dict and add auth_user_id from JWT
    profile_dict = profile.model_dump()
    profile_dict["auth_user_id"] = auth_user_id
    profile_dict["updated_at"] = datetime.utcnow()

    if existing_profile:
        # Upsert: Update the partial profile with full profile data
        profile_dict.pop("auth_user_id")  # Don't overwrite auth_user_id
        await profiles_collection.update_one(
            {"auth_user_id": auth_user_id},
            {"$set": profile_dict}
        )
        # Fetch the updated profile
        created_profile = await profiles_collection.find_one({"auth_user_id": auth_user_id})
    else:
        # Fresh insert (fallback for edge cases)
        profile_dict["created_at"] = datetime.utcnow()
        result = await profiles_collection.insert_one(profile_dict)
        created_profile = await profiles_collection.find_one({"_id": result.inserted_id})
    
    # Convert MongoDB _id to string for response
    created_profile["id"] = str(created_profile.pop("_id"))

    # Index the profile in Pinecone
    index_profile(created_profile)

    # Construct full URLs before returning
    created_profile = construct_social_urls(created_profile)

    return ProfileResponse(**created_profile)




@profile_router.get("/profile", response_model = ProfileResponse, status_code=200)
async def get_profile(request: Request, auth_user_id: int = Depends(get_current_user_id)):
    profiles_collection = get_profiles_collection(request)
    profile = await profiles_collection.find_one({"auth_user_id": auth_user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile["id"] = str(profile.pop("_id"))
    
    # Construct full URLs before returning
    profile = construct_social_urls(profile)
    
    return ProfileResponse(**profile)

@profile_router.get("/profile/{username}",response_model = ProfileResponse, status_code=200)
async def get_profile_by_username(
    request : Request,
    username : str,
    auth_user_id : int = Depends(get_current_user_id)
):
    profiles_collection = get_profiles_collection(request)
    profile = await profiles_collection.find_one({"auth_user_id": auth_user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="User not found... Login First")

    other_profile = await profiles_collection.find_one({"username": username})
    
    if not other_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    other_profile["id"] = str(other_profile.pop("_id"))
    
    # Construct full URLs before returning
    other_profile = construct_social_urls(other_profile)
    
    return ProfileResponse(**other_profile)


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

    # Construct full URLs before returning
    updated_profile = construct_social_urls(updated_profile)

    return ProfileResponse(**updated_profile)