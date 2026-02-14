from app.agents.project_planner.state import ProjectPlannerState
from langchain_core.messages import SystemMessage, HumanMessage
# from app.services.llm_service import get_llm
from app.agents.llm_config import get_chat_llm_2 as get_llm
from app.utils.llm_parser import parse_llm_output
import json

async def milestone_definition_node(state: ProjectPlannerState) -> ProjectPlannerState:
    """
    Groups refined features into sprints based on timeline and team size.
    """
    print("--- MILESTONE DEFINITION ---")
    
    project_title = state.get("title", "Project")
    features = state.get("extracted_features", [])
    timeline = state.get("estimated_duration", "4 weeks") # e.g. "8 weeks"
    team_members = state.get("team_members", [])

    # Simple logic to determine number of sprints based on duration
    # Assuming 2-week sprints as standard
    try:
        import re
        weeks = int(re.search(r'\d+', timeline).group())
    except:
        weeks = 4 # Default fallback
        
    num_sprints = max(1, weeks // 2)
    
    llm = get_llm()
    
    prompt = f"""
    You are an Agile Project Manager.
    
    PROJECT: {project_title}
    REFINED FEATURES: {', '.join(features)}
    TIMELINE: {timeline} ({weeks} weeks total)
    TEAM SIZE: {len(team_members)} members
    SPRINTS: Plan for {num_sprints} sprints (approx 2 weeks each).
    
    Task:
    Group the features into logical sprints. Start with foundational work, then core features, then polish/advanced features.
    
    OUTPUT FORMAT:
    Return valid JSON list of objects.
    [
        {{
            "sprint_number": 1,
            "name": "Sprint Name (e.g. Foundation)",
            "duration": "2 weeks",
            "goals": ["Setup Repo", "Auth API"],
            "features": ["Feature 1", "Feature 2"] 
        }},
        ...
    ]
    """
    
    messages = [
        SystemMessage(content="You are an expert Agile coach planning a project roadmap."),
        HumanMessage(content=prompt)
    ]
    
    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        
        milestones = parse_llm_output(content, expected_type="json")
        
        print(f"✅ Created plan with {len(milestones)} sprints.")
        return {"milestones": milestones}
        
    except Exception as e:
        print(f"❌ Error in milestone definition: {e}")
        return {"error": f"Milestone definition failed: {str(e)}"}
