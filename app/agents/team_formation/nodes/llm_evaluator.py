from langchain_core.prompts import ChatPromptTemplate
from app.agents.llm_config import get_chat_llm
from ..state import TeamFormationState
from langchain_core.output_parsers import StrOutputParser
from app.agents.utils import extract_json
import json

EVAL_PROMPT = """You are evaluating candidates for a project team.
Project: {project_title}
Required Skills: {required_skills}
Candidates:
{candidates_json}
For each candidate, provide:
1. match_score (0-100)
2. reasoning (why they're a good/bad fit)
3. recommended_role
Return JSON array:
[
  {{"username": "...", "match_score": 85, "reasoning": "...", "recommended_role": "..."}}
]
"""

async def evaluate_candidates(state: TeamFormationState) -> dict:
    llm = get_chat_llm()

    prompt = ChatPromptTemplate.from_template(EVAL_PROMPT)

    chain = prompt | llm | StrOutputParser()

    response = await chain.ainvoke({
        "project_title": state["project_title"],
        "required_skills": ", ".join(state["required_skills"]),
        "candidates_json": json.dumps(state["candidates"])
    })

    # Parse JSON from LLM response (handles markdown code blocks)
    recommendations = extract_json(response)

    return {"recommendations": recommendations}

