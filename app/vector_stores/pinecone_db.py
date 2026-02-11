from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
import os
from pinecone import Pinecone,ServerlessSpec
from dotenv import load_dotenv
from langchain_core.documents import Document
from fastapi import Depends

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

def get_pinecone_instance():
    pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    return pc

def get_pinecone_index():
    """
    Get or create a Pinecone index
    """
    pc = get_pinecone_instance()

    index_name = PINECONE_INDEX_NAME

    if not pc.has_index(index_name):
        pc.create_index(
            name = index_name,
            dimension = 384,
            metric = "cosine",
            spec = ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    index = pc.Index(index_name)

    return index

def get_embedding_model():
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embedding_model

def get_pinecone_vector_store():
    index = get_pinecone_index()
    embedding_model = get_embedding_model()

    return PineconeVectorStore(
        index = index,
        embedding = embedding_model
    )

def index_profile(profile: dict):
    """
    Convert profile's skills to a document and store in pinecone
    """
    try:
        skills_text = " ".join(profile.get("primary_skills", []))
        skills_text += " " + " ".join(profile.get("secondary_skills", []))
        skills_text += " " + profile.get("bio", "")
        skills_text += " " + profile.get("experience_level", "")

        doc = Document(page_content=skills_text, metadata={
            "name": profile.get("name", ""),
            "username": profile.get("username"),
            "availability_hours": profile.get("availability_hours"),
            "email": profile.get("email"),
            "timezone": profile.get("timezone", "UTC")
        })

        vector_store = get_pinecone_vector_store()
        vector_store.add_documents(documents=[doc], ids=[str(profile.get("auth_user_id"))])

        print(f"✅ Profile indexed: {profile.get('username')}")
        return {"success": True, "message": "Profile indexed successfully"}

    except Exception as e:
        print(f"❌ Error indexing profile: {e}")
        return {"success": False, "error": str(e)}
