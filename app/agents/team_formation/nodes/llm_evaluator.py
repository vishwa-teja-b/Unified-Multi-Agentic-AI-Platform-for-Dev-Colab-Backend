from langchain_core.prompts import ChatPromptTemplate
from app.agents.llm_config import get_chat_llm
from ..state import TeamFormationState
from langchain_core.output_parsers import StrOutputParser
from app.agents.utils import extract_json
import json

EVAL_PROMPT = """You are evaluating candidates for a project team.
Project: {project_title}
Required Skills: {required_skills}

Candidates (with their email as identifier):
{candidates_json}

For each candidate, evaluate and return:
1. email (use the exact email from the candidate data as identifier)
2. match_score (0-100, based on skill match and availability)
3. reasoning (1-2 sentences explaining why they're a good fit)

Return ONLY a JSON array, no markdown:
[
  {{"email": "candidate@email.com", "match_score": 85, "reasoning": "Strong skills in required areas..."}}
]
"""

async def evaluate_candidates(state: TeamFormationState) -> dict:
    llm = get_chat_llm()
    candidates = state.get("candidates", [])
    
    if not candidates:
        return {"recommendations": []}

    prompt = ChatPromptTemplate.from_template(EVAL_PROMPT)
    chain = prompt | llm | StrOutputParser()

    response = await chain.ainvoke({
        "project_title": state["project_title"],
        "required_skills": ", ".join(state["required_skills"]),
        "candidates_json": json.dumps(candidates, indent=2)
    })

    # Parse JSON from LLM response
    llm_evaluations = extract_json(response)
    
    # Create lookup by email for LLM scores
    eval_lookup = {}
    if isinstance(llm_evaluations, list):
        for evaluation in llm_evaluations:
            email = evaluation.get("email", "")
            if email:
                eval_lookup[email] = evaluation
    
    # Merge original candidate data with LLM evaluation
    recommendations = []
    for candidate in candidates:
        email = candidate.get("email", "")
        llm_eval = eval_lookup.get(email, {})
        
        # Combine all data: original candidate + LLM evaluation
        recommendation = {
            # Original candidate data
            "role": candidate.get("role", ""),
            "name": candidate.get("name", ""),
            "username": candidate.get("username", ""),
            "email": email,
            "skills": candidate.get("skills", ""),
            "similarity_score": candidate.get("similarity_score", 0),
            "availability_hours": candidate.get("availability_hours", 0),
            "timezone": candidate.get("timezone", "UTC"),
            "timezone_diff": candidate.get("timezone_diff", 0),
            "timezone_score": candidate.get("timezone_score", 1.0),
            # LLM evaluation data
            "match_score": llm_eval.get("match_score", int(candidate.get("similarity_score", 0) * 100)),
            "reasoning": llm_eval.get("reasoning", "Skill match based on profile analysis.")
        }
        recommendations.append(recommendation)
    
    # Sort by match_score descending
    recommendations.sort(key=lambda x: x.get("match_score", 0), reverse=True)

    return {"recommendations": recommendations}


