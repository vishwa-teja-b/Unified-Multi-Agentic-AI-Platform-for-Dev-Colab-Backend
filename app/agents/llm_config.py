from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from app.config.external_services import OPENROUTER_BASE_URL

load_dotenv()

def get_chat_llm():

    chat_llm = ChatOpenAI(
        model=os.getenv("MODEL_1"),
        base_url=OPENROUTER_BASE_URL,
        api_key=os.getenv("OPEN_ROUTER_API_KEY_1"),
        temperature=0.5,
    )

    return chat_llm

def get_chat_llm_2():

    chat_llm = ChatOpenAI(
        model=os.getenv("MODEL_1"),
        base_url=OPENROUTER_BASE_URL,
        api_key=os.getenv("OPEN_ROUTER_API_KEY_2"),
        temperature=0.5,
    )

    return chat_llm