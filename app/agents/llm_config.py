from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def get_chat_llm():

    chat_llm = ChatOpenAI(
        model=os.getenv("MODEL_1"),
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPEN_ROUTER_API_KEY_1"),
        temperature=0.5,
    )

    return chat_llm