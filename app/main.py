# In main.py
import asyncio
from app.models.password_reset_token import PasswordResetToken
from app.db.mysql_connection import engine
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.init_db import init_db
from dotenv import load_dotenv
from app.routers.auth import router
from sqlmodel import Session, select, or_
from datetime import datetime

load_dotenv()

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
    # Start background cleanup task
    cleanup_task = asyncio.create_task(cleanup_used_otps())
    yield
    # Cancel on shutdown
    cleanup_task.cancel()

app = FastAPI(lifespan=lifespan)

app.include_router(router)
