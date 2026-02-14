from app.agents.project_planner.state import ProjectPlannerState
from langchain_core.messages import SystemMessage, HumanMessage
# from app.services.llm_service import get_llm
from app.agents.llm_config import get_chat_llm_2 as get_llm
from app.utils.llm_parser import parse_llm_output

async def feature_extraction_node(state: ProjectPlannerState) -> ProjectPlannerState:
    """
    Analyzes the project description and high-level features to extract 
    granular technical requirements.
    """
    print("--- FEATURE REFINEMENT & EXTRACTION ---")
    
    project_title = state.get("title", "Untitled Project")
    description = state.get("description", "")
    base_features = state.get("features", [])
    
    # Initialize LLM
    llm = get_llm()
    
    prompt = f"""
    You are an expert Technical Project Manager and System Architect.
    
    PROJECT: {project_title}
    DESCRIPTION: {description}
    HIGH-LEVEL FEATURES: {', '.join(base_features)}
    
    Your task is to refine these high-level features into granular, technical requirements 
    that a developer can implement.
    
    For example:
    - If "User Auth" is a feature -> Expand to: "JWT Authentication", "Login/Signup Screens", "Password Hashing", "Google OAuth".
    - If "Payment" is a feature -> Expand to: "Stripe Integration", "Checkout Flow", "Payment History API".
    
    OUTPUT FORMAT:
    Return ONLY a Python list of strings representing the detailed features. 
    Example: ["JWT Authentication", "Login Screen", "Stripe API Integration"]
    Do not include any other text or markdown formatting.
    """
    
    messages = [
        SystemMessage(content="You are a precise technical architect."),
        HumanMessage(content=prompt)
    ]
    
    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        
        refined_features = parse_llm_output(content, expected_type="json")
        
        if not isinstance(refined_features, list):
            raise ValueError("Output is not a list")
            
        print(f"✅ Extracted {len(refined_features)} technical features.")
        return {"extracted_features": refined_features}
        
    except Exception as e:
        print(f"❌ Error in feature extraction: {e}")
        # Fallback to base features if extraction fails
        return {"extracted_features": base_features, "error": f"Feature extraction failed: {str(e)}"}
