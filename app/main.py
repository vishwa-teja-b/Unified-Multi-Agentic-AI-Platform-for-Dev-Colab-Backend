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
    
    # Start background cleanup task
    cleanup_task = asyncio.create_task(cleanup_used_otps())

    yield
    # Cancel on shutdown
    cleanup_task.cancel()
    mongo_client.close() # Close MongoDB connection

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(project_router)
app.include_router(agent_router)