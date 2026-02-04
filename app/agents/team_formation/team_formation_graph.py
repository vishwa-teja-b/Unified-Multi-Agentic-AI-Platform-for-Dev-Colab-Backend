from langgraph.graph import StateGraph, START,END
from .state import TeamFormationState
from .nodes.role_analyzer import analyze_roles
from .nodes.skill_matcher import skill_matcher
from .nodes.llm_evaluator import evaluate_candidates
from langgraph.checkpoint.mongodb import MongoDBSaver
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
TEAM_FORMATION_AGENT_COLLECTION_NAME = os.getenv("TEAM_FORMATION_AGENT_COLLECTION_NAME")


async def initiate_team_formation_agent_graph():

    graph = StateGraph(TeamFormationState)

    # create nodes
    graph.add_node("analyze_roles", analyze_roles)
    graph.add_node("skill_matcher", skill_matcher)
    graph.add_node("evaluate_candidates", evaluate_candidates)

    # create edges
    graph.add_edge(START, "analyze_roles")
    graph.add_edge("analyze_roles", "skill_matcher")
    graph.add_edge("skill_matcher", "evaluate_candidates")
    graph.add_edge("evaluate_candidates", END)

    # return graph

    return graph


async def invoke_team_formation_agent(graph, initial_state : dict, thread_id:str):
    
    with MongoDBSaver.from_conn_string(conn_string=MONGODB_URI, db_name=MONGODB_DB_NAME, checkpoint_collection_name=TEAM_FORMATION_AGENT_COLLECTION_NAME) as checkpointer:

        team_formation_agent = graph.compile(checkpointer=checkpointer)

        print("Team Formation Agent Invoked")

        config = {"configurable":{"thread_id" : f"{thread_id}"}}

        final_state = await team_formation_agent.ainvoke(initial_state, config)

        return final_state 