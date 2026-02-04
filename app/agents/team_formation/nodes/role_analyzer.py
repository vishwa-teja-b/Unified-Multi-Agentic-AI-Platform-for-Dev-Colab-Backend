from langchain_core.prompts import ChatPromptTemplate
from app.agents.llm_config import get_chat_llm
from ..state import TeamFormationState
from langchain_core.output_parsers import StrOutputParser
from app.agents.utils import extract_json

ROLE_PROMPT = """You are a technical team analyst.
Given the project requirements, identify the specific team roles needed.
Project: {project_title}
Required Skills: {required_skills}
Team Size: {team_size}
Timeline: {timeline}
Return a JSON array of roles:
[
  {{"role": "Role Name", "count": 1, "skills": ["skill1", "skill2"]}}
]
"""

async def analyze_roles(state: TeamFormationState) -> dict:
    llm = get_chat_llm()

    prompt = ChatPromptTemplate.from_template(ROLE_PROMPT)

    chain = prompt | llm | StrOutputParser()

    response = await chain.ainvoke({
        "project_title": state["project_title"],
        "required_skills": ", ".join(state["required_skills"]),
        "team_size": state["team_size"],
        "timeline": state["timeline"]
    })

    # Parse JSON from LLM response (handles markdown code blocks)
    roles = extract_json(response)

    return {"roles": roles}
