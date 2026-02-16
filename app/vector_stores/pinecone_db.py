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
PINECONE_PROJECTS_INDEX_NAME = os.getenv("PINECONE_PROJECTS_INDEX", "projects")


def get_pinecone_instance():
    pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    return pc

def get_pinecone_index():
    """
    Get or create the profiles Pinecone index
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


def get_projects_pinecone_index():
    """
    Get or create the projects Pinecone index
    """
    pc = get_pinecone_instance()

    index_name = PINECONE_PROJECTS_INDEX_NAME

    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
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


def get_projects_vector_store():
    """Vector store for project semantic search"""
    index = get_projects_pinecone_index()
    embedding_model = get_embedding_model()

    return PineconeVectorStore(
        index=index,
        embedding=embedding_model
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


# ==================== PROJECT INDEXING ====================

def index_project(project: dict):
    """
    Index a project's searchable content in Pinecone for semantic search.
    Embeds: title + description + skills + features + category
    """
    try:
        text_parts = [
            project.get("title", ""),
            project.get("description", ""),
            project.get("category", ""),
            " ".join(project.get("required_skills", [])),
            " ".join(project.get("features", [])),
        ]
        search_text = " ".join(part for part in text_parts if part)

        doc = Document(page_content=search_text, metadata={
            "title": project.get("title", ""),
            "category": project.get("category", ""),
            "complexity": project.get("complexity", ""),
            "status": project.get("status", ""),
        })

        vector_store = get_projects_vector_store()
        vector_store.add_documents(documents=[doc], ids=[str(project.get("id"))])

        print(f"✅ Project indexed: {project.get('title')}")
        return {"success": True, "message": "Project indexed successfully"}

    except Exception as e:
        print(f"❌ Error indexing project: {e}")
        return {"success": False, "error": str(e)}


def delete_project_index(project_id: str):
    """Remove a project from the Pinecone index on deletion."""
    try:
        index = get_projects_pinecone_index()
        index.delete(ids=[project_id])
        print(f"✅ Project removed from index: {project_id}")
    except Exception as e:
        print(f"❌ Error deleting project index: {e}")


def search_projects(query: str, k: int = 10) -> list[dict]:
    """
    Semantic search over indexed projects.
    Returns list of {"id": str, "score": float, "metadata": dict}
    """
    try:
        vector_store = get_projects_vector_store()
        results = vector_store.similarity_search_with_score(query, k=k)

        matches = []
        for doc, score in results:
            # LangChain Pinecone stores the vector ID in metadata
            # We need to extract the project_id we used as the document ID
            matches.append({
                "score": float(score),
                "metadata": doc.metadata,
            })

        return matches

    except Exception as e:
        print(f"❌ Error searching projects: {e}")
        return []