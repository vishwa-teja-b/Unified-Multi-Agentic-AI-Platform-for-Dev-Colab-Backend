from app.agents.project_planner.state import ProjectPlannerState
from langchain_core.messages import SystemMessage, HumanMessage
# from app.services.llm_service import get_llm
from app.agents.llm_config import get_chat_llm_2 as get_llm
from app.utils.llm_parser import parse_llm_output
import json

async def task_generation_node(state: ProjectPlannerState) -> ProjectPlannerState:
    """
    Breaks down each sprint milestone into granular tasks and assigns them to team members.
    """
    print("--- TASK GENERATION ---")
    
    milestones = state.get("milestones", [])
    team_members = state.get("team_members", [])
    
    # Enrich team members info for context (Role + Skills)
    team_context = []
    for member in team_members:
        # Assuming member dict has 'name', 'role' or 'job_title', 'skills'
        # Default to generic if missing
        name = member.get("username", member.get("user_id", "Developer"))
        role = member.get("role", "Full Stack Developer")   
        skills = member.get("skills", [])
        team_context.append(f"- {name} ({role}): Skills: {', '.join(skills)}")
    
    llm = get_llm()
    
    final_roadmap = []
    
    for sprint in milestones:
        sprint_name = sprint.get("name", f"Sprint {sprint.get('sprint_number')}")
        sprint_goals = sprint.get("goals", [])
        
        prompt = f"""
        You are a Tech Lead assigning tasks to your team.
        
        SPRINT: {sprint_name}
        GOALS: {', '.join(sprint_goals)}
        TEAM:
        {chr(10).join(team_context)}
        
        Task:
        Break down the sprint goals into granular tasks (coding, design, testing, deployment).
        Assign each task to the most suitable team member based on their role and skills.
        Estimate time in hours (e.g. 4h, 8h). Priority: High/Medium/Low.
        
        OUTPUT FORMAT:
        Return valid JSON listing tasks for this sprint.
        [
            {{
                "id": "T-101",
                "title": "Setup React Repo",
                "assignee": "Name of member",
                "role": "Frontend",
                "estimate": "4h",
                "priority": "High",
                "status": "todo"
            }},
            ...
        ]
        """
        
        messages = [
            SystemMessage(content="You are an expert Tech Lead creating detailed tasks."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = await llm.ainvoke(messages)
            content = response.content.strip()
            
            tasks = parse_llm_output(content, expected_type="json")
            
            # Combine sprint info with tasks
            final_roadmap.append({
                **sprint,
                "tasks": tasks
            })
            
        except Exception as e:
            print(f"❌ Error generating tasks for sprint {sprint_name}: {e}")
            # Fallback: keep sprint but empty tasks
            final_roadmap.append({
                **sprint,
                "tasks": [],
                "error": str(e)
            })

    print(f"✅ Generated tasks for {len(final_roadmap)} sprints.")
    return {"roadmap": final_roadmap}
