from langgraph.graph import StateGraph, END
from app.agents.project_planner.state import ProjectPlannerState
from app.agents.project_planner.nodes.feature_extraction import feature_extraction_node
from app.agents.project_planner.nodes.milestone_definition import milestone_definition_node
from app.agents.project_planner.nodes.task_generation import task_generation_node
from langgraph.checkpoint.mongodb import MongoDBSaver
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
PROJECT_PLANNER_AGENT_COLLECTION_NAME = os.getenv("PROJECT_PLANNER_AGENT_COLLECTION_NAME")


async def initiate_project_planner_agent_graph():

    graph = StateGraph(ProjectPlannerState)

    # create nodes
    graph.add_node("feature_extraction", feature_extraction_node)   
    graph.add_node("milestone_definition", milestone_definition_node)
    graph.add_node("task_generation", task_generation_node)

    # create edges
    graph.set_entry_point("feature_extraction")
    graph.add_edge("feature_extraction", "milestone_definition")
    graph.add_edge("milestone_definition", "task_generation")
    graph.add_edge("task_generation", END)

    # return graph

    return graph


async def invoke_project_planner_agent(graph, initial_state : dict, thread_id:str):
    
    with MongoDBSaver.from_conn_string(conn_string=MONGODB_URI, db_name=MONGODB_DB_NAME, checkpoint_collection_name=PROJECT_PLANNER_AGENT_COLLECTION_NAME) as checkpointer:

        project_planner_agent = graph.compile(checkpointer=checkpointer)

        print("Project Planner Agent Invoked")

        config = {"configurable":{"thread_id" : f"{thread_id}"}}

        final_state = await project_planner_agent.ainvoke(initial_state, config)

        return final_state