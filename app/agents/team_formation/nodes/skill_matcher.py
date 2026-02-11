from app.vector_stores.pinecone_db import get_pinecone_vector_store
from ..state import TeamFormationState
from app.utils.timezone_utils import filter_candidates_by_timezone


async def skill_matcher(state: TeamFormationState) -> dict:
    vector_store = get_pinecone_vector_store()
    owner_timezone = state.get("owner_timezone","UTC")

    all_candidates = []

    # roles should be a list from extract_json
    roles = state.get("roles", [])
    if isinstance(roles, dict):
        # Handle case where LLM returns {"roles": [...]}
        roles = roles.get("roles", [])

    for role in roles:
        # building search query from role skills
        skills = role.get("skills", [])
        query = " ".join(skills) if skills else role.get("role", "")

        # search in pinecone (cosine similarity search with score)
        results = vector_store.similarity_search_with_score(query, k=5)

        for doc, score in results:
            all_candidates.append({
                "role": role.get("role", ""),
                "name": doc.metadata.get("name", "") or doc.metadata.get("username", "Unknown"),
                "username": doc.metadata.get("username", ""),
                "email": doc.metadata.get("email", ""),
                "skills": doc.page_content,
                "similarity_score" : score,
                "availability_hours": doc.metadata.get("availability_hours", 0),
                "timezone" : doc.metadata.get("timezone","UTC")
            })
        
        # FILTER CANDIDATES BY TIMEZONE (ADD THIS)
    filtered_candidates = filter_candidates_by_timezone(
        candidates=all_candidates,
        owner_timezone=owner_timezone,
        max_hour_difference=4.0  # Only include people within 4 hours
    )

    return {"candidates": filtered_candidates}