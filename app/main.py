# In main.py
import asyncio
from app.models.password_reset_token import PasswordResetToken
from app.db.mysql_connection import engine
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.init_db import init_db
from dotenv import load_dotenv
from app.routers.auth import auth_router
from app.routers.profiles import profile_router
from app.routers.projects import project_router
from app.routers.agents import agent_router
from sqlmodel import Session, select, or_
from datetime import datetime
from app.db.mongo import create_mongo_client
from fastapi.middleware.cors import CORSMiddleware
from app.routers.invitations import invitation_router
from app.routers.teams import teams_router
from app.routers.planned_projects import planned_projects_router
from app.tasks.background_tasks import delete_old_invitations
import os

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URL")
MONGODB_NAME = os.getenv("MONGODB_DB_NAME")

async def cleanup_used_otps():
    """Background worker that runs every 15 minutes to cleanup used OTPs"""
    while True:
        await asyncio.sleep(900)  # 15 minutes

        with Session(engine) as session:
            # Fixed: Use or_() for SQLModel OR conditions
            tokens = session.exec(
                select(PasswordResetToken).where(
                    or_(
                        PasswordResetToken.is_used == True,
                        PasswordResetToken.expires_at < datetime.utcnow()
                    )
                )
            ).all()

            for token in tokens:
                session.delete(token)

            session.commit()
            print(f"🧹 Cleaned up {len(tokens)} expired/used OTPs")
            
        
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Creates tables on startup

    mongo_client = create_mongo_client(MONGO_URI)
    app.state.mongo_client = mongo_client
    app.state.db = mongo_client[MONGODB_NAME]

    print("MONGODB CONNECTION ESTABLISHED")
    
    # Start background cleanup tasks
    cleanup_task = asyncio.create_task(cleanup_used_otps())
    invitation_cleanup_task = asyncio.create_task(delete_old_invitations(interval_seconds=86400, limit_days=7)) # Run daily, delete older than 7 days

    yield
    # Cancel on shutdown
    cleanup_task.cancel()
    invitation_cleanup_task.cancel()
    mongo_client.close() # Close MongoDB connection

app = FastAPI(lifespan=lifespan)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(project_router)
app.include_router(agent_router)
app.include_router(invitation_router)
app.include_router(teams_router)
app.include_router(planned_projects_router)