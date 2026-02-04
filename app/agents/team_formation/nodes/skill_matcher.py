from app.vector_stores.pinecone_db import get_pinecone_vector_store
from ..state import TeamFormationState


async def skill_matcher(state: TeamFormationState) -> dict:
    vector_store = get_pinecone_vector_store()

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
                "name": doc.metadata.get("name", ""),
                "email": doc.metadata.get("email", ""),
                "skills": doc.page_content,
                "similarity_score" : score,
                "availability_hours": doc.metadata.get("availability_hours", 0)
            })

    return {"candidates": all_candidates}
