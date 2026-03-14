from sqlmodel import SQLModel
from app.db.mysql_connection import engine

# Import all models so SQLModel registers them
from app.models.User import User
from app.models.password_reset_token import PasswordResetToken
import logging

logger = logging.getLogger(__name__)


def init_db():
    """Create all tables in the database"""
    SQLModel.metadata.create_all(engine)
    logger.info("MySQL connection established")
    logger.info("Database tables created: User, PasswordResetToken")


if __name__ == "__main__":
    init_db()
